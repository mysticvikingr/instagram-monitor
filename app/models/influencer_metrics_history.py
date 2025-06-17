from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Index
from app.db.session import Base
from sqlalchemy.sql import func

class InfluencerMetricsHistory(Base):
    __tablename__ = "influencer_metrics_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    username = Column(String(255), nullable=False)
    bio = Column(Text)
    follower_count = Column(Integer)
    following_count = Column(Integer)
    post_count = Column(Integer)
    recorded_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_user_id_recorded_at", "user_id", "recorded_at"),
    )
