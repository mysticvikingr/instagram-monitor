from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.models.influencer_metrics_history import InfluencerMetricsHistory

router = APIRouter()

@router.get("/")
def influencerMetrics(db: Session = Depends(get_db)):
    return db.query(InfluencerMetricsHistory).all()
