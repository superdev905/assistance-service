from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserResponse (BaseModel):
    id: int
    names: str
    paternal_surname: str = Field(alias='paternalSurname')
    maternal_surname: str = Field(alias='maternalSurname')
    charge_name: Optional[str] = Field(alias='charge')
    email: str


class VisitHome(BaseModel):
    business_id: int = Field(alias="businessId")
    business_name: str = Field(alias="businessName")
    construction_id: int = Field(alias="constructionId")
    construction_name: str = Field(alias="constructionName")
    start_date: datetime = Field(alias="startDate")
    end_date: datetime = Field(alias="endDate")
    shift_id: int = Field(alias="shiftId")
    shift_name: str = Field(alias="shiftName")
    type_name: str = Field(alias="typeName")
    title: str
    status: str
    assigned: UserResponse

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


# employee_rut = Column(String(12), nullable=False)
# employee_id = Column(Integer, nullable=False)
# employee_name = Column(String(100), nullable=False)
# employee_lastname = Column(String(100), nullable=False)
# attended_id = Column(Integer, nullable=False)
# attended_name = Column(String(200), nullable=False)
# is_attended_relative = Column(Boolean, nullable=False, server_default="0")
# date = Column(DateTime, nullable=False)
# source_system = Column(String(100), nullable=False)
# source_business = Column(String(100), nullable=False)
# attention_place = Column(String(255), nullable=False)
# contact_method = Column(String(255), nullable=False)
# business_id = Column(Integer)
# business_name = Column(String(255))
# construction_id = Column(Integer)
# construction_name = Column(String(255))
# topic_id = Column(Integer, nullable=False)
# area_id = Column(Integer, nullable=False)
# area_name = Column(String(100), nullable=False)
# management_id = Column(Integer, nullable=False)
# is_social_case = Column(String(2), nullable=False)
# status = Column(String(50), nullable=False)
# company_report = Column(String(2), nullable=False)
# company_report_observation = Column(String(400))
# observation = Column(String(255), nullable=False)
# assigned_id = Column(Integer, nullable=False)
# case_id = Column(Integer)
# task_id = Column(Integer)


class AssistanceHome(BaseModel):
    date: datetime
    employee_rut: str = Field(alias="employeeRut")
    employee_id: int = Field(alias="employeeId")
    employee_name: str = Field(alias="employeeName")
    employee_lastname: str = Field(alias="employeeLastname")
    attended_id: int = Field(alias="attendedId")
    attended_name: str = Field(alias="attendedName")
    is_attended_relative: bool = Field(alias="isAttendedRelative")
    attention_place: str = Field(alias="attentionPlace")
    area_name: str = Field(alias="areaName")
    area_id: int = Field(alias="areaId")
    management_id: int = Field(alias="managementId")
    management_name: str = Field(alias="managementName")
    status: str
    assistance: UserResponse

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
