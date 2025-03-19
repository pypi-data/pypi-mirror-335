import contextlib
import sys
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Self, get_origin

import sqlalchemy as sqla
from pydantic import ConfigDict
from sqlalchemy import CheckConstraint, Column, ColumnElement, Connection, Table, event
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlmodel import Field, Session, SQLModel, select, text

from sciop.types import IDField, InputType

if TYPE_CHECKING:
    from sqlalchemy import Connection, Table, TextClause
    from sqlalchemy.sql.expression import Select
    from sqlmodel.main import FieldInfo

    from sciop.models import Account


class TableMixin(SQLModel):
    """Mixin to add base elements to all tables"""

    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
    )

    model_config = ConfigDict(ignored_types=(hybrid_method, hybrid_property))

    @property
    def id(self) -> int:
        """
        The value of the primary key, `table_id` property.
        """
        for name, field in self.model_fields.items():
            try:
                if field.annotation is IDField or IDField in get_origin(field.annotation):
                    return getattr(self, name)
            except TypeError:
                continue
        raise AttributeError("No IDField found")


class TableReadMixin(SQLModel):
    """
    Mixin to add base elements to the read version of all tables
    """

    created_at: datetime
    updated_at: datetime


class SearchableMixin(SQLModel):
    """
    Mixin that makes a sqlmodel class full text searchable using external content tables
    https://sqlite.org/fts5.html#external_content_tables

    Inspired in part by:
    https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-full-text-search
    """

    __searchable__: list[str] = None
    """
    List of columns that should be added to the full text search table 
    """

    _fts_table: ClassVar[Table] = None

    @classmethod
    def primary_key_column(cls) -> str:
        """
        Name of the column that is the primary key, i.e. is an IDField
        (Assuming there is only one)
        """
        for name, field in cls.model_fields.items():
            field: FieldInfo
            if getattr(field, "primary_key", False) is True:
                return name
        raise ValueError("No primary key found")

    @classmethod
    def fts_table(cls) -> Table:
        """Virtual table for full text search"""
        if cls._fts_table is None:
            cols = [Column(colname) for colname in cls.__searchable__]
            cls._fts_table = Table(
                cls.__fts_table_name__(),
                cls.metadata,
                Column("rowid"),
                *cols,
            )
        return cls._fts_table

    @classmethod
    def __fts_table_name__(cls) -> str:
        return "__".join([cls.__tablename__, "search"])

    @classmethod
    def search(cls, query: str, session: Session) -> list[Self]:
        """
        Find model instances that match the provided query
        This convenience method should generally be avoided, as it returns all matches
        and its text statement makes it impossible/tricky to combine with other queries,
        but it is a bit more efficient than the `in` clause in the normal search_statement
        """

        text_stmt = text(
            f"SELECT rowid as {cls.primary_key_column()}, * FROM {cls.__fts_table_name__()} "  # noqa: S608 - confirmed no sqli
            f"WHERE {cls.__fts_table_name__()} MATCH :q ORDER BY rank;"
        ).bindparams(q=query)
        stmt = select(cls).from_statement(text_stmt)
        return session.exec(stmt).all()

    @classmethod
    def search_statement(cls, query: str) -> "Select":
        """
        Search query statement on the full text search table that selects
        only the row IDs, so that the full object can be retrieved in a subsequent query,
        probably as a subquery.

        Examples:

            .. code-block:: python

                query = select(Example
                    ).where(
                        Example.some_column == True
                    ).filter(
                        Example.id.in_(Example.search_statement(query))
                    )

        """
        table = cls.fts_table()
        if len(query) < 3:
            query = query + "*"
            where_clause = text(f"{cls.__fts_table_name__()} = :query").bindparams(query=query)
        else:
            where_clause = text(f"{cls.__fts_table_name__()} = :query").bindparams(query=query)

        return (
            select(table.c.rowid.label(cls.primary_key_column()))
            .where(where_clause)
            .order_by(text("rank"))
        )

    @classmethod
    def count_statement(cls, query: str) -> "TextClause":
        """Select statement to count number of search results"""
        return text(
            f"SELECT count(*) FROM {cls.__fts_table_name__()} WHERE {cls.__fts_table_name__()} MATCH :q;"  # noqa: S608 - confirmed no sqli
        ).bindparams(q=query)

    @classmethod
    def register_events(cls) -> None:
        """
        # FIXME: make this happen on class declaration with a decorator
        """
        event.listen(cls.__table__, "after_create", cls.after_create)

    @classmethod
    def after_create(cls, target: "Table", connection: "Connection", **kwargs: Any) -> None:
        """
        Create a matching full text search table with triggers to keep it updated

        Uses an external content table - https://sqlite.org/fts5.html#external_content_and_contentless_tables
        and the ``trigram`` tokenizer to support subtoken queries

        These are definitely string interpolations in sql text clauses,
        but none of the interpolated values are from user input, all are derived from the model class
        """
        if not cls.__searchable__:
            return

        table_name = cls.__fts_table_name__()
        col_names = ", ".join(cls.__searchable__)
        new_names = ", ".join(
            [f"new.{cname}" for cname in [cls.primary_key_column()] + cls.__searchable__]
        )
        old_names = ", ".join(
            [f"old.{cname}" for cname in [cls.primary_key_column()] + cls.__searchable__]
        )
        # ruff: noqa: E501
        create_stmt = text(
            f"""
            CREATE VIRTUAL TABLE {table_name} USING fts5({col_names}, content={target.name}, content_rowid={cls.primary_key_column()}, tokenize='trigram');
            """
        )
        trigger_insert = text(
            f"""  
            CREATE TRIGGER {target.name}_ai AFTER INSERT ON {target.name} BEGIN
              INSERT INTO {table_name}(rowid, {', '.join(cls.__searchable__)}) VALUES ({new_names});
            END;
            """  # noqa: S608 - confirmed no sqli
        )
        trigger_delete = text(
            f"""
            CREATE TRIGGER {target.name}_ad AFTER DELETE ON {target.name} BEGIN
              INSERT INTO {table_name}({table_name}, rowid, {col_names}) VALUES('delete', {old_names});
            END;
            """
        )
        trigger_update = text(
            f"""
            CREATE TRIGGER {target.name}_au AFTER UPDATE ON {target.name} BEGIN
              INSERT INTO {table_name}({table_name}, rowid, {col_names}) VALUES('delete', {old_names});
              INSERT INTO {table_name}(rowid, {col_names}) VALUES ({new_names});
            END;
            """  # noqa: S608 - confirmed no sqli
        )
        try:
            connection.execute(create_stmt)
        except OperationalError as e:
            if "already exists" not in str(e):
                raise e

        connection.execute(trigger_insert)
        connection.execute(trigger_delete)
        connection.execute(trigger_update)


