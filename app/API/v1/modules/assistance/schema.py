from datetime import datetime, time, timedelta
from typing import Optional
from pydantic import BaseModel


class ShiftCreate(BaseModel):
    type_id: int
    date: datetime
    start_date: datetime
    end_date: datetime
    shift_id: int
    shift_name: Optional[str]
    status: str
    assigned_id: int
    business_id: int
    business_name: Optional[str]
    construction_id: int
    construction_name: Optional[str]
    observation: str
    created_by: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "type_id": 1,
                "date": datetime.now(),
                "start_date": datetime.now() + timedelta(minutes=30),
                "end_date": datetime.now() + timedelta(minutes=30),
                "shift_id": 1,
                "shift_name": "MAÑANA",
                "status": "PROGRAMADA",
                "assigned_id":  1,
                "business_id": 1,
                "business_name": "",
                "construction_id": 1,
                "construction_name": "",
                "observation": "Comentarios simples",
                "created_by": 1
            }
        }


class ShiftSchema (ShiftCreate):
    id: int
