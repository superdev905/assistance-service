from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class VisitCreate(BaseModel):
    visit_id: int
    date: datetime
    relevant: str
    observations: str
    created_by: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "visit_id": 1,
                "type_id": 1,
                "date": datetime.now(),
                "relevant": "Casos relevantes",
                "observations": "Comentarios simples",
                "created_by": 1
            }
        }


class VisitSchema (VisitCreate):
    id: int
