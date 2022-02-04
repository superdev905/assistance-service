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
    id: int
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


class AssistanceHome(BaseModel):
    date: datetime
    id: int
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


class Benefit(BaseModel):
    id: int
    name: str
    code: str


class ActivityItem(BaseModel):
    id: int
    state: str
    benefit: Benefit
    name: str
    founding: str
    annual_amount: int = Field(alias="annualAmount")
    benefit_cost: float = Field(alias="benefitCost")
    description: str
    created_date: datetime = Field(alias="createdDate")
    start_date: datetime = Field(alias="startDate")
    end_date: datetime = Field(alias="endDate")
    is_active: bool = Field(alias="isActive")
    reuse_quantity: int = Field(alias="reuseQuantity")
    execute_schedule: int = Field(alias="executeSchedule")
    temporality: str
    benefit_id: int = Field(alias="benefitId")
    employee_id: int = Field(alias="employeeId")
    employee_name: str = Field(alias="employeeName")
    assistance_id: Optional[int] = Field(alias="assistanceId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class DeliveredBenefit(BaseModel):
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
    status: str
    activity: Optional[ActivityItem]
    assistance: UserResponse

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
