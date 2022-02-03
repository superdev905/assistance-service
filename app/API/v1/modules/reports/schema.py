from typing import Optional
from pydantic import BaseModel


class ReportCategoryBase(BaseModel):
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Charlas",
            }
        }

class ReportVisitDateRange(BaseModel):
    startDate: Optional[str]
    endDate: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "startDate": "2022-02-02T21:15:59.634Z",
                "endDate": "2022-02-02T21:15:59.634Z"
            }
        }

class ReportVisitsbyCompany(BaseModel):
    business_id: str
    startDate: Optional[str]
    endDate: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "business_id": "1",
                "startDate": "2022-02-02T21:15:59.634Z",
                "endDate": "2022-02-02T21:15:59.634Z"
            }
        }

class ReportVisitsbyAssigned(BaseModel):
    assigned_id: str
    startDate: Optional[str]
    endDate: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "assigned_id": "1",
                "startDate": "2022-02-02T21:15:59.634Z",
                "endDate": "2022-02-02T21:15:59.634Z"
            }
        }

class ReportAssistancebyEmployee(BaseModel):
    employee_id: str
    startDate: Optional[str]
    endDate: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "employee_id": "1",
                "startDate": "2022-02-02T21:15:59.634Z",
                "endDate": "2022-02-02T21:15:59.634Z"
            }
        }

class ReportAssistancebyCompany(BaseModel):
    business_id: str
    startDate: Optional[str]
    endDate: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "business_id": "1",
                "startDate": "2022-02-02T21:15:59.634Z",
                "endDate": "2022-02-02T21:15:59.634Z"
            }
        }



class ReportCategoryCreate(ReportCategoryBase):
    pass


class ReportCategoryItem(ReportCategoryBase):
    id: int
    created_by: int

    class Config:
        allow_population_by_field_name = True
