from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from app.database.base_class import Base
from sqlalchemy import Column, Integer, String


class AssistanceConstruction(Base):
    __tablename__ = "assistance_construction"
    id = Column(Integer, primary_key=True,
                unique=True, autoincrement=True)
    type_name = Column(String(255), nullable=False)
    type_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    visit_id = Column(Integer, ForeignKey('visit.id', ondelete='CASCADE'))
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       server_default=func.now(), onupdate=func.now())
    charge = relationship(
        "Visit", uselist=False)
