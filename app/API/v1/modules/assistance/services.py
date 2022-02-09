

from sqlalchemy.sql.expression import and_
from sqlalchemy.orm.session import Session
from .model import Assistance
from app.settings import SERVICES
from ...helpers.fetch_data import handle_request


def get_attention_tracking_by_employee(req, db: Session, employee_id: int):
    attentions = db.query(Assistance).filter(and_(
        Assistance.status == "SEGUIMIENTO", Assistance.employee_id == employee_id)).first()

    last_attention = db.query(Assistance).filter(
        Assistance.employee_id == employee_id).order_by(Assistance.created_at.desc()).first()

    handle_request(req.token, SERVICES["employees"] +
                   "/employees/"+str(employee_id),
                   {
                       "hast_follow_attentions": bool(attentions),
        "last_attention_date": last_attention.date.isoformat()},
        "PATCH",)


def search_employees(req, employee_rut: str):
    return handle_request(req.token, SERVICES["employees"] + "/employees/?search=" +
                          employee_rut + "&state=CREATED&page=1&size=50", None, "GET")
