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
from app.database.main import get_database
from app.settings import SERVICES
from ..assistance.model import Assistance
from .model import Visit
from .schema import VisitSchema, VisitCreate, VisitPatchSchema, VisitReportSchema
from ...services.file import create_visit_report

router = APIRouter(prefix="/visits", tags=["Visitas"])


@router.get("/calendar")
def get_calendar_events(start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        status: Optional[str] = None,
                        user_id: Optional[int] = None,
                        db: Session = Depends(get_database)):
    """
    Optiene las asistencias y visitas para mostrar en el calendario

    - **start_date**: Fecha de inicio
    - **end_date**: Fecha de fin
    - **user_id**: Id de usuario responsable
    """
    filters = []

    if start_date and end_date:
        filters.append(Visit.start_date >= start_date)
        filters.append(Visit.end_date <= end_date)
    if status:
        filters.append(Visit.status == status)
    if user_id:
        filters.append(Visit.assigned_id == user_id)

    return db.query(Visit).filter(*filters).order_by(Visit.date).all()


@router.get("")
def get_all(user_id: Optional[int] = None,
            start_date: Optional[datetime] = None,
            search: Optional[str] = None,
            db: Session = Depends(get_database), params: PaginationParams = Depends()):
    """
    Retorna la lista de visitas
    ---
    Parametros:
    - **size**: Página de asistencias
    - **limit**: Número de registros por cada página asistencias
    - **user_id**: Id de usuario responsable
    - **start_date**: Fecha inicial para filtrar visitas
    - **search**: Parámetro a buscar 
    """
    filters = []
    search_filters = []
    if user_id:
        filters.append(Visit.assigned_id == user_id)
    if start_date:
        filters.append(func.DATE(Visit.start_date) >= start_date)
    if search:
        formatted_search = '%{}%'.format(search)
        search_filters.append(Visit.title.ilike(formatted_search))
        search_filters.append(Visit.business_name.ilike(formatted_search))
        search_filters.append(
            Visit.construction_name.ilike(formatted_search))
    return paginate(db.query(Visit).filter(and_(*filters, or_(*search_filters), Visit.status != "CANCELADA")).order_by(Visit.start_date), params)


@router.get("/{id}")
def get_one(id: int, db: Session = Depends(get_database)):
    """
    Optiene una visita
    ---
    - **id**: id de asistencia/visita
    """
    visit = db.query(Visit).filter(Visit.id == id).first()

    if not visit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No existe una visita con este" + id)

    r = requests.get(SERVICES["parameters"]+"/shift/"+str(visit.shift_id))

    return {**visit.__dict__, "shift": r.json()}


@router.get("/{id}/statistics")
def delete_one(id: int, db: Session = Depends(get_database)):
    """
    Obtiene las estadisticas de las 

    - **id**: visit_id de la asistencia

    """

    total = len(db.query(Assistance).filter(Assistance.visit_id == id).all())

    return {"total": total, "new": 0, "old": total}


@router.post("/{id}/report")
def create_report(id: int, report_in: VisitReportSchema, db: Session = Depends(get_database)):
    """
    Crea el reporte de la visita
    ---
    - **id**: id de asistencia/visita
    """
    visit = db.query(Visit).filter(Visit.id == id).first()

    if not visit:
        raise HTTPException(
            status_code=400, detail="Esta visita no existe")

    total_assistance = len(db.query(Assistance).filter(
        Assistance.visit_id == id).all())
    data = {"construction_name": visit.construction_name,
            "user": report_in.user,
            "correlative": str(visit.id),
            "user_email": report_in.user_email,
            "user_phone": report_in.user_phone,
            "relevant": report_in.relevant,
            "observations": report_in.observations,
            "total": str(total_assistance)}

    report_name = create_visit_report(data)

    visit.report_key = report_name
    visit.report_url = report_name

    db.add(visit)
    db.commit()
    db.refresh(visit)

    return {"msg": "Reporte creado"}


@ router.post("")
def create_one(obj_in: VisitCreate, db: Session = Depends(get_database)):
    """
    Crea una nueva asistencia

    """
    print(obj_in.start_date)
    saved_event = Visit(**jsonable_encoder(obj_in))

    db.add(saved_event)
    db.commit()
    db.refresh(saved_event)
    return saved_event


@ router.put("/{id}")
def update_one(id: int, update_body: VisitCreate, db: Session = Depends(get_database)):
    """
    Actualiza un evento
    - **id**: id del evento

    """
    found_event = db.query(Visit).filter(
        Visit.id == id).first()
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


@ router.patch("/{id}")
def patch_one(id: int, patch_body: VisitPatchSchema, db: Session = Depends(get_database)):
    """
    Actualiza campos de un evento
    - **id**: id del evento

    """
    found_event = db.query(Visit).filter(
        Visit.id == id).first()
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


@ router.delete("/{id}")
def delete_one(id: int,  db: Session = Depends(get_database)):
    """
    Elimina un evento

    - **id**: id del evento

    """
    event = db.query(Visit).filter(
        Visit.id == id).first()
    if not event:
        raise HTTPException(
            status_code=400, detail="Este evento no existe")

    db.delete(event)
    db.commit()
    return {"message": "Evento eliminado"}
