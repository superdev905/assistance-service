from datetime import datetime
from typing import List
from fastapi import status, APIRouter, Request, Query
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from starlette.responses import StreamingResponse
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from app.database.main import get_database
from ...middlewares.auth import JWTBearer
from ...helpers.crud import get_updated_obj
from .services import generate_visits_excel
from ..visit.model import Visit
from .schema import ReportVisitDateRange

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(JWTBearer())])


@router.post("/visits",)
def generate_visit_report(req: Request, range: ReportVisitDateRange, db: Session = Depends(get_database)):
    """
    Genera los reportes para visitas
    """

    file_name = "Visitas"
    headers = {
        'Content-Disposition': "attachment; filename=" + file_name + ".xlsx"
    }

    result = None
    start = None
    end = None
    if(range.startDate):
        start = datetime.fromisoformat(range.startDate.replace('Z', '+00:00'))
    if(range.endDate):
        end = datetime.fromisoformat(range.endDate.replace('Z', '+00:00'))

    if(start == None and end == None):
        result = [v.__dict__ for v in db.query(Visit).all()]

    elif(start and end):
        result = [v.__dict__ for v in db.query(Visit).filter(Visit.date.between(start, end)).all()]
        
    elif (end == None):
        result = [v.__dict__ for v in db.query(Visit).filter(Visit.date >= start).all()]
        
    elif (start == None):
        result = [v.__dict__ for v in db.query(Visit).filter(Visit.date <= end).all()]
        


    buffer_export = generate_visits_excel(
        req, result, start, end)

    return StreamingResponse(buffer_export, headers=headers)
