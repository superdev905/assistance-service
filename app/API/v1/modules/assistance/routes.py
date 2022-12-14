from typing import Optional
from fastapi import status, APIRouter, Request, Query
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.functions import func
from fastapi_pagination import PaginationParams
from fastapi_pagination.ext.sqlalchemy import paginate
from app.settings import SERVICES
from app.database.main import get_database
from ...helpers.fetch_data import fetch_parameter_data, fetch_service
from ...middlewares.auth import JWTBearer
from ..attachment.services import save_attachment
from .services import get_attention_tracking_by_employee, search_employees
from .model import Assistance
from .schema import AssistanceCreate, AssistanceDetails, AssistancePatchSchema, AssistanceReport


router = APIRouter(prefix="/assistance",
                   tags=["Asistencias"],
                   dependencies=[Depends(JWTBearer())])


@router.get("")
def get_all(visit_id: Optional[int] = None,
            db: Session = Depends(get_database)):
    """
    Retorna la lista de asistencias por cada usuario
    ---
    Parametros:

    - **visit_id**: Id de visita
    """

    result_list = []

    group_by_employee = db.query(Assistance.employee_id.label("employee_id"),
                                 Assistance.employee_rut.label("run"),
                                 Assistance.employee_name.label("names"),
                                 Assistance.employee_lastname.label(
                                     "lastname"),
                                 Assistance.area_name.label('area'),
                                 Assistance.construction_id.label('obraId'),
                                 Assistance.created_at.label('created_at'),
                                 func.count(Assistance.employee_id).label("times")).filter(Assistance.visit_id == visit_id).group_by(
        Assistance.employee_id, Assistance.employee_name, Assistance.employee_lastname, Assistance.employee_rut, Assistance.area_name, Assistance.construction_id, Assistance.created_at).all()

    result_list.append(group_by_employee)

    db.close()
    return result_list

@router.get("/report")
def get_all(visit_id: Optional[int] = None,
            db: Session = Depends(get_database)):
    """
    Retorna la lista de asistencias por cada usuario para el reporte
    ---
    Parametros:

    - **visit_id**: Id de visita
    """

    result_list = []

    listado_atenciones = db.query(Assistance).filter(Assistance.visit_id == visit_id).all()

    result_list.append(listado_atenciones)

    db.close()
    return result_list


@router.get("/search")
def get_one(req: Request,
            visit_id: int,
            employee_rut: str = None,
            db: Session = Depends(get_database)):
    formatted_search = '{}%'.format(employee_rut)
    employees = db.query(Assistance.employee_id.label("employee_id")).filter(and_(
        Assistance.visit_id == visit_id, Assistance.employee_rut.ilike(formatted_search))).group_by(Assistance.employee_id).all()

    result = []
    fetched_employees = search_employees(req, employee_rut)
    if len(employees) == 0:
        for item in fetched_employees["items"]:
            result.append({**item, "tag": "N", "is_old": False})
    else:
        for item in fetched_employees["items"]:
            temp_item = {**item}
            for emp in employees:
                if item["id"] == int(emp.employee_id):
                    temp_item["tag"] = "A"
                    temp_item["is_old"] = True
                else:
                    temp_item["tag"] = "N"
                    temp_item["is_old"] = False
            result.append(temp_item)
    db.close()
    return result


@router.get("/attended")
def get_attended_list(visit_id: int = None,
                      id_employee: int = None,
                      status: str = None,
                      social_case_id: int = Query(None, alias="socialCaseId"),
                      db: Session = Depends(get_database)):
    filters = []
    if visit_id:
        filters.append(Assistance.visit_id == visit_id)
    if id_employee:
        filters.append(Assistance.employee_id == id_employee)
    if status:
        filters.append(Assistance.status.like(status))
    if social_case_id:
        filters.append(Assistance.case_id == social_case_id)
    list = db.query(Assistance).filter(
        and_(*filters)).order_by(Assistance.created_at.desc()).all()

    db.close()
    return list


@router.get("/business")
def get_attended_list(business_id: int = None,
                      db: Session = Depends(get_database),
                      params: PaginationParams = Depends()):
    filters = []
    filters.append(Assistance.business_id == business_id)
    query = db.query(Assistance).filter(
        and_(*filters)).order_by(Assistance.created_at.desc()).options(joinedload(Assistance.visit))
    db.close()
    return paginate(query, params)

