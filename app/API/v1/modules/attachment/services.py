from sqlalchemy.orm.session import Session
from fastapi.encoders import jsonable_encoder
from .model import Attachment


def save_attachment(db: Session, obj: dict, user_id: int):
    obj_attachment = jsonable_encoder(obj, by_alias=False)
    obj_attachment["created_by"] = user_id
    new_attachment = Attachment(**obj_attachment)

    db.add(new_attachment)
    db.commit()
    db.refresh(new_attachment)
    return new_attachment
