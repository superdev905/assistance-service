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
    id: int
    startDate: Optional[str]
    endDate: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "startDate": "2022-02-02T21:15:59.634Z",
                "endDate": "2022-02-02T21:15:59.634Z"
            }
        }

class ReportVisitsbyAssigned(BaseModel):
    id: int
    startDate: Optional[str]
    endDate: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "startDate": "2022-02-02T21:15:59.634Z",
                "endDate": "2022-02-02T21:15:59.634Z"
            }
        }

class ReportAssistancebyEmployee(BaseModel):
    id: int
    startDate: Optional[str]
    endDate: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "startDate": "2022-02-02T21:15:59.634Z",
                "endDate": "2022-02-02T21:15:59.634Z"
            }
        }

class ReportAssistancebyCompany(BaseModel):
    id: int
    startDate: Optional[str]
    endDate: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {"""  """
                "id": 1,
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
