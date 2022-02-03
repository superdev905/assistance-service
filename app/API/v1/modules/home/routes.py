from datetime import datetime
from operator import and_
from typing import List
from fastapi import status, APIRouter, Request, Query
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from starlette.responses import StreamingResponse
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from app.database.main import get_database
from ...middlewares.auth import JWTBearer
from ...helpers.crud import get_updated_obj
from ...helpers.fetch_data import fetch_list_parameters, fetch_parameter_data, fetch_users_service
from ..visit.model import Visit
from ..assistance.model import Assistance
from .schema import AssistanceHome, DeliveredBenefit, VisitHome
from .services import get_delivered_benefit

router = APIRouter(
    prefix="/home",
    tags=["Home"],
    dependencies=[Depends(JWTBearer())])


@router.get("/visits", response_model=List[VisitHome])
def get_last_five_visits(req: Request,  db: Session = Depends(get_database)):
    """
    Retorna las 5 ultimas visitas pendientes
    """
    filters = []

    current_user = fetch_users_service(req.token, req.user_id)
    current_user_role = current_user["role"]["key"]

    if current_user_role == "SOCIAL_ASSISTANCE":
        filters.append(Visit.assigned_id == req.user_id)

    types = fetch_list_parameters(req.token, "task-type")
    visit_type_id = None
    for i in types:
        if i["description"] == "VISITA":
            visit_type_id = i['id']

    filters.append(Visit.status == "PROGRAMADA")
    filters.append(Visit.type_id == visit_type_id)

    docs = db.query(Visit).filter(and_(*filters)).order_by(
        Visit.start_date.desc()).limit(5).all()
    result = []
    for doc in docs:
        assigned = fetch_users_service(req.token, doc.assigned_id)
        result.append({**doc.__dict__, "assigned": assigned,
                      "type_name": "VISITA"})

    return result


@router.get("/attentions", response_model=List[AssistanceHome])
def get_last_five_visits(req: Request,  db: Session = Depends(get_database)):
    """
    Retorna las 5 ultimas atenciones
    """
    filters = []

    current_user = fetch_users_service(req.token, req.user_id)
    current_user_role = current_user["role"]["key"]

    managements = fetch_list_parameters(req.token, "management")

    if current_user_role == "SOCIAL_ASSISTANCE":
        filters.append(Assistance.assigned_id == req.user_id)

    docs = db.query(Assistance).filter(*filters).order_by(
        Assistance.date.desc()).limit(5).all()
    result = []
    for doc in docs:
        user = fetch_users_service(req.token, doc.assigned_id)
        management_name = ""
        for i in managements:
            if i["id"] == doc.management_id:
                management_name = i["name"]
        result.append({**doc.__dict__, "assistance": user,
                      "management_name": management_name})

    return result


@router.get("/delivered-benefits", response_model=List[DeliveredBenefit])
def get_last_five_visits(req: Request,  db: Session = Depends(get_database)):
    """
    Retorna las 5 ultimos beneficios entregados
    """
    filters = []
    result = []

    current_user = fetch_users_service(req.token, req.user_id)
    current_user_role = current_user["role"]["key"]

    managements = fetch_list_parameters(req.token, "management")

    if current_user_role == "SOCIAL_ASSISTANCE":
        filters.append(Assistance.assigned_id == req.user_id)

    management_delivered_id = None

    for i in managements:
        if i["name"] == "ENTREGA DE BENEFICIO":
            management_delivered_id = i["id"]

    filters.append(Assistance.management_id == management_delivered_id)

    docs = db.query(Assistance).filter(*filters).order_by(
        Assistance.date.desc()).limit(5).all()

    for i in docs:
        activity = get_delivered_benefit(req, i.id)
        user = fetch_users_service(req.token, i.assigned_id)
        result.append({**i.__dict__,
                       "assistance": user,
                      "activity": activity})

    return result
