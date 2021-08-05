from typing import Optional
from fastapi import status, Request, APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from app.database.main import get_database
from .model import Assistance
from .schema import ShiftCreate, ShiftSchema


router = APIRouter(prefix="/assistance-visits", tags=["Asistencias y visitas"])


@router.get("", response_model=ShiftSchema)
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
def create_one(obj_in: ShiftCreate, db: Session = Depends(get_database)):
    """
    Crea una nueva asistencia

    """

    obj = jsonable_encoder(obj_in)
    return {}
