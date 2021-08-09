from typing import Optional
from fastapi import status, Request, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from app.database.main import get_database
from .model import Assistance
from .schema import AssistanceSchema, AssistanceCreate, AssistancePatchSchema


router = APIRouter(prefix="/assistance-visits", tags=["Asistencias y visitas"])


@router.get("")
def get_all(skip: int = 0, limit: int = 25, status: Optional[str] = None, db: Session = Depends(get_database)):
    """
    Optiene las asistencias y visitas aplicando filtros

    - **skip**: página de asistencias
    - **limit**: limite de asistencias
    - **status**: estado de asistencia
    """

    filters = []
    if status:
        filters.append(Assistance.status == status)
    return db.query(Assistance).filter(*filters).offset(skip).limit(limit).all()


@router.post("")
def create_one(obj_in: AssistanceCreate, db: Session = Depends(get_database)):
    """
    Crea una nueva asistencia

    """
    print(obj_in.start_date)
    saved_event = Assistance(**jsonable_encoder(obj_in))

    db.add(saved_event)
    db.commit()
    db.refresh(saved_event)
    return saved_event


@router.put("/{id}")
def update_one(id: int, update_body: AssistanceCreate, db: Session = Depends(get_database)):
    """
    Actualiza un evento
    - **id**: id del evento

    """
    found_event = db.query(Assistance).filter(
        Assistance.id == id).first()
    if not found_event:
        raise HTTPException(
            status_code=400, detail="Este evento no existe")

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


@router.patch("/{id}")
def patch_one(id: int, patch_body: AssistancePatchSchema, db: Session = Depends(get_database)):
    """
    Actualiza campos de un evento
    - **id**: id del evento

    """
    found_event = db.query(Assistance).filter(
        Assistance.id == id).first()
    if not found_event:
        raise HTTPException(
            status_code=400, detail="Este evento no existe")

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


@router.delete("/{id}")
def delete_one(id: int,  db: Session = Depends(get_database)):
    """
    Elimina un evento

    - **id**: id del evento

    """
    event = db.query(Assistance).filter(
        Assistance.id == id).first()
    if not event:
        raise HTTPException(
            status_code=400, detail="Este evento no existe")

    db.delete(event)
    db.commit()
    return {"message": "Evento eliminado"}