@router.get("/business-construction")
def get_attended_list(business_id: int = None,
                      construction_id: int = None,
                      db: Session = Depends(get_database),
                      params: PaginationParams = Depends()):
    filters = []
    filters.append(and_(Assistance.business_id == business_id, Assistance.construction_id == construction_id))
    query = db.query(Assistance).filter(
        and_(*filters)).order_by(Assistance.created_at.desc()).options(joinedload(Assistance.visit))
    db.close()
    return paginate(query, params)

@router.get("/business-history")
def get_attended_list(business_id: int = None,
                      construction_id: int = None,
                      visit_id: int = None,
                      db: Session = Depends(get_database)):
    filters = []
    filters.append(and_(Assistance.business_id == business_id, Assistance.construction_id == construction_id, Assistance.visit_id != visit_id))
    query = db.query(Assistance.employee_id.label('employee_id'),
                     Assistance.employee_name.label('employee_name'),
                     Assistance.employee_lastname.label('employee_lastname'),
                     Assistance.employee_rut.label('employee_rut')).filter(
        and_(*filters)).group_by(Assistance.employee_id, Assistance.employee_name, Assistance.employee_lastname, Assistance.employee_rut).all()
    result = query
    db.close()
    return jsonable_encoder(result)


@router.get("/{id}", response_model=AssistanceDetails)
def get_one(req: Request, id: int, db: Session = Depends(get_database)):
    """
    Optiene los detalles de una asistencia
    ---
    - **id**: id de asistencia
    """
    found_event = db.query(Assistance).filter(Assistance.id == id).first()

    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Esta asistencia no existe")
    management = fetch_parameter_data(req.token,
                                      "management",
                                      str(found_event.management_id))

    business = fetch_service(
        req.token, SERVICES["business"]+"/business/"+str(found_event.business_id)) if found_event.business_id else None

    construction = fetch_service(
        req.token, SERVICES["business"]+"/constructions/"+str(found_event.construction_id)) if found_event.construction_id else None

    topic = fetch_parameter_data(req.token,
                                 "topics",
                                 str(found_event.topic_id))
    area = fetch_parameter_data(req.token,
                                "areas",
                                found_event.area_id)

    db.close()
    return {**found_event.__dict__,
            "management": management,
            "topic": topic,
            "area": area,
            "business": business,
            "construction": construction,
            }


@router.post("")
def create_one(req: Request, obj_in: AssistanceCreate, db: Session = Depends(get_database)):
    """
    Crea una nueva asistencia
    """
    new_assistance = jsonable_encoder(obj_in)
    del new_assistance["attachments"]
    saved_assistance = Assistance(**new_assistance)

    db.add(saved_assistance)
    db.commit()
    db.refresh(saved_assistance)

    for attach in obj_in.attachments:
        save_attachment(db, attach, obj_in.created_by, saved_assistance.id)

    get_attention_tracking_by_employee(req, db, obj_in.employee_id)

    db.close()
    return {**saved_assistance.__dict__,
            "id": saved_assistance.id}


@ router.put("/{id}")
def update_one(id: int,
               update_body: AssistanceCreate,
               db: Session = Depends(get_database)):
    """
    Actualiza un asistencia
    - **id**: id de la asistencia

    """
    found_event = db.query(Assistance).filter(
        Assistance.id == id).first()
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Esta asistencia no existe")

    obj_data = jsonable_encoder(found_event)

    if isinstance(update_body, dict):
        update_data = update_body
    else:
        update_data = update_body.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(found_event, field, update_data[field])

    db.add(found_event)
    db.commit()
    db.refresh(found_event)
    db.close()
    return found_event


@ router.patch("/{id}")
def patch_one(id: int,
              patch_body: AssistancePatchSchema,
              db: Session = Depends(get_database)):
    """
    Actualiza campos de una asistencia
    - **id**: id de la asistencia

    """
    found_event = db.query(Assistance).filter(
        Assistance.id == id).first()
    if not found_event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Esta asistencia no existe")

    obj_data = jsonable_encoder(found_event)

    if isinstance(patch_body, dict):
        update_data = patch_body
    else:
        update_data = patch_body.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(found_event, field, update_data[field])

    db.add(found_event)
    db.commit()
    db.refresh(found_event)
    db.close()
    return found_event


