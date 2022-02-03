from datetime import datetime
from typing import List
from xmlrpc.client import Boolean, boolean
from fastapi import status, APIRouter, Request, Query
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException 
from starlette.responses import StreamingResponse
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from sqlalchemy.sql.elements import and_
from app.database.main import get_database
from ...middlewares.auth import JWTBearer
from ...helpers.crud import get_updated_obj
from .services import generate_visits_excel, generate_visits_by_company_excel, generate_visits_by_assigned_excel, generate_assistance_by_employee_excel, generate_assistance_by_company_excel
from ..visit.model import Visit
from ..assistance.model import Assistance
from .schema import ReportVisitDateRange, ReportVisitsbyCompany, ReportVisitsbyAssigned, ReportAssistancebyEmployee, ReportAssistancebyCompany

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(JWTBearer())])

def exists(resultQuery):
    return Boolean(resultQuery)


@router.post("/visits",)
def generate_visit_report(req: Request, range: ReportVisitDateRange, db: Session = Depends(get_database)):
    
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
        
    if(exists(result)):
        file_name = "Visitas"
        headers = {
            'Content-Disposition': "attachment; filename=" + file_name + ".xlsx"
        }
        buffer_export = generate_visits_excel(req, result, start, end)
        return StreamingResponse(buffer_export, headers=headers)
    else:
        return 'Sin Registros'

@router.post("/visit-by-company",)
def generate_visit_by_company_report(req: Request, schema: ReportVisitsbyCompany, db: Session = Depends(get_database)):

    result = None
    id_ = None
    start_ = None
    end_ = None

    if(schema.business_id):
        id_ = int(schema.business_id)
    if(schema.startDate):
        start_ = datetime.fromisoformat(schema.startDate.replace('Z', '+00:00'))
    if(schema.endDate):
        end_ = datetime.fromisoformat(schema.endDate.replace('Z', '+00:00'))


    if(start_ == None and end_ == None):
        result = [v.__dict__ for v in db.query(Visit).filter(Visit.business_id == id_).all()]

    elif(start_ and end_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.date.between(start_, end_), Visit.business_id == id_)).all()]

    elif (end_ == None and start_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.business_id == id_, Visit.date >= start_)).all()]

    elif (start_ == None and end_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.business_id == id_, Visit.date <= end_)).all()]

    if(exists(result)):
        company_name = result[0]["business_name"]
        file_name = f"Visitas_Empresa_{company_name}"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }
        buffer_export = generate_visits_by_company_excel(req, result, company_name, start_, end_)
        return StreamingResponse(buffer_export, headers=headers)
    else:
        return 'Sin Registros'

@router.post("/visit-by-assigned",)
def generate_visit_by_assigned_report(req: Request, schema: ReportVisitsbyAssigned, db: Session = Depends(get_database)):

    result = None
    id_ = None
    start_ = None
    end_ = None

    if(schema.assigned_id):
        id_ = int(schema.assigned_id)
    if(schema.startDate):
        start_ = datetime.fromisoformat(schema.startDate.replace('Z', '+00:00'))
    if(schema.endDate):
        end_ = datetime.fromisoformat(schema.endDate.replace('Z', '+00:00'))
    
    if(start_ == None and end_ == None):
        result = [v.__dict__ for v in db.query(Visit).filter(Visit.assigned_id == id_).all()]

    elif(start_ and end_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.date.between(start_, end_), Visit.assigned_id == id_)).all()]

    elif (end_ == None and start_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.assigned_id == id_, Visit.date >= start_)).all()]

    elif (start_ == None and end_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.assigned_id == id_, Visit.date <= end_)).all()]

    if(exists(result)):
        file_name = f"Visitas_Profesional_id{id_}"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }
        buffer_export = generate_visits_by_assigned_excel(req, result, start_, end_)
        return StreamingResponse(buffer_export, headers=headers)
    else:
        return 'Sin Registros'

@router.post("/assistance-employee",)
def generate_assistance_by_employee_report(req: Request, schema: ReportAssistancebyEmployee, db: Session = Depends(get_database)):
    
    result = None
    id_ = None
    start_ = None
    end_ = None

    if(schema.employee_id):
        id_ = int(schema.employee_id)
    if(schema.startDate):
        start_ = datetime.fromisoformat(schema.startDate.replace('Z', '+00:00'))
    if(schema.endDate):
        end_ = datetime.fromisoformat(schema.endDate.replace('Z', '+00:00'))
    
    if(start_ == None and end_ == None):
        result = [v.__dict__ for v in db.query(Assistance).filter(Assistance.employee_id == id_).all()]

    elif(start_ and end_):
        result = [v.__dict__ for v in db.query(Assistance).filter(and_(Assistance.date.between(start_, end_), Assistance.employee_id == id_)).all()]

    elif (end_ == None and start_):
        result = [v.__dict__ for v in db.query(Assistance).filter(and_(Assistance.employee_id == id_, Assistance.date >= start_)).all()]

    elif (start_ == None and end_):
        result = [v.__dict__ for v in db.query(Assistance).filter(and_(Assistance.employee_id == id_, Assistance.date <= end_)).all()]

    
    if(exists(result)):
        rut_employee = result[0]["employee_rut"]
        file_name = f"Visitas_Trabajador_{rut_employee}"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }

        buffer_export = generate_assistance_by_employee_excel(req, result, rut_employee, start_, end_)

        return StreamingResponse(buffer_export, headers=headers)
    else:
        return 'Sin Registros'

@router.post("/assistance-company",)
def generate_assistance_by_company_report(req: Request, schema: ReportAssistancebyCompany, db: Session = Depends(get_database)):
    
    
    result = None
    id_ = None
    start_ = None
    end_ = None

    if(schema.business_id):
        id_ = int(schema.business_id)
    if(schema.startDate):
        start_ = datetime.fromisoformat(schema.startDate.replace('Z', '+00:00'))
    if(schema.endDate):
        end_ = datetime.fromisoformat(schema.endDate.replace('Z', '+00:00'))
    
    if(start_ == None and end_ == None):
        result = [v.__dict__ for v in db.query(Assistance).filter(Assistance.business_id == id_).all()]

    elif(start_ and end_):
        result = [v.__dict__ for v in db.query(Assistance).filter(and_(Assistance.date.between(start_, end_), Assistance.business_id == id_)).all()]

    elif (end_ == None and start_):
        result = [v.__dict__ for v in db.query(Assistance).filter(and_(Assistance.business_id == id_, Assistance.date >= start_)).all()]

    elif (start_ == None and end_):
        result = [v.__dict__ for v in db.query(Assistance).filter(and_(Assistance.business_id == id_, Assistance.date <= end_)).all()]
    
    
    if(exists(result)):
        company_name = result[0]["business_name"]
        file_name = f"Visitas_Empresa_{company_name}"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }
        buffer_export = generate_assistance_by_company_excel(req, result, company_name, start_, end_)

        return StreamingResponse(buffer_export, headers=headers)
    else:
        return 'Sin Registros'