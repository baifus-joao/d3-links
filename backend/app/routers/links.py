from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.link import LinkCreate, LinkRead, LinkStats
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.link_service import LinkAlreadyExistsError, LinkNotFoundError, LinkService

router = APIRouter(prefix="/links", tags=["links"])

link_service = LinkService()
analytics_service = AnalyticsService()


def validate_date_range(start_date: date | None, end_date: date | None) -> None:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date nao pode ser maior que end_date",
        )


@router.post("", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
def create_link(payload: LinkCreate, db: Session = Depends(get_db)) -> LinkRead:
    try:
        return link_service.create_link(db, payload)
    except LinkAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"short_code '{exc.args[0]}' ja existe") from exc


@router.get("", response_model=list[LinkRead])
def list_links(db: Session = Depends(get_db)) -> list[LinkRead]:
    return link_service.list_links(db)


@router.get("/{link_id}", response_model=LinkRead)
def get_link(link_id: str, db: Session = Depends(get_db)) -> LinkRead:
    try:
        return link_service.get_link_detail(db, link_id)
    except LinkNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="link nao encontrado") from exc


@router.get("/{link_id}/stats", response_model=LinkStats)
def get_link_stats(
    link_id: str,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> LinkStats:
    validate_date_range(start_date, end_date)
    try:
        return analytics_service.get_stats(db, link_id, start_date, end_date)
    except LinkNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="link nao encontrado") from exc


@router.get("/{link_id}/clicks/export")
def export_link_clicks(
    link_id: str,
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Response:
    validate_date_range(start_date, end_date)
    try:
        csv_content, filename = analytics_service.export_clicks_csv(db, link_id, start_date, end_date)
    except LinkNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="link nao encontrado") from exc

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=csv_content, media_type="text/csv", headers=headers)


@router.get("/{link_id}/qr-code")
def get_qr_code(link_id: str, db: Session = Depends(get_db)) -> Response:
    try:
        image = analytics_service.generate_qr_code(db, link_id)
    except LinkNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="link nao encontrado") from exc

    return Response(content=image, media_type="image/png")
