from sqlalchemy import Column, Integer, String, DateTime, Index
from app.db.session import Base
from sqlalchemy.sql import func

class PostMetricsHistory(Base):
    __tablename__ = "post_metrics_history"

    id = Column(Integer, primary_key=True, index=True)
    post_code = Column(String(50), nullable=False)
    post_id = Column(String(50), nullable=False)
    like_count = Column(Integer)
    comment_count = Column(Integer)
    play_count = Column(Integer)
    recorded_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_post_code_recorded_at", "post_code", "recorded_at"),
    )
