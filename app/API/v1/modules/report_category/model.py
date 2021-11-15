from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import Boolean, DateTime
from app.database.base_class import Base
from sqlalchemy import Column, Integer, String


class VisitReportCategory(Base):
    __tablename__ = "visit_report_category"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    is_active = Column(Boolean, nullable=False)
    description = Column(String(220))
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
