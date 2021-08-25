import json
import requests
from datetime import datetime
from typing import Optional
from fastapi import status, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.sql.functions import func
from fastapi_pagination import PaginationParams
from fastapi_pagination.ext.sqlalchemy import paginate
from app.settings import EMPLOYEE_SERVICE
from app.database.main import get_database
from .model import Assistance
from .schema import AssistanceSchema, AssistanceCreate, AssistancePatchSchema


router = APIRouter(prefix="/assistance", tags=["Asistencias"])


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
def get_one(visit_id: int, employee_rut: str = None, db: Session = Depends(get_database)):
    formatted_search = '%{}%'.format(employee_rut)
    employees = db.query(Assistance.employee_id.label("employee_id")).filter(and_(
        Assistance.visit_id == visit_id, Assistance.employee_rut.ilike(formatted_search))).group_by(Assistance.employee_id).all()

    result = []
    params = {"search": employee_rut, "state": "CREATED"}
    r = requests.get(EMPLOYEE_SERVICE+"/api/v1/employees",
                     params=params)
    if len(employees) == 0:
        for item in r.json():
            result.append({**item, "tag": "N", "is_old": False})

    else:
        for item in r.json():
            temp_item = {**item}
            for emp in employees:
                print(item["id"] == int(emp.employee_id))
                if item["id"] == int(emp.employee_id):
                    temp_item["tag"] = "A"
                    temp_item["is_old"] = True
                else:
                    temp_item["tag"] = "N"
                    temp_item["is_old"] = False
            result.append(temp_item)
    return result


@router.get("/attended")
def get_attended_list(visit_id: int, id_employee: str = None, db: Session = Depends(get_database)):
    list = db.query(Assistance).filter(and_(
        Assistance.visit_id == visit_id, Assistance.employee_id == id_employee)).all()
    return list


@router.get("/{id}")
def get_one(id: int, db: Session = Depends(get_database)):
    """
    Optiene una asistencia
    ---
    - **id**: id de asistencia
    """

    return db.query(Assistance).filter(Assistance.id == id).first()


@router.post("")
def create_one(obj_in: AssistanceCreate, db: Session = Depends(get_database)):
    """
    Crea una nueva asistencia

    """
    saved_event = Assistance(**jsonable_encoder(obj_in))

    db.add(saved_event)
    db.commit()
    db.refresh(saved_event)
    return saved_event


@ router.put("/{id}")
def update_one(id: int, update_body: AssistanceCreate, db: Session = Depends(get_database)):
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
def patch_one(id: int, patch_body: AssistancePatchSchema, db: Session = Depends(get_database)):
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
