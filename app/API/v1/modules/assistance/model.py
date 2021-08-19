from sqlalchemy.sql.expression import null
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import DateTime, Time
from app.database.base_class import Base
from sqlalchemy import Column, Integer, String


class Assistance(Base):
    __tablename__ = "assistance"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
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
    attached_url = Column(Integer)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
