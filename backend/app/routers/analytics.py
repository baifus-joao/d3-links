from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.analytics import OverviewStats
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

analytics_service = AnalyticsService()


def validate_date_range(start_date: date | None, end_date: date | None) -> None:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date nao pode ser maior que end_date",
        )


@router.get("/overview", response_model=OverviewStats)
def get_overview(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    top_n: int = Query(default=6, ge=3, le=12),
    db: Session = Depends(get_db),
) -> OverviewStats:
    validate_date_range(start_date, end_date)
    return analytics_service.get_overview(db, start_date=start_date, end_date=end_date, top_n=top_n)
