from fastapi import Request
from sqlalchemy.orm import Session

from backend.app.repositories.click_repository import ClickRepository
from backend.app.services.link_service import LinkService
from backend.app.utils.request_context import build_tracking_context


class TrackingService:
    def __init__(self) -> None:
        self.link_service = LinkService()
        self.click_repository = ClickRepository()

    def resolve_and_track(self, db: Session, short_code: str, request: Request):
        link = self.link_service.get_link_entity_by_short_code(db, short_code)
        context = build_tracking_context(request)
        self.click_repository.create(
            db,
            link_id=link.id,
            ip=context["ip"],
            user_agent=context["user_agent"],
            referer=context["referer"],
            country=context["country"],
            device_type=context["device_type"],
            source=context["source"],
        )
        db.commit()
        return link
