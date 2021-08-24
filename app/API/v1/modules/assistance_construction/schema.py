from datetime import datetime
from pydantic import BaseModel


class AssistanceConstructionCreate(BaseModel):
    type_id: int
    type_name: str
    date: datetime
    quantity: int
    visit_id: int
    created_by: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "type_id": 1,
                "date": datetime.now(),
                "type_name": 'AFICHES: BECAS (BMA/BEXC)',
                "quantity": 5,
                "visit_id": 4,
                "created_by": 1
            }
        }


class AssistanceConstructionSchema (AssistanceConstructionCreate):
    id: int
