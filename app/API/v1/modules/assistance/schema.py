from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from ..attachment.schema import AttachmentCreate


class AssistanceCreate(BaseModel):
    date: datetime
    employee_rut: str
    employee_id: int
    employee_name: str
    employee_lastname: str
    source_system: str
    source_business: str
    attention_place: str
    contact_method: str
    business_id: Optional[int]
    business_name: Optional[str]
    construction_id: Optional[int]
    construction_name: Optional[str]
    topic_id: int
    area_id: int
    area_name: str
    management_id: int
    is_social_case: str
    status: str
    company_report: str
    company_report_observation: Optional[str]
    assigned_id: int
    case_id: int
    task_id: int
    visit_id: Optional[int]
    observation: str
    attachments: List[Optional[AttachmentCreate]]
    created_by: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "date": datetime.now(),
                "employee_rut": '122.',
                "employee_id": 1,
                "employee_name": "Jhon Die Volkman Senger",
                "employee_lastname": "Jhon Die Volkman Senger",
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
                "area_name": "SALUD",
                "management_id": 1,
                "is_social_case": 'NO',
                "status": "COMPLETADO",
                "company_report": "SI",
                "case_id": 1,
                "task_id": 1,
                "visit_id": 4,
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


class Parameter(BaseModel):
    id: int
    description: Optional[str]
    name: Optional[str]


class Management(BaseModel):
    id: int
    name: str


class Business(BaseModel):
    rut: str
    id: int
    business_name: str
    address: str


class Construction(BaseModel):
    id: int
    name: str
    address: str


class AssistanceDetails(AssistanceCreate):
    id: int
    management: Parameter
    topic: Parameter
    area: Parameter
    task: Parameter
    business: Business
    construction: Construction

    class Config:
        allow_population_by_field_name = True
