from datetime import datetime, time, timedelta
from typing import Optional
from pydantic import BaseModel

""" date = Column(DateTime, nullable=False)
    source_system = Column(Integer, nullable=False)
    source_business = Column(Integer, nullable=False)
    attention_place = Column(String(255), nullable=False)
    contact_method = Column(String(255), nullable=False)
    business_id = Column(Integer, nullable=False)
    business_name = Column(String(255), nullable=False)
    construction_id = Column(Integer, nullable=False)
    construction_name = Column(String(255), nullable=False)
    topic_id = Column(Integer, nullable=False)
    management_id = Column(Integer, nullable=False)
    is_social_case = Column(String(2), nullable=False)
    status = Column(String(50), nullable=False)
    company_report = Column(String(2), nullable=False)
    observation = Column(String(255), nullable=False)
    assigned_id = Column(Integer, nullable=False)
    case_id = Column(Integer, nullable=False)
    task_id = Column(Integer, nullable=False)
    attached_url = Column(Integer)"""


class AssistanceCreate(BaseModel):
    date: datetime
    source_system: int
    source_business: int
    attention_place: str
    contact_method: str
    assigned_id: int
    business_id: int
    business_name: Optional[str]
    construction_id: int
    construction_name: Optional[str]
    topic_id: int
    management_id: int
    is_social_case: str
    status: str
    company_report: str
    assigned_id: int
    case_id: int
    task_id: int
    observation: str
    attached_url: Optional[str] = ""

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "date": datetime.now(),
                "assigned_id":  1,
                "business_id": 1,
                "business_name": "",
                "construction_id": 1,
                "construction_name": "",
                "observation": "Observation",
                "created_by": 1
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
