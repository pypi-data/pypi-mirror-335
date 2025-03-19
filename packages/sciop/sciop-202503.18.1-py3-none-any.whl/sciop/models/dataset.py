import hashlib
import re
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, Optional, Self, Union

from annotated_types import MaxLen
from pydantic import TypeAdapter, computed_field, field_validator, model_validator
from sqlalchemy import event
from sqlalchemy.orm.attributes import AttributeEventToken
from sqlalchemy.schema import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel
from sqlmodel.main import FieldInfo

from sciop.const import DATASET_PART_RESERVED_SLUGS, DATASET_RESERVED_SLUGS, PREFIX_LEN
from sciop.models.account import Account
from sciop.models.mixin import ModerableMixin, SearchableMixin, TableMixin, TableReadMixin
from sciop.models.tag import DatasetTagLink
from sciop.services.markdown import render_db_fields_to_html
from sciop.types import (
    AccessType,
    EscapedStr,
    ExternalIdentifierType,
    IDField,
    InputType,
    MaxLenURL,
    PathLike,
    Scarcity,
    ScrapeStatus,
    SlugStr,
    SourceType,
    Threat,
    UsernameStr,
)

if TYPE_CHECKING:
    from sciop.models import AuditLog, Tag, Upload, UploadRead

PREFIX_PATTERN = re.compile(r"\w{6}-[A-Z]{3}_\S+")


def _add_prefix(val: str, timestamp: datetime, key: str) -> str:
    # underscores can only get in slugs through prefix events
    if "__" in val:
        return val
    hasher = hashlib.blake2b(digest_size=3)
    hasher.update(timestamp.isoformat().encode("utf-8"))
    hash = hasher.hexdigest()
    return f"{hash}-{key.upper()}__{val}"


def _remove_prefix(val: str) -> str:
    if "__" in val:
        return val.split("__")[1]
    else:
        return val


def _prefixed_len(info: FieldInfo) -> int:
    max_len = [md for md in info.metadata if isinstance(md, MaxLen)][0]
    return max_len.max_length + PREFIX_LEN


class DatasetBase(ModerableMixin):
    title: str = Field(
        title="Title",
        description="""
    Human readable name for dataset. 
    Match the title given by the source as closely as possible.
    """,
        min_length=3,
        max_length=512,
    )
    slug: SlugStr = Field(
        title="Dataset Slug",
        description="""
    Short, computer readable identifier for dataset.
    The acronym or abbreviation of the dataset name, e.g. for the NOAA
    "Fundamental Climate Data Record - Mean Layer Temperature NOAA"
    use "fcdr-mlt-noaa". Converted to a slugified string.
    """,
        min_length=2,
        max_length=128,
    )
    publisher: str = Field(
        title="Publisher",
        description="""
    The agency, organization, author, group, publisher, etc. that is associated with the dataset.
    Please use a canonical acronym/abbreviation form of the name when possible,
    using the autocompleted values if any correct matches are listed.
    """,
        max_length=256,
        schema_extra={"json_schema_extra": {"autocomplete": "publisher"}},
    )
    homepage: Optional[MaxLenURL] = Field(
        None,
        title="Homepage",
        description="""
    The index/landing page that describes this dataset, if any. 
    If the dataset has multiple associated URLs, if e.g. an index page with metadata
    is different from the download URL, add ths index here and additional URLs below.
    """,
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="""
    Additional information about the dataset. Markdown input is supported.
    """,
        schema_extra={"json_schema_extra": {"input_type": InputType.textarea}},
        max_length=16384,
    )
    description_html: Optional[str] = Field(
        default="",
        schema_extra={"json_schema_extra": {"input_type": InputType.none}},
        max_length=32768,
    )
    dataset_created_at: Optional[datetime] = Field(
        None,
        title="Dataset Creation Date",
        description="""
        Datetime when dataset was originally created in UTC. May be approximate or left blank.
        """,
    )
    dataset_updated_at: Optional[datetime] = Field(
        None,
        title="Dataset Last Updated",
        description="""
        Datetime when the dataset was last updated in UTC. May be approximate or left blank
        """,
    )
    source_type: SourceType = Field(
        "unknown",
        title="Source Type",
        description="""
    The protocol/technology needed to download the dataset.
    Use "web" if the dataset is an archive of websites themselves,
    and "http" if the dataset is some other raw data available via http download.
    """,
    )
    source_available: bool = Field(
        default=True,
        title="Source Available",
        description="""
        Whether the canonical source of this dataset is still available.
        Default true unless known to be taken down.
        """,
    )
    last_seen_at: Optional[datetime] = Field(
        default=None,
        title="Last Seen At",
        description="""
        If the dataset has been removed, the last time it was known to be available. 
        If the dataset is scheduled to be removed, 
        the time in the future where it is expected to be unavailable. 
        Otherwise, leave blank.
        Times should be in UTC.
        """,
    )
    source_access: AccessType = Field(
        default="unknown",
        title="Source Access",
        description="""
    How the canonical source can be accessed, whether it needs credentials
    or is intended to be public.
    """,
    )
    scarcity: Scarcity = Field(
        default="unknown",
        title="Scarcity",
        description="""
    To prioritize scrapes, an estimate of the rarity of this dataset.
    Datasets that are likely to only exist in one or a few places are prioritized over
    those that are widely available.
    """,
    )
    threat: Threat = Field(
        default="unknown",
        title="Threat",
        description="""
    To prioritize scrapes, an estimate of how likely this dataset is likely to disappear
    in the immediate future. Datasets that are under direct threat due to the their nature
    or specific threats made against them are prioritized over those 
    for whom no specific threat exists.
    """,
    )


