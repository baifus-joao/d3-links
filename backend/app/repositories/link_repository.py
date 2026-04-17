from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.click import Click
from backend.app.models.link import Link


class LinkRepository:
    def create(
        self,
        db: Session,
        *,
        original_url: str,
        short_code: str,
        description: str | None,
        tags: list[str],
    ) -> Link:
        link = Link(
            original_url=original_url,
            short_code=short_code,
            description=description,
            tags=tags,
        )
        db.add(link)
        db.flush()
        return link

    def update(self, db: Session, link: Link, **fields) -> Link:
        for field, value in fields.items():
            setattr(link, field, value)
        db.add(link)
        db.flush()
        return link

    def delete(self, db: Session, link: Link) -> None:
        db.delete(link)
        db.flush()

    def get_by_id(self, db: Session, link_id: str) -> Link | None:
        return db.get(Link, link_id)

    def get_by_short_code(self, db: Session, short_code: str) -> Link | None:
        stmt = select(Link).where(Link.short_code == short_code)
        return db.execute(stmt).scalar_one_or_none()

    def list_with_click_counts(self, db: Session) -> list[tuple[Link, int]]:
        click_counts = (
            select(Click.link_id, func.count(Click.id).label("total_clicks"))
            .group_by(Click.link_id)
            .subquery()
        )

        stmt = (
            select(Link, func.coalesce(click_counts.c.total_clicks, 0))
            .outerjoin(click_counts, Link.id == click_counts.c.link_id)
            .order_by(Link.created_at.desc())
        )
        return list(db.execute(stmt).all())

    def get_with_click_count(self, db: Session, link_id: str) -> tuple[Link, int] | None:
        click_counts = (
            select(Click.link_id, func.count(Click.id).label("total_clicks"))
            .group_by(Click.link_id)
            .subquery()
        )

        stmt = (
            select(Link, func.coalesce(click_counts.c.total_clicks, 0))
            .outerjoin(click_counts, Link.id == click_counts.c.link_id)
            .where(Link.id == link_id)
        )
        return db.execute(stmt).first()

    def count_all(self, db: Session) -> int:
        stmt = select(func.count(Link.id))
        return db.execute(stmt).scalar_one()

    def get_ranked_links(
        self,
        db: Session,
        *,
        limit: int = 6,
        start_date=None,
        end_date=None,
    ) -> list[tuple[Link, int, int, object | None]]:
        filtered_clicks = select(
            Click.link_id,
            func.count(Click.id).label("period_clicks"),
            func.max(Click.timestamp).label("last_click_at"),
        )

        if start_date:
            filtered_clicks = filtered_clicks.where(Click.timestamp >= start_date)
        if end_date:
            filtered_clicks = filtered_clicks.where(Click.timestamp < end_date)

        filtered_clicks = filtered_clicks.group_by(Click.link_id).subquery()

        total_clicks = (
            select(Click.link_id, func.count(Click.id).label("total_clicks"))
            .group_by(Click.link_id)
            .subquery()
        )

        stmt = (
            select(
                Link,
                func.coalesce(filtered_clicks.c.period_clicks, 0),
                func.coalesce(total_clicks.c.total_clicks, 0),
                filtered_clicks.c.last_click_at,
            )
            .outerjoin(filtered_clicks, Link.id == filtered_clicks.c.link_id)
            .outerjoin(total_clicks, Link.id == total_clicks.c.link_id)
            .order_by(
                func.coalesce(filtered_clicks.c.period_clicks, 0).desc(),
                func.coalesce(total_clicks.c.total_clicks, 0).desc(),
                Link.short_code.asc(),
            )
            .limit(limit)
        )
        return list(db.execute(stmt).all())
