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
    is_close = Column(Boolean, nullable=False, server_default="0")
    is_close_pending = Column(Boolean, nullable=False, server_default="0")
    close_revision_id = Column(Integer, ForeignKey("visit_revision.id"))
    shift_id = Column(Integer, nullable=False)
    shift_name = Column(String(120))
    status = Column(String(15), nullable=False, default="PROGRAMADA")
    assigned_id = Column(Integer, nullable=False)
    business_id = Column(Integer)
    construction_id = Column(Integer)
    business_name = Column(String(150))
    construction_name = Column(String(150))
    observation = Column(String(500), nullable=False)
    company_workers = Column(Integer)
    outsourced_workers = Column(Integer)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
    reports = relationship(
        "VisitReport", back_populates="visit", lazy="select")
    close_revision = relationship(
        "VisitRevision", uselist=False, lazy="joined")


class VisitReport(Base):
    __tablename__ = "visit_report"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_name = Column(String(250), nullable=False)
    user_phone = Column(String(9))
    user_email = Column(String(100), nullable=False)
    observations = Column(String(800), nullable=False)
    relevant = Column(String(800), nullable=False)
    is_active = Column(Boolean, nullable=False)
    report_url = Column(String(255), nullable=False)
    report_key = Column(String(255), nullable=False)
    create_date = Column(DateTime(timezone=True),
                         nullable=False, server_default=func.now())
    visit_id = Column(Integer, ForeignKey(
        "visit.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
    visit = relationship(
        "Visit", back_populates="reports", lazy="select")
    contacts = relationship(
        "ReportTarget", back_populates="visit_report", lazy="joined")


class ReportTarget(Base):
    __tablename__ = "report_target"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    contact_id = Column(Integer, nullable=False)
    visit_report_id = Column(Integer, ForeignKey(
        "visit_report.id", ondelete="CASCADE"), nullable=False)
    contact_names = Column(String(250), nullable=False)
    contact_email = Column(String(100), nullable=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
    visit_report = relationship(
        "VisitReport", back_populates="contacts", lazy="joined")


class VisitRevision(Base):
    __tablename__ = "visit_revision"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    type = Column(String(20), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    comments = Column(String(800))
    approver_id = Column(Integer, nullable=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
