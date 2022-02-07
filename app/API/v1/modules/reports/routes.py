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
from .schema import ReportVisitDateRange, ReportbyIdAndDateRange
from ...helpers.fetch_data import fetch_list_parameters


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
    visit_type_id = None
    if(range.startDate):
        start = datetime.fromisoformat(range.startDate.replace('Z', '+00:00'))
    if(range.endDate):
        end = datetime.fromisoformat(range.endDate.replace('Z', '+00:00'))

    types = fetch_list_parameters(req.token, "task-type")
    for i in types:
        if i["description"] == "VISITA":
            visit_type_id = i['id']

    if(start == None and end == None):
        result = [v.__dict__ for v in db.query(Visit).filter(Visit.type_id == visit_type_id).all()]

    elif(start and end):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.date.between(start, end), Visit.type_id == visit_type_id)).all()]
        
    elif (end == None):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.date >= start, Visit.type_id == visit_type_id)).all()]
        
    elif (start == None):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.date <= end, Visit.type_id == visit_type_id)).all()]
        
    file_name = "Visitas"
    headers = {
        'Content-Disposition': "attachment; filename=" + file_name + ".xlsx"
    }
    
    if(exists(result)):
        buffer_export = generate_visits_excel(req, result, start, end)
        return StreamingResponse(buffer_export, headers=headers)
    else:
        buffer_export = generate_visits_excel(req, [], start, end)
        return StreamingResponse(buffer_export, headers=headers)

@router.post("/visit-by-company",)
def generate_visit_by_company_report(req: Request, schema: ReportbyIdAndDateRange, db: Session = Depends(get_database)):

    result = None
    id_ = None
    start_ = None
    end_ = None
    visit_type_id = None

    if(schema.id):
        id_ = schema.id
    if(schema.startDate):
        start_ = datetime.fromisoformat(schema.startDate.replace('Z', '+00:00'))
    if(schema.endDate):
        end_ = datetime.fromisoformat(schema.endDate.replace('Z', '+00:00'))

    types = fetch_list_parameters(req.token, "task-type")
    for i in types:
        if i["description"] == "VISITA":
            visit_type_id = i['id']


    if(start_ == None and end_ == None):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.business_id == id_, Visit.type_id == visit_type_id)).all()]

    elif(start_ and end_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.date.between(start_, end_), Visit.business_id == id_, Visit.type_id == visit_type_id)).all()]

    elif (end_ == None and start_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.business_id == id_, Visit.date >= start_, Visit.type_id == visit_type_id)).all()]

    elif (start_ == None and end_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.business_id == id_, Visit.date <= end_, Visit.type_id == visit_type_id)).all()]

    
    
    if(exists(result)):
        company_name = result[0]["business_name"]
        file_name = f"Visitas_Empresa_{company_name}"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }
        buffer_export = generate_visits_by_company_excel(req, result, company_name, start_, end_)
        return StreamingResponse(buffer_export, headers=headers)
    else:
        file_name = f"Visitas_Empresa_SIN_REGISTROS"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }
        buffer_export = generate_visits_by_company_excel(req, [], 'SIN_REGISTROS', start_, end_)
        return StreamingResponse(buffer_export, headers=headers)

@router.post("/visit-by-assigned",)
def generate_visit_by_assigned_report(req: Request, schema: ReportbyIdAndDateRange, db: Session = Depends(get_database)):

    result = None
    id_ = None
    start_ = None
    end_ = None
    visit_type_id = None

    if(schema.id):
        id_ = schema.id
    if(schema.startDate):
        start_ = datetime.fromisoformat(schema.startDate.replace('Z', '+00:00'))
    if(schema.endDate):
        end_ = datetime.fromisoformat(schema.endDate.replace('Z', '+00:00'))

    types = fetch_list_parameters(req.token, "task-type")
    for i in types:
        if i["description"] == "VISITA":
            visit_type_id = i['id']
    
    if(start_ == None and end_ == None):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.assigned_id == id_, Visit.type_id == visit_type_id)).all()]

    elif(start_ and end_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.date.between(start_, end_), Visit.assigned_id == id_, Visit.type_id == visit_type_id)).all()]

    elif (end_ == None and start_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.assigned_id == id_, Visit.date >= start_, Visit.type_id == visit_type_id)).all()]

    elif (start_ == None and end_):
        result = [v.__dict__ for v in db.query(Visit).filter(and_(Visit.assigned_id == id_, Visit.date <= end_, Visit.type_id == visit_type_id)).all()]

    if(exists(result)):
        file_name = f"Visitas_Profesional_id{id_}"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }
        buffer_export = generate_visits_by_assigned_excel(req, result, start_, end_)
        return StreamingResponse(buffer_export, headers=headers)
    else:
        file_name = f"Visitas_Profesional_id_SIN_REGISTROS"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }
        buffer_export = generate_visits_by_assigned_excel(req, [], start_, end_)
        return StreamingResponse(buffer_export, headers=headers)

@router.post("/assistance-employee",)
def generate_assistance_by_employee_report(req: Request, schema: ReportbyIdAndDateRange, db: Session = Depends(get_database)):
    
    result = None
    id_ = None
    start_ = None
    end_ = None

    if(schema.id):
        id_ = schema.id
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
        file_name = f"Asistencias_Trabajador_{rut_employee}"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }

        buffer_export = generate_assistance_by_employee_excel(req, result, rut_employee, start_, end_)

        return StreamingResponse(buffer_export, headers=headers)
    else:
        rut_employee = 'SIN_REGISTROS'
        file_name = f"Asistencias_Trabajador_{rut_employee}"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }

        buffer_export = generate_assistance_by_employee_excel(req, [], rut_employee, start_, end_)

        return StreamingResponse(buffer_export, headers=headers)

@router.post("/assistance-company",)
def generate_assistance_by_company_report(req: Request, schema: ReportbyIdAndDateRange, db: Session = Depends(get_database)):
    
    
    result = None
    id_ = None
    start_ = None
    end_ = None

    if(schema.id):
        id_ = schema.id
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
        file_name = f"Asistencias_Empresa_{company_name}"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }
        buffer_export = generate_assistance_by_company_excel(req, result, company_name, start_, end_)

        return StreamingResponse(buffer_export, headers=headers)
    else:
        company_name = 'SIN_REGISTROS'
        file_name = f"Asistencias_Empresa_{company_name}"
        headers = {
            'Content-Disposition': f"attachment; filename={file_name}.xlsx"
        }
        buffer_export = generate_assistance_by_company_excel(req, [], company_name, start_, end_)

        return StreamingResponse(buffer_export, headers=headers)