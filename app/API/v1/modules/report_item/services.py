from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm.session import Session
from .model import VisitReportItem


def seed_items(db: Session, user_id: int) -> None:
    items = [
        {
            "name": "Charlas",
            "description": "",
        },
        {
            "name": "Afiches",
            "description": "",
        },
        {
            "name": "Difusión",
            "description": "",
        },
        {
            "name": "Entradas",
            "description": "",
        },
        {
            "name": "Otros",
            "description": "",
        },
        {
            "name": "Otros",
            "description": "",

        }
    ]

    for item in items:
        obj_item = jsonable_encoder(item)
        obj_item["created_by"] = user_id
        obj_item["is_active"] = True

        db_item = VisitReportItem(**obj_item)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
