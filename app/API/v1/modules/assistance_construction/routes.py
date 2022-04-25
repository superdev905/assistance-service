from typing import Optional
from fastapi.param_functions import Depends
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from app.database.main import SessionLocal, get_database
from ...middlewares.auth import JWTBearer
from .model import AssistanceConstruction
from .schema import AssistanceConstructionSchema, AssistanceConstructionCreate


router = SQLAlchemyCRUDRouter(
    schema=AssistanceConstructionSchema,
    create_schema=AssistanceConstructionCreate,
    db_model=AssistanceConstruction,
    db=get_database,
    prefix="assistance-construction",
    tags=["Asistencia en obra"],
    delete_all_route=False,
    dependencies=[Depends(JWTBearer())]
)


@router.get("")
def overloaded_get_all(skip: int = None,
                       limit: int = None,
                       visit_id: Optional[str] = None,
                       db: SessionLocal = Depends(get_database)):
    """
    Retorna la lista de assistencias en obra
    ---
    """
    filters = []
    if visit_id:
        filters.append(AssistanceConstruction.visit_id == visit_id)
    db.close()
    return db.query(AssistanceConstruction).filter(*filters).offset(skip).limit(limit).all()
