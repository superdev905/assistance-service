from datetime import datetime, timedelta
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.functions import func
from .model import Visit


def format_business_details(details: dict) -> dict:
    if not details:
        return None

    return {"address": details["address"],
            "latitude": details["latitude"],
            "longitude": details["longitude"],
            "business_name": details["business_name"],
            "rut": details["rut"],
            }


def format_construction_details(details: dict) -> dict:
    if not details:
        return None

    return {"address": details["address"],
            "latitude": details["latitude"],
            "longitude": details["longitude"],
            "name": details["name"],
            }


def get_blocked_status(visit: Visit) -> bool:
    current_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
    end_date = datetime.strftime(
        visit.end_date + timedelta(hours=48), '%Y-%m-%d')

    return current_date >= end_date


def block_visit(db: Session, visit: Visit) -> None:
    if get_blocked_status(visit):
        visit.is_active = False
        db.add(visit)
        db.commit()
        db.refresh(visit)