class Dataset(DatasetBase, TableMixin, SearchableMixin, table=True):
    __tablename__ = "datasets"
    __searchable__ = ["title", "slug", "publisher", "homepage", "description"]

    slug: SlugStr = Field(
        unique=True,
        index=True,
        min_length=2,
        max_length=_prefixed_len(DatasetBase.model_fields["slug"]),
    )
    dataset_id: IDField = Field(None, primary_key=True)
    uploads: list["Upload"] = Relationship(back_populates="dataset")
    external_sources: list["ExternalSource"] = Relationship(back_populates="dataset")
    external_identifiers: list["ExternalIdentifier"] = Relationship(back_populates="dataset")
    urls: list["DatasetURL"] = Relationship(back_populates="dataset")
    tags: list["Tag"] = Relationship(
        back_populates="datasets",
        sa_relationship_kwargs={"lazy": "selectin"},
        link_model=DatasetTagLink,
    )
    account_id: Optional[int] = Field(default=None, foreign_key="accounts.account_id")
    account: Optional["Account"] = Relationship(back_populates="datasets")
    scrape_status: ScrapeStatus = "unknown"
    audit_log_target: list["AuditLog"] = Relationship(back_populates="target_dataset")
    parts: list["DatasetPart"] = Relationship(back_populates="dataset")


event.listen(Dataset, "before_update", render_db_fields_to_html("description"))
event.listen(Dataset, "before_insert", render_db_fields_to_html("description"))


@event.listens_for(Dataset.is_removed, "set")
def _datset_prefix_on_removal(
    target: Dataset, value: bool, oldvalue: bool, initiator: AttributeEventToken
) -> None:
    """Add or remove a prefix when removal state is toggled"""
    if value:
        # add prefix
        target.slug = _add_prefix(target.slug, target.created_at, "REM")
    else:
        target.slug = _remove_prefix(target.slug)


class DatasetCreate(DatasetBase):
    urls: list[MaxLenURL] = Field(
        default_factory=list,
        title="URL(s)",
        description="""
        URL(s) to the direct download of the data, if public, 
        or any additional URLs associated with the dataset.
        One URL per line.
        If uploading a recursive web archive dump, only the top-level URL is needed.
        """,
        schema_extra={"json_schema_extra": {"input_type": InputType.textarea}},
        max_length=512,
    )
    tags: list[Annotated[SlugStr, Field(min_length=2, max_length=32)]] = Field(
        title="Tags",
        description="""
        Tags for this dataset. Use matching autocomplete values, when available.
        Enter as comma separated list or press enter to store a token.
        Only lowercase alphanumeric characters and `-` are allowed.
        Include as many tags as are applicable: topic, data type/file type,
        if this dataset is part of a collection (e.g. each dataset in NOAA's
        Fundamental Climate Data Records should be tagged with `fcdr`), etc.
        Tags are used to generate RSS feeds so people can reseed data that is important to them.
        """,
        schema_extra={"json_schema_extra": {"input_type": InputType.tokens}},
        min_length=1,
        max_length=512,
    )
    external_identifiers: list["ExternalIdentifierCreate"] = Field(
        title="External Identifiers",
        default_factory=list,
        schema_extra={
            "json_schema_extra": {
                "input_type": InputType.model_list,
                "model_name": "ExternalIdentifierCreate",
            }
        },
        max_length=32,
    )
    parts: list["DatasetPartCreate"] = Field(
        default_factory=list,
        title="Part(s)",
        schema_extra={"json_schema_extra": {"input_type": InputType.none}},
    )

    @field_validator("urls", "tags", mode="before")
    def split_lines(cls, value: str | list[str]) -> Optional[list[str]]:
        """Split lists of strings given as one entry per line"""
        return _split_lines(value)

    @field_validator("tags", "tags", mode="before")
    def split_commas(cls, value: str | list[str]) -> Optional[list[str]]:
        """Split lists of strings given as one entry per line"""
        if isinstance(value, str):
            if not value or value == "":
                return None
            value = value.split(",")
        elif value is None:
            return None

        # split any substrings, e.g. if comma-separated strings are used in
        # the token-input style of tag entry
        split_val = []
        for v in value:
            split_subvals = v.split(",")
            split_subvals = [subv.strip() for subv in split_subvals]
            split_val.extend(split_subvals)
        value = split_val

        # filter empty strings
        value = [v for v in value if v.strip()]

        # if left with an empty list, None
        if value:
            return value
        else:
            return None

    @field_validator("*", mode="before")
    def empty_strings_are_none(cls, value: Any) -> Any:
        """Forms sometimes submit input without anything as empty strings not None"""
        if value == "":
            value = None
        return value

    @field_validator("slug", mode="after")
    def not_reserved_slug(cls, slug: str) -> str:
        assert slug not in DATASET_RESERVED_SLUGS, f"slug {slug} is reserved"
        return slug


