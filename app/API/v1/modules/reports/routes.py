from datetime import datetime
from typing import List
from fastapi import status, APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from starlette.responses import StreamingResponse
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from app.database.main import get_database
from ...middlewares.auth import JWTBearer
from ...helpers.crud import get_updated_obj
from .services import generate_visits_excel

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(JWTBearer())])


@router.post("/visits",)
def generate_visit_report(req: Request, db: Session = Depends(get_database)):
    """
    Genera los reportes para visitas
    """

    file_name = "Visitas"
    headers = {
        'Content-Disposition': "attachment; filename=" + file_name + ".xlsx"
    }

    buffer_export = generate_visits_excel(
        req, [], datetime.now(), datetime.now())

    return StreamingResponse(buffer_export, headers=headers)
