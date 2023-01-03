from sqlalchemy import Column, ForeignKey, String, Text, text
from sqlalchemy.dialects.mysql import TIMESTAMP, INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func

from app.core.config import config
from app.core.models.base_generate import Base


class TblTemplates(Base):
    __tablename__ = "templates"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    type = Column(String(10), nullable=False)
    title = Column(String(config.TEMPLATE_TITLE_MAX_LENGTH), nullable=False)
    likes = Column(INTEGER(unsigned=True), server_default=text("0"))
    created_at = Column(
        TIMESTAMP(fsp=config.DATETIME_PRECISION),
        server_default=func.now(config.DATETIME_PRECISION),
    )
    content = Column(Text, nullable=False)
    author_id = Column(ForeignKey("users.id"))

    author = relationship("TblUsers", back_populates="templates")
