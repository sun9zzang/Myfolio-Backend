from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func

from app.core.config import settings
from app.core.models.base_generate import Base


class TblTemplates(Base):
    __tablename__ = "templates"

    template_id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    title = Column(String(settings.TEMPLATE_TITLE_MAX_LENGTH), nullable=False)
    likes = Column(INTEGER(unsigned=True), default=0)
    content = Column(Text, nullable=False)
    created_date = Column(
        DATETIME(fsp=settings.DATETIME_PRECISION),
        server_default=func.now(settings.DATETIME_PRECISION),
    )
    user_id = Column(ForeignKey("users.user_id"))

    user = relationship("TblUsers", back_populates="templates")
