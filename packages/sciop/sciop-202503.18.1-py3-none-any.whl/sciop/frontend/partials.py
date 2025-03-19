"""Assorted partials that have no other base type"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from sciop import models
from sciop.frontend.templates import templates

partials_router = APIRouter(prefix="/partials")


@partials_router.get("/model-list", response_class=HTMLResponse)
def model_list(idx: int, field_name: str, model_name: str, form_id: str, request: Request):
    """
    Render a model that is nested within a form using the form-json syntax
    https://github.com/xehrad/form-json
    """
    if not hasattr(models, model_name):
        raise HTTPException(404, f"Model {model_name} not found")
    return templates.TemplateResponse(
        request,
        "partials/model-list.html",
        {
            "form_id": form_id,
            "idx": idx,
            "model_name": model_name,
            "model": getattr(models, model_name),
            "field_name": field_name,
            "field_name_prefix": f"{field_name}[{idx}].",
        },
    )
