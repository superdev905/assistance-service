from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AssistanceCreate(BaseModel):
    date: datetime
    employee_id: int
    source_system: str
    source_business: str
    attention_place: str
    contact_method: str
    business_id: int
    business_name: Optional[str]
    construction_id: int
    construction_name: Optional[str]
    topic_id: int
    area_id: int
    management_id: int
    is_social_case: str
    status: str
    company_report: str
    assigned_id: int
    case_id: int
    task_id: int
    observation: str
    attached_url: Optional[str] = ""
    created_by: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "date": datetime.now(),
                "employee_id": 1,
                "source_system": "VISITAS",
                "source_business": "FUNDACIÓN CHCC",
                "attention_place": 'Oficina',
                "contact_method": "Presencial",
                "business_id": 1,
                "business_name": "",
                "construction_id": 1,
                "construction_name": "",
                "topic_id": 1,
                "area_id": 1,
                "management_id": 1,
                "is_social_case": 'NO',
                "status": "COMPLETADO",
                "company_report": "SI",
                "case_id": 1,
                "task_id": 1,
                "attached_url": "",
                "observation": "Observation",
                "created_by": 1,
                "assigned_id":  1
            }
        }


class AssistancePatchSchema (BaseModel):
    status: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "status": "",
            }}


class AssistanceSchema (AssistanceCreate):
    id: int