@ router.delete("/{id}")
def delete_one(req: Request,  id: int,  db: Session = Depends(get_database)):
    """
    Elimina una asistencia

    - **id**: id de la asistencia

    """
    event = db.query(Assistance).filter(
        Assistance.id == id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Esta asistencia no existe")

    db.delete(event)
    db.commit()

    get_attention_tracking_by_employee(req, db, event.employee_id)

    db.close()
    return {"message": "Asistencia eliminada"}

@router.post("/get-assistance-report")
def get_assistance(body: AssistanceReport, db: Session = Depends(get_database)):
    """
    Obtiene listado de asistencia para reporte
    """

    terreno = [
        {"name": "ATENCION GRUPAL", "total": 0, "area_id": 11},
        {"name": "ATENCI??N INDIVIDUAL", "total": 0, "area_id": 10},
        {"name": "BENEFICIOS DE EMPRESA", "total": 0, "area_id": 8},
        {"name": "DEUDA / AHORRO", "total": 0, "area_id": 7},
        {"name": "EDUCACI??N", "total": 0, "area_id": 6},
        {"name": "FAMILIA", "total": 0, "area_id": 5},
        {"name": "FINIQUITADO", "total": 0, "area_id": 13},
        {"name": "FUNDACION RECONOCER", "total": 0, "area_id": 9},
        {"name": "INCORPORACION", "total": 0, "area_id": 14},
        {"name": "LEGAL", "total": 0, "area_id": 4},
        {"name": "PREVISI??N", "total": 0, "area_id": 1},
        {"name": "PROYECTOS SOCIALES", "total": 0, "area_id": 12},
        {"name": "SALUD", "total": 0, "area_id": 2},
        {"name": "VIVIENDA", "total": 0, "area_id": 3},
    ]
    topic_id_terreno = []
    management_id_terreno = []
    oficina = [
        {"name": "ATENCION GRUPAL", "total": 0, "area_id": 11},
        {"name": "ATENCI??N INDIVIDUAL", "total": 0, "area_id": 10},
        {"name": "BENEFICIOS DE EMPRESA", "total": 0, "area_id": 8},
        {"name": "DEUDA / AHORRO", "total": 0, "area_id": 7},
        {"name": "EDUCACI??N", "total": 0, "area_id": 6},
        {"name": "FAMILIA", "total": 0, "area_id": 5},
        {"name": "FINIQUITADO", "total": 0, "area_id": 13},
        {"name": "FUNDACION RECONOCER", "total": 0, "area_id": 9},
        {"name": "INCORPORACION", "total": 0, "area_id": 14},
        {"name": "LEGAL", "total": 0, "area_id": 4},
        {"name": "PREVISI??N", "total": 0, "area_id": 1},
        {"name": "PROYECTOS SOCIALES", "total": 0, "area_id": 12},
        {"name": "SALUD", "total": 0, "area_id": 2},
        {"name": "VIVIENDA", "total": 0, "area_id": 3},
    ]
    topic_id_oficina = []
    management_id_oficina = []
    assistances_company = []
    personas_visitas = []

    assistances = db.query(Assistance).filter(Assistance.visit_id.in_((body.visit_id))).all()
    assistances_company_report = db.query(Assistance).filter(and_(Assistance.visit_id.in_((body.visit_id)), Assistance.company_report == 'SI'))

    total_consultas = len(assistances)

    for company_report in assistances_company_report:
        assistances_company.append(company_report)

    for obj in assistances:
        personas_visitas.append({"visit_id": obj.visit_id, "persona": obj.employee_id})
        if obj.attention_place == 'TERRENO':
            topic_id_terreno.append(obj.topic_id)
            management_id_terreno.append(obj.management_id)
            for area_terreno in terreno:
                if area_terreno["name"] == obj.area_name:
                    area_terreno["total"] = area_terreno["total"] + 1
        else:
            topic_id_oficina.append(obj.topic_id)
            management_id_oficina.append(obj.management_id)
            for area_oficina in oficina:
                if area_oficina["name"] == obj.area_name:
                    area_oficina["total"] = area_oficina["total"] +1

    return {
        "terreno": terreno,
        "topic_ids_terreno": topic_id_terreno,
        "management_id_terreno": management_id_terreno, 
        "oficina": oficina, 
        "topic_ids_oficina": topic_id_oficina, 
        "management_id_oficina": management_id_oficina,
        "companyReport": assistances_company,
        "total_consultas": total_consultas,
        "personas_visitas": personas_visitas
        }