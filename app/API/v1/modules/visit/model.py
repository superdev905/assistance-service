from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, DateTime, Time
from app.database.base_class import Base
from sqlalchemy import Column, Integer, String


class Visit(Base):
    __tablename__ = "visit"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    type_id = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="1")
    shift_id = Column(Integer, nullable=False)
    shift_name = Column(String(120))
    status = Column(String(15), nullable=False, default="PROGRAMADA")
    assigned_id = Column(Integer, nullable=False)
    business_id = Column(Integer)
    construction_id = Column(Integer)
    business_name = Column(String(150))
    construction_name = Column(String(150))
    observation = Column(String(500), nullable=False)
    report_url = Column(String(255))
    report_key = Column(String(255))
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
    contacts = relationship(
        "ReportTarget", back_populates="visit", lazy="joined")


class ReportTarget(Base):
    __tablename__ = "report_target"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    contact_id = Column(Integer, nullable=False)
    visit_id = Column(Integer, ForeignKey(
        "visit.id", ondelete="CASCADE"), nullable=False)
    contact_names = Column(String(250), nullable=False)
    contact_email = Column(String(100), nullable=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
    visit = relationship(
        "Visit", back_populates="contacts", lazy="joined")
