from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.repositories.click_repository import ClickRepository
from backend.app.repositories.link_repository import LinkRepository
from backend.app.schemas.link import LinkCreate, LinkRead, LinkSummary, LinkUpdate


class LinkNotFoundError(Exception):
    pass


class LinkAlreadyExistsError(Exception):
    pass


class LinkService:
    def __init__(self) -> None:
        self.link_repository = LinkRepository()
        self.click_repository = ClickRepository()
        self.settings = get_settings()

    def create_link(self, db: Session, payload: LinkCreate) -> LinkRead:
        existing = self.link_repository.get_by_short_code(db, payload.short_code)
        if existing:
            raise LinkAlreadyExistsError(payload.short_code)

        link = self.link_repository.create(
            db,
            original_url=str(payload.original_url),
            short_code=payload.short_code,
            description=payload.description,
            tags=payload.tags,
        )
        db.commit()
        db.refresh(link)
        return self._serialize_link(link, total_clicks=0)

    def list_links(self, db: Session) -> list[LinkRead]:
        rows = self.link_repository.list_with_click_counts(db)
        return [self._serialize_link(link, total_clicks=total_clicks) for link, total_clicks in rows]

    def update_link(self, db: Session, link_id: str, payload: LinkUpdate) -> LinkRead:
        link = self.get_link_entity(db, link_id)
        updates = payload.model_dump(exclude_unset=True)

        if "original_url" in updates:
            updates["original_url"] = str(updates["original_url"])

        if "short_code" in updates:
            existing = self.link_repository.get_by_short_code(db, updates["short_code"])
            if existing and existing.id != link.id:
                raise LinkAlreadyExistsError(updates["short_code"])

        updated = self.link_repository.update(db, link, **updates)
        db.commit()
        db.refresh(updated)
        total_clicks = self.click_repository.count_for_link(db, updated.id)
        return self._serialize_link(updated, total_clicks=total_clicks)

    def delete_link(self, db: Session, link_id: str) -> None:
        link = self.get_link_entity(db, link_id)
        self.link_repository.delete(db, link)
        db.commit()

    def get_link_detail(self, db: Session, link_id: str) -> LinkRead:
        row = self.link_repository.get_with_click_count(db, link_id)
        if not row:
            raise LinkNotFoundError(link_id)
        link, total_clicks = row
        return self._serialize_link(link, total_clicks=total_clicks)

    def get_link_entity_by_short_code(self, db: Session, short_code: str):
        link = self.link_repository.get_by_short_code(db, short_code.strip().lower())
        if not link:
            raise LinkNotFoundError(short_code)
        return link

    def get_link_entity(self, db: Session, link_id: str):
        link = self.link_repository.get_by_id(db, link_id)
        if not link:
            raise LinkNotFoundError(link_id)
        return link

    def serialize_summary(self, link) -> LinkSummary:
        return LinkSummary(
            id=link.id,
            short_code=link.short_code,
            original_url=link.original_url,
            description=link.description,
            tags=link.tags or [],
            created_at=link.created_at,
            short_url=self.build_short_url(link.short_code),
        )

    def _serialize_link(self, link, *, total_clicks: int) -> LinkRead:
        return LinkRead(
            **self.serialize_summary(link).model_dump(),
            total_clicks=total_clicks,
        )

    def build_short_url(self, short_code: str) -> str:
        return f"{self.settings.base_url.rstrip('/')}/{short_code}"
