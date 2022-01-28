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


class ReportCategoryCreate(ReportCategoryBase):
    pass


class ReportCategoryItem(ReportCategoryBase):
    id: int
    created_by: int

    class Config:
        allow_population_by_field_name = True
