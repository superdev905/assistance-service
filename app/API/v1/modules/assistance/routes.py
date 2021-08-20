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
from app.database.main import get_database
from .model import Assistance
from .schema import AssistanceSchema, AssistanceCreate, AssistancePatchSchema


router = APIRouter(prefix="/assistance", tags=["Asistencias"])


@router.get("")
def get_all(visit_id: Optional[int] = None,

            db: Session = Depends(get_database), params: PaginationParams = Depends()):
    """
    Retorna la lista de asistencias
    ---
    Parametros:
    - **page**: Página de asistencias
    - **size**: Número de registros por cada página asistencias
    - **user_id**: Id de usuario responsable
    - **start_date**: Fecha inicial para filtrar visitas
    - **search**: Parámetro a buscar 
    """
    filters = []
    search_filters = []

    return paginate(db.query(Assistance).filter(and_(*filters, or_(*search_filters))).order_by(Assistance.created_at), params)


@router.get("/{id}")
def get_one(id: int, db: Session = Depends(get_database)):
    """
    Optiene una asistencia
    ---
    - **id**: id de asistencia
    """

    return db.query(Assistance).filter(Assistance.id == id).first()


@ router.post("")
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
