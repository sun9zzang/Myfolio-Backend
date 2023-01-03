from sqlalchemy import Column, ForeignKey, String, Text, text
from sqlalchemy.dialects.mysql import INTEGER, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func

from app.core.config import config
from app.core.models.base_generate import Base


class TblFolios(Base):
    __tablename__ = "folios"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    type = Column(String(10), nullable=False)
    title = Column(String(200), nullable=False)
    author_id = Column(ForeignKey("users.id"))
    base_template_id = Column(ForeignKey("templates.id"))
    base_template_content = Column(Text, nullable=False)
    base_template_fetched_at = Column(
        TIMESTAMP(fsp=config.DATETIME_PRECISION),
        server_default=func.now(config.DATETIME_PRECISION),
    )
    user_input_data = Column(Text, default="{}")
    last_modified = Column(
        TIMESTAMP(fsp=config.DATETIME_PRECISION),
        nullable=False,
        server_default=text(
            f"CURRENT_TIMESTAMP({config.DATETIME_PRECISION}) ON UPDATE CURRENT_TIMESTAMP({config.DATETIME_PRECISION})"
        ),
    )

    # base_template = relationship("TblTemplates", back_populates="folios")
    author = relationship("TblUsers", back_populates="folios")