class DatasetRead(DatasetBase, TableReadMixin):
    slug: SlugStr = Field(min_length=2, max_length=_prefixed_len(DatasetBase.model_fields["slug"]))
    uploads: list["UploadRead"] = Field(default_factory=list)
    external_sources: list["ExternalSource"] = Field(default_factory=list)
    external_identifiers: list["ExternalIdentifierRead"] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    scrape_status: ScrapeStatus
    is_approved: bool

    @field_validator("tags", mode="before")
    def collapse_tags(cls, val: list["Tag"]) -> list[str]:
        return [tag.tag for tag in val]

    @field_validator("urls", mode="before")
    def collapse_urls(cls, val: list["DatasetURL"]) -> list[str]:
        return [url.url for url in val]

    @field_validator("tags", mode="after")
    def sort_list(cls, val: list[Any]) -> list[Any]:
        return sorted(val)


class DatasetURL(SQLModel, table=True):
    __tablename__ = "dataset_urls"

    dataset_url_id: IDField = Field(default=None, primary_key=True)
    dataset_id: Optional[int] = Field(default=None, foreign_key="datasets.dataset_id")
    dataset: Optional[Dataset] = Relationship(back_populates="urls")

    url: MaxLenURL


class ExternalSourceBase(SQLModel):
    """An external source for this dataset"""

    source: EscapedStr = Field(
        description="The name of the group or person who provides the dataset",
        max_length=256,
    )
    url: MaxLenURL = Field(description="Link to the external source", max_length=512)
    description: str = Field(
        description="Additional information about the completeness, accuracy, etc. "
        "of the external source",
        max_length=4096,
    )


class ExternalSource(ExternalSourceBase, TableMixin, table=True):
    __tablename__ = "external_sources"

    external_source_id: IDField = Field(None, primary_key=True)
    dataset_id: Optional[int] = Field(default=None, foreign_key="datasets.dataset_id")
    dataset: Dataset = Relationship(back_populates="external_sources")
    account_id: Optional[int] = Field(default=None, foreign_key="accounts.account_id")
    account: Optional[Account] = Relationship(back_populates="external_submissions")


class ExternalIdentifierBase(SQLModel):
    """
    Some additional, probably persistent identifier for a dataset
    """

    type: ExternalIdentifierType
    identifier: str = Field(min_length=1, max_length=512)

    @property
    def uri(self) -> str:
        if self.type in ("ark"):
            return f"{self.type}:{self.identifier}"
        elif self.type == "cid":
            return f"https://dweb.link/ipfs/{self.identifier}"
        elif self.type == "doi":
            return f"https://doi.org/{self.identifier}"
        elif self.type == "isni":
            return f"https://isni.org/isni/{self.identifier}"
        elif self.type == "issn":
            return f"https://urn.issn.org/urn:issn:{self.identifier}"
        elif self.type == "isbn":
            return f"urn:{self.type}:{self.identifier}"
        elif self.type in ("purl", "urn", "uri"):
            return self.identifier


class ExternalIdentifier(ExternalIdentifierBase, TableMixin, table=True):
    __tablename__ = "external_identifiers"

    external_identifier_id: IDField = Field(None, primary_key=True)
    dataset_id: Optional[int] = Field(default=None, foreign_key="datasets.dataset_id")
    dataset: Dataset = Relationship(back_populates="external_identifiers")


class ExternalIdentifierCreate(ExternalIdentifierBase):

    @field_validator("identifier", mode="before")
    def strip_whitespace(cls, val: str) -> str:
        return val.strip()

    @model_validator(mode="after")
    def validate_by_type(self) -> Self:
        """
        Apply additional validation from the annotation on the external identifier type
        """
        annotation = ExternalIdentifierType.__annotations__.get(self.type, None)
        if annotation is None:
            return self

        adapter = TypeAdapter(annotation)
        self.identifier = adapter.validate_python(self.identifier)
        return self


