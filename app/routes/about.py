from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["About & Docs"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/system-design/view")
def system_design(request: Request):
    return templates.TemplateResponse(
        "about.html",      # keep filename short
        {"request": request}
    )

@router.get("/data-deletion")
def data_deletion(request: Request):
    return templates.TemplateResponse(
        "data_deletion.html",
        {"request": request}
    )
