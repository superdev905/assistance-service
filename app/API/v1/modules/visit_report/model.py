from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from app.database.base_class import Base
from sqlalchemy import Column, Integer, String


class VisitReport(Base):
    __tablename__ = "visit_report"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    visit_id = Column(Integer, ForeignKey("visit.id", ondelete="CASCADE"))
    date = Column(DateTime, nullable=False)
    relevant = Column(String(500), nullable=False)
    observations = Column(String(500), nullable=False)

    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
    visit = relationship("Visit", uselist=False)