class ExternalIdentifierRead(ExternalIdentifierBase):
    pass


class UploadDatasetPartLink(SQLModel, table=True):
    __tablename__ = "upload_dataset_part_links"
    dataset_part_id: Optional[int] = Field(
        default=None, foreign_key="dataset_parts.dataset_part_id", primary_key=True
    )
    upload_id: Optional[int] = Field(
        default=None, foreign_key="uploads.upload_id", primary_key=True
    )


class DatasetPartBase(SQLModel):
    part_slug: SlugStr = Field(
        title="Part Slug",
        description="Unique identifier for this dataset part",
        min_length=1,
        max_length=256,
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Additional information about this part. Markdown input is supported.",
        max_length=4096,
    )
    description_html: Optional[str] = Field(
        "",
        schema_extra={"json_schema_extra": {"input_type": InputType.none}},
        max_length=8192,
    )


class DatasetPart(DatasetPartBase, TableMixin, ModerableMixin, table=True):
    __tablename__ = "dataset_parts"
    __table_args__ = (UniqueConstraint("dataset_id", "part_slug", name="_dataset_part_slug_uc"),)

    part_slug: SlugStr = Field(
        index=True,
        min_length=1,
        max_length=_prefixed_len(DatasetPartBase.model_fields["part_slug"]),
    )
    dataset_part_id: IDField = Field(None, primary_key=True)
    dataset_id: Optional[int] = Field(None, foreign_key="datasets.dataset_id")
    dataset: Optional[Dataset] = Relationship(back_populates="parts")
    account_id: Optional[int] = Field(None, foreign_key="accounts.account_id")
    account: Optional[Account] = Relationship(back_populates="dataset_parts")
    uploads: list["Upload"] = Relationship(
        back_populates="dataset_parts", link_model=UploadDatasetPartLink
    )
    paths: list["DatasetPath"] = Relationship(back_populates="dataset_part")
    audit_log_target: list["AuditLog"] = Relationship(back_populates="target_dataset_part")


@event.listens_for(DatasetPart.is_removed, "set")
def _part_prefix_on_removal(
    target: DatasetPart, value: bool, oldvalue: bool, initiator: AttributeEventToken
) -> None:
    """Add or remove a prefix when removal state is toggled"""
    if value:
        # add prefix
        target.part_slug = _add_prefix(target.part_slug, target.created_at, "REM")
    else:
        target.part_slug = _remove_prefix(target.part_slug)


event.listen(DatasetPart, "before_update", render_db_fields_to_html("description"))
event.listen(DatasetPart, "before_insert", render_db_fields_to_html("description"))


class DatasetPartCreate(DatasetPartBase):
    paths: list[PathLike] = Field(
        default_factory=list,
        title="Paths",
        description="A list of paths that this part should contain, "
        "if the part is not a single file. One path per line.",
        max_length=2048,
        schema_extra={"json_schema_extra": {"input_type": InputType.textarea}},
    )

    @field_validator("paths", mode="before")
    def split_lines(cls, value: str | list[str]) -> Optional[list[str]]:
        return _split_lines(value)

    @field_validator("part_slug", mode="after")
    def not_reserved_slug(cls, slug: str) -> str:
        assert slug not in DATASET_PART_RESERVED_SLUGS, f"slug {slug} is reserved"
        return slug


class DatasetPartRead(DatasetPartBase):
    dataset: DatasetRead
    uploads: list["UploadRead"] = Field(default_factory=list)
    account: UsernameStr

    @computed_field
    def absolute_slug(self) -> str:
        """Slug joined by / with the parent dataset slug"""
        return "/".join([self.dataset.slug, self.part_slug])

    @field_validator("account", mode="before")
    def account_to_username(cls, account: Union["Account", str]) -> str:
        from sciop.models import Account

        if isinstance(account, Account):
            account = account.username
        return account


class DatasetPath(TableMixin, table=True):
    __tablename__ = "dataset_paths"

    dataset_path_id: IDField = Field(None, primary_key=True)
    dataset_part_id: Optional[int] = Field(None, foreign_key="dataset_parts.dataset_part_id")
    dataset_part: DatasetPart = Relationship(back_populates="paths")
    path: str = Field(max_length=1024)


def _split_lines(value: str | list[str]) -> Optional[list[str]]:
    if isinstance(value, str):
        if not value or value == "":
            return []
        value = value.splitlines()
    elif isinstance(value, list) and len(value) == 1:
        if "\n" in value[0]:
            value = value[0].splitlines()
        elif value[0] == "":
            return []
    elif value is None:
        return []

    # filter empty strings
    value = [v for v in value if v and v.strip()]
    return value
