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
from .services import generate_visits_excel, generate_visits_by_company_excel, generate_visits_by_assigned_excel, generate_assistance_by_employee_excel, generate_assistance_by_company_excel
from ..visit.model import Visit
from ..assistance.model import Assistance
from .schema import ReportVisitDateRange

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(JWTBearer())])


@router.get("/visits",)
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

@router.get("/visit-by-company",)
def generate_visit_by_company_report(req: Request, business_id: int, db: Session = Depends(get_database)):
    
    result = [v.__dict__ for v in db.query(Visit).filter(Visit.business_id == business_id).all()]

    company_name = result[0]["business_name"]
    file_name = f"Visitas_Empresa_{company_name}"
    headers = {
        'Content-Disposition': f"attachment; filename={file_name}.xlsx"
    }

    buffer_export = generate_visits_by_company_excel(req, result, company_name)
    return StreamingResponse(buffer_export, headers=headers)

@router.get("/visit-by-assigned",)
def generate_visit_by_assigned_report(req: Request, assigned_id: int, db: Session = Depends(get_database)):
    
    result = [v.__dict__ for v in db.query(Visit).filter(Visit.assigned_id == assigned_id).all()]

    file_name = f"Visitas_Profesional_id{assigned_id}"
    headers = {
        'Content-Disposition': f"attachment; filename={file_name}.xlsx"
    }

    buffer_export = generate_visits_by_assigned_excel(req, result)
    return StreamingResponse(buffer_export, headers=headers)


@router.get("/assistance-employee",)
def generate_assistance_by_employee_report(req: Request, employee_id: int, db: Session = Depends(get_database)):
    
    result = [a.__dict__ for a in db.query(Assistance).filter(Assistance.employee_id == employee_id).all()]

    rut_employee = result[0]["employee_rut"]
    file_name = f"Visitas_Trabajador_{rut_employee}"
    headers = {
        'Content-Disposition': f"attachment; filename={file_name}.xlsx"
    }

    buffer_export = generate_assistance_by_employee_excel(req, result, rut_employee)

    return StreamingResponse(buffer_export, headers=headers)

@router.get("/assistance-company",)
def generate_assistance_by_company_report(req: Request, business_id: int, db: Session = Depends(get_database)):
    
    result = [a.__dict__ for a in db.query(Assistance).filter(Assistance.business_id == business_id).all()]

    company_name = result[0]["business_name"]
    file_name = f"Visitas_Empresa_{company_name}"
    headers = {
        'Content-Disposition': f"attachment; filename={file_name}.xlsx"
    }

    buffer_export = generate_assistance_by_company_excel(req, result, company_name)

    return StreamingResponse(buffer_export, headers=headers)
