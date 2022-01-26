from typing import List
from fastapi import status, APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from app.database.main import get_database
from ...middlewares.auth import JWTBearer
from ...helpers.crud import get_updated_obj
from .model import VisitReportItem
from .schema import ReportCategoryCreate, ReportCategoryItem
from .services import seed_report_items

router = APIRouter(
    prefix="/visits-report-items",
    tags=["Items en reporte de visita"],
    dependencies=[Depends(JWTBearer())])


@router.get("", response_model=List[ReportCategoryItem])
def get_all(db: Session = Depends(get_database)):
    """
    Obtiene los items que se muestran en la tabla de reporte
    """
    return db.query(VisitReportItem).filter(VisitReportItem.is_active == True).all()


@router.post("", response_model=ReportCategoryItem)
def create(request: Request, body:  ReportCategoryCreate, db: Session = Depends(get_database)):
    """
    Crea un nuevo item
    ---
    - **name**: Nombre
    - **description**: Descripción item
    """
    obj_item = jsonable_encoder(body)
    obj_item["created_by"] = request.user_id
    obj_item["is_active"] = True
    db_item = VisitReportItem(**obj_item)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


@router.put("/{id}", response_model=ReportCategoryItem)
def update_one(id: int, body:  ReportCategoryCreate, db: Session = Depends(get_database)):
    """
    Actualiza el item
    ---
    - **id**: id del item
    - **name**: Nombre
    - **description**: Descripción item
    """
    found_item = db.query(VisitReportItem).filter(
        VisitReportItem.id == id).first()

    if not found_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No existe una categoría con este id: %s" % format(id))

    if not found_item.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No existe una categoría con este id: %s" % format(id))

    updated_item = get_updated_obj(found_item, body)

    db.add(updated_item)
    db.commit()
    db.refresh(updated_item)

    return updated_item


@router.delete("/{id}")
def delete_one(id: int, db: Session = Depends(get_database)):
    """
    Elimina un item
    ---
    - **id**: id del item
    """
    found_item = db.query(VisitReportItem).filter(
        VisitReportItem.id == id).first()

    if not found_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No existe una categoría con este id: %s" % format(id))

    if not found_item.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No existe una categoría con este id: %s" % format(id))

    found_item.is_active = False

    db.add(found_item)
    db.commit()
    db.refresh(found_item)

    return {"message": "Item eliminado"}


@router.post("/seed")
def seed_items(request: Request, db: Session = Depends(get_database)):
    """
    Registra items
    ---
    """
    seed_report_items(db, request.user_id)

    return {"message": "Datos creados"}
