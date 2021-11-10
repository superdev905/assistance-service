
from typing import List, Optional
from fastapi import APIRouter
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from app.database.main import get_database
from .model import Attachment
from .schema import AttachmentItem

router = APIRouter(prefix="/attachments", tags=["Archivos adjuntos"])


@router.get("", response_model=List[AttachmentItem])
def get_all(employee_id: Optional[int] = None,
            db: Session = Depends(get_database)):
    """
    Retorna la lista de archivos adjuntos
    ---
    - **employee_id**: Id de trabajador
    """

    filters = []

    if not employee_id:
        filters.append(Attachment.data_id == employee_id)
        filters.append(Attachment.source_system == "TRABAJADORES")

    return db.query(Attachment).filter(*filters).all()
