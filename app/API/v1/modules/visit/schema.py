from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field


class VisitCreate(BaseModel):
    type_id: int
    title: str
    date: datetime
    start_date: datetime
    end_date: datetime
    shift_id: int
    shift_name: Optional[str]
    status: str
    assigned_id: int
    business_id: Optional[int]
    business_name: Optional[str]
    construction_id: Optional[int]
    construction_name: Optional[str]
    observation: str
    created_by: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "title": "Nueva visita",
                "type_id": 1,
                "date": datetime.now(),
                "start_date": datetime.now(),
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


class VisitPatchSchema (BaseModel):
    status: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "status": "PROGRAMADA",
            }}


class VisitSchema (VisitCreate):
    id: int


class ReportContact(BaseModel):
    contact_id: int
    contact_names: str
    contact_email: str


class VisitReportSchema(BaseModel):
    user: str
    user_phone: str
    user_email: str
    observations: str
    relevant: str
    date: str
    contacts: Optional[List[ReportContact]]


class VisitsExport(BaseModel):
    start_date: datetime = Field(alias="startDate")
    end_date: datetime = Field(alias="endDate")
