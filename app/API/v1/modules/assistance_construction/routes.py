from operator import and_, or_
from typing import Optional
from fastapi.param_functions import Depends
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from app.database.main import SessionLocal, get_database
from ...middlewares.auth import JWTBearer
from .model import AssistanceConstruction
from .schema import AssistanceConstructionSchema, AssistanceConstructionCreate, AssistanceConstructionAficheCharlaFolleto


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

@router.post("/get-folleto-charla-afiche")
def get_all_data(visitIdList: AssistanceConstructionAficheCharlaFolleto, db: SessionLocal = Depends(get_database)):
    """
    Retorna la lista de Folletos, Charlas y afiches realizados en las visitas.
    visitIdList: Arreglo de id de visitas para obtener data.
    """
    folleto = []
    totalFolleto = 0
    afiche = []
    totalAfiche = 0
    charla = []
    totalCharla = 0
    allData = db.query(AssistanceConstruction).filter(and_(AssistanceConstruction.visit_id.in_((visitIdList.id)), or_(AssistanceConstruction.type_name.ilike('FOLLETOS%'), or_(AssistanceConstruction.type_name.ilike('CHARLA%'), AssistanceConstruction.type_name.ilike('AFICHES%')))))

    for obj in allData:
        if "AFICHE" in obj.type_name:
            afiche.append({"type": obj.type_name, "quantity": obj.quantity, "visit_id": obj.visit_id})
            totalAfiche = totalAfiche + obj.quantity
        if "FOLLETO" in obj.type_name:
            folleto.append({"type": obj.type_name, "quantity": obj.quantity, "visit_id": obj.visit_id})
            totalFolleto = totalFolleto + obj.quantity
        if "CHARLA" in obj.type_name:
            charla.append({"type": obj.type_name, "quantity": obj.quantity, "visit_id": obj.visit_id})
            totalCharla = totalCharla + obj.quantity

    return {"folleto": folleto, "totalFolleto": totalFolleto, "afiche": afiche, "totalAfiche": totalAfiche, "charla": charla, "totalCharla": totalCharla,}
