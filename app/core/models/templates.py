from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, DATETIME
from sqlalchemy.sql.expression import func

from app.core.models.base_generate import Base
from app.core.config import settings


class TblTemplates(Base):
    __tablename__ = "templates"

    template_id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    title = Column(String(settings.TEMPLATE_TITLE_MAX_LENGTH), nullable=False)
    likes = Column(INTEGER(unsigned=True), default=0)
    created_date = Column(
        DATETIME(fsp=settings.DATETIME_PRECISION),
        server_default=func.now(settings.DATETIME_PRECISION)
    )
    user_id = Column(ForeignKey("users.user_id"))

    user = relationship("TblUsers", back_populates="templates")
