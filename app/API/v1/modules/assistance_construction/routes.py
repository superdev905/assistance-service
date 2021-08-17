from fastapi_crudrouter import SQLAlchemyCRUDRouter
from app.database.main import SessionLocal, get_database
from .model import AssistanceConstruction
from .schema import AssistanceConstructionSchema, AssistanceConstructionCreate


router = SQLAlchemyCRUDRouter(
    schema=AssistanceConstructionSchema,
    create_schema=AssistanceConstructionCreate,
    db_model=AssistanceConstruction,
    db=get_database,
    prefix="assistance-construction",
    tags=["Asistencia en obra"],
    delete_all_route=False
)