class EnumTableMixin(SQLModel):
    """Enum table mixin for method for ensuring all enum values exist"""

    __enum_column_name__: ClassVar[str] = None
    """Column that has the enum values for which rows should be created"""

    @classmethod
    def enum_class(cls) -> StrEnum:
        """Get the enum itself used in the enum column"""
        return cls.model_fields[cls.__enum_column_name__].annotation

    @classmethod
    def ensure_enum_values(cls, session: Session) -> None:
        if cls.__enum_column_name__ is None:
            raise ValueError("__enum_column_name__ must be declared for EnumTableMixins")

        enum = cls.enum_class()
        for item in enum:
            stmt = select(cls).where(getattr(cls, cls.__enum_column_name__) == item.value)
            existing_enum_row = session.exec(stmt).first()
            if not existing_enum_row:
                db_item = cls(**{cls.__enum_column_name__: item.value})
                session.add(db_item)

        session.commit()

    @classmethod
    def get_item(cls, item: str | StrEnum, session: Session) -> Self:
        """Get the row corresponding to this enum item"""
        if isinstance(item, str) and sys.version_info < (3, 12):
            if item not in cls.enum_class().__members__:
                raise KeyError(f"No such item {item} exists in {cls.enum_class()}")
        elif item not in cls.enum_class():
            raise KeyError(f"No such item {item} exists in {cls.enum_class()}")

        return session.exec(
            select(cls).where(getattr(cls, cls.__enum_column_name__) == item)
        ).first()


