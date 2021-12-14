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
from .model import Assistance
from .schema import AssistanceCreate, AssistanceDetails, AssistancePatchSchema


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

    items = [{"name": "SALUD", "short": "S"},
             {"name": "VIVIENDA", "short": "V"},
             {"name": "PREVISIÓN", "short": "P"},
             {"name": "FAMILIA", "short": "F"},
             {"name": "EDUCACION", "short": "E"},
             {"name": "LEGAL", "short": "L"},
             {"name": "DEUDA/AHORRO", "short": "D"},
             {"name": "BENEFICIO EMPRESA", "short": "B"},
             {"name": "FUNDACION RECONOCER", "short": "FR"},
             {"name": "PROYECTO SOCIAL", "short": "PS"},
             {"name": "INCORPORACION", "short": "IN"}]

    result_list = []

    group_by_employee = db.query(Assistance.employee_id.label("employee_id"),
                                 Assistance.employee_rut.label("run"),
                                 Assistance.employee_name.label("names"),
                                 Assistance.employee_lastname.label(
                                     "lastname"),
                                 func.count(Assistance.employee_id).label("times")).filter(Assistance.visit_id == visit_id).group_by(
        Assistance.employee_id, Assistance.employee_name, Assistance.employee_lastname, Assistance.employee_rut).all()

    for employee in group_by_employee:
        emp = {}
        list = []
        for i in items:

            total_by_item = db.query(Assistance).filter(and_(
                Assistance.employee_id == employee.employee_id, Assistance.area_name.ilike(i[
                    "name"]),
                Assistance.visit_id == visit_id)).all()
            list.append({**i, "total": len(total_by_item)})
            emp[i["short"]] = len(total_by_item)

        result_list.append({"employee_id": employee.employee_id, "employee_run": employee.run,
                           "employee_fullname": employee.names + " " + employee.lastname, **emp, "tag": "A"})

    return {"items": result_list}


@router.get("/search")
def get_one(req: Request,
            visit_id: int,
            employee_rut: str = None,
            db: Session = Depends(get_database)):
    formatted_search = '{}%'.format(employee_rut)
    employees = db.query(Assistance.employee_id.label("employee_id")).filter(and_(
        Assistance.visit_id == visit_id, Assistance.employee_rut.ilike(formatted_search))).group_by(Assistance.employee_id).all()

    result = []
    r = fetch_service(req.token,
                      SERVICES["employees"]+"/employees?search=" + employee_rut + "&state=CREATED")
    if len(employees) == 0:
        for item in r:
            result.append({**item, "tag": "N", "is_old": False})

    else:
        for item in r:
            temp_item = {**item}
            for emp in employees:
                if item["id"] == int(emp.employee_id):
                    temp_item["tag"] = "A"
                    temp_item["is_old"] = True
                else:
                    temp_item["tag"] = "N"
                    temp_item["is_old"] = False
            result.append(temp_item)
    return result


@router.get("/attended")
def get_attended_list(visit_id: int = None,
                      id_employee: int = None,
                      social_case_id: int = Query(None, alias="socialCaseId"),
                      db: Session = Depends(get_database)):
    filters = []
    if visit_id:
        filters.append(Assistance.visit_id == visit_id)
    if id_employee:
        filters.append(Assistance.employee_id == id_employee)
    if social_case_id:
        filters.append(Assistance.case_id == social_case_id)
    list = db.query(Assistance).filter(
        and_(*filters)).order_by(Assistance.created_at.desc()).all()
    return list


@router.get("/business")
def get_attended_list(business_id: int = None,
                      db: Session = Depends(get_database),
                      params: PaginationParams = Depends()):
    filters = []
    filters.append(Assistance.business_id == business_id)
    query = db.query(Assistance).filter(
        and_(*filters)).order_by(Assistance.created_at.desc()).options(joinedload(Assistance.visit))
    return paginate(query, params)


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

    return {**found_event.__dict__,
            "management": management,
            "topic": topic,
            "area": area,
            "business": business,
            "construction": construction,
            }


@router.post("")
def create_one(obj_in: AssistanceCreate, db: Session = Depends(get_database)):
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
    return found_event


@ router.delete("/{id}")
def delete_one(id: int,  db: Session = Depends(get_database)):
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
    return {"message": "Asistencia eliminada"}
