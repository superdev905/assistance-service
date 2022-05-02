from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, Integer, String


class Assistance(Base):
    __tablename__ = "assistance"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    employee_rut = Column(String(12), nullable=False)
    employee_id = Column(Integer, nullable=False)
    employee_name = Column(String(100), nullable=False)
    employee_lastname = Column(String(100), nullable=False)
    attended_id = Column(Integer, nullable=False)
    attended_name = Column(String(200), nullable=False)
    is_attended_relative = Column(Boolean, nullable=False, server_default="0")
    date = Column(DateTime, nullable=False)
    source_system = Column(String(100), nullable=False)
    source_business = Column(String(100), nullable=False)
    attention_place = Column(String(255), nullable=False)
    contact_method = Column(String(255), nullable=False)
    business_id = Column(Integer)
    business_name = Column(String(255))
    construction_id = Column(Integer)
    construction_name = Column(String(255))
    topic_id = Column(Integer, nullable=False)
    area_id = Column(Integer, nullable=False)
    area_name = Column(String(100), nullable=False)
    management_id = Column(Integer, nullable=False)
    is_social_case = Column(String(2), nullable=False)
    status = Column(String(50), nullable=False)
    company_report = Column(String(2), nullable=False)
    company_report_observation = Column(String(400))
    observation = Column(String(255), nullable=False)
    assigned_id = Column(Integer, nullable=False)
    case_id = Column(Integer)
    task_id = Column(Integer)
    visit_id = Column(Integer, ForeignKey("visit.id", ondelete="CASCADE"))
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
    employee_company_id = Column(Integer, nullable=True)

    visit = relationship("Visit", uselist=False)
    attachments = relationship(
        "Attachment", back_populates="assistance", lazy="joined")