class ListlikeMixin(SQLModel):
    """
    Mixin for models that are many-to-many joined to "primary" models,
    like tags, urls, etc. where the same tag or url is expected to be re-used many times
    """

    __value_column_name__: ClassVar[str] = None

    @classmethod
    def get_item(cls, value: str, session: Session) -> Self:
        """Get the row corresponding to the value of this item"""
        if cls.__value_column_name__ is None:
            raise ValueError("__value_column__ must be declared for ListlikeMixins")

        return session.exec(
            select(cls).where(getattr(cls, cls.__value_column_name__) == value)
        ).first()


class ModerableMixin(SQLModel):
    """
    Common columns/properties among moderable objects
    """

    is_approved: bool = Field(
        False,
        description="Whether this item has been reviewed and is now visible",
        schema_extra={"json_schema_extra": {"input_type": InputType.none}},
    )
    is_removed: bool = Field(
        False,
        description="Whether the item has been, for all practical purposes, deleted.",
        schema_extra={"json_schema_extra": {"input_type": InputType.none}},
    )

    model_config = ConfigDict(ignored_types=(hybrid_method, hybrid_property))

    # TODO: https://github.com/fastapi/sqlmodel/issues/299#issuecomment-2223569400
    @hybrid_property
    def is_visible(self) -> bool:
        """Whether the dataset should be displayed and included in feeds"""
        return self.is_approved and not self.is_removed

    @is_visible.inplace.expression
    @classmethod
    def _is_visible(cls) -> ColumnElement[bool]:
        return sqla.and_(cls.is_approved == True, cls.is_removed == False)

    @hybrid_property
    def needs_review(self) -> bool:
        """Whether a dataset needs to be reviewed"""
        return not self.is_approved and not self.is_removed

    @needs_review.inplace.expression
    @classmethod
    def _needs_review(cls) -> ColumnElement[bool]:
        return sqla.and_(cls.is_approved == False, cls.is_removed == False)

    @hybrid_method
    def visible_to(self, account: Optional["Account"] = None) -> bool:
        """Whether this item is visible to the given account"""
        if account is None:
            return self.is_visible
        if self.is_visible:
            return True
        elif self.is_removed:
            return False
        elif hasattr(self, "account") and self.account == account:
            return True
        else:
            return account.has_scope("review")

    @visible_to.inplace.expression
    @classmethod
    def _visible_to(cls, account: Optional["Account"] = None) -> ColumnElement[bool]:
        if account is None:
            return cls._is_visible

        if hasattr(cls, "account"):
            return sqla.and_(
                cls.is_removed == False,
                sqla.or_(
                    cls.is_visible == True,
                    account.has_scope("review") == True,
                    cls.account == account,
                ),
            )
        else:
            return sqla.and_(
                cls.is_removed == False,
                sqla.or_(cls.is_visible == True, account.has_scope("review") == True),
            )

    @hybrid_method
    def removable_by(self, account: Optional["Account"] = None) -> bool:
        if account is None:
            return False
        return self.account == account or account.has_scope("review")

    @removable_by.inplace.expression
    @classmethod
    def _removable_by(cls, account: Optional["Account"] = None) -> ColumnElement[bool]:
        if account is None:
            return sqla.false()
        return sqla.or_(cls.account == account, account.has_scope("review") == True)


class _FriedolinType(StrEnum):
    friedolin = "friedolin"


class _Friedolin(SQLModel, table=True):
    __tablename__ = "friedolin"
    friedolin: _FriedolinType = Field(
        "friedolin",
        primary_key=True,
        unique=True,
        sa_column_args=[
            CheckConstraint(text("friedolin = 'friedolin'"), name="the_friedolin_constraint")
        ],
    )


@event.listens_for(_Friedolin.__table__, "after_create")
def _make_friedolin(target: Table, connection: Connection, **kwargs: Any) -> None:
    with contextlib.suppress(Exception):
        # this can fail and we literally don't care
        connection.execute(target.insert().values(friedolin="friedolin"))
