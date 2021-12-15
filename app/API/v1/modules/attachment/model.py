from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from app.database.base_class import Base
from sqlalchemy import Column, Integer, String


class Attachment (Base):
    __tablename__ = "attachment"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    file_name = Column(String(1024), nullable=False)
    file_key = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(String(20), nullable=False)
    source_system = Column(String(50))
    data_id = Column(Integer)
    assistance_id = Column(Integer, ForeignKey("assistance.id"))
    upload_date = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True),
                       onupdate=func.now(), server_default=func.now())
    assistance = relationship(
        "Assistance", back_populates="attachments", lazy="select")
