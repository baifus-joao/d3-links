from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.services.link_service import LinkNotFoundError
from backend.app.services.tracking_service import TrackingService

router = APIRouter(tags=["redirect"])

tracking_service = TrackingService()


@router.get("/{short_code}")
def redirect_short_link(short_code: str, request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    try:
        link = tracking_service.resolve_and_track(db, short_code, request)
    except LinkNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="link curto nao encontrado") from exc

    return RedirectResponse(url=link.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
