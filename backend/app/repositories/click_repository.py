from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.click import Click
from backend.app.models.link import Link


class ClickRepository:
    def create(
        self,
        db: Session,
        *,
        link_id: str,
        ip: str,
        user_agent: str,
        referer: str | None,
        country: str | None,
        device_type: str,
        source: str,
    ) -> Click:
        click = Click(
            link_id=link_id,
            ip=ip,
            user_agent=user_agent,
            referer=referer,
            country=country,
            device_type=device_type,
            source=source,
        )
        db.add(click)
        db.flush()
        return click

    def count_for_link(self, db: Session, link_id: str, start_date: date | None = None, end_date: date | None = None) -> int:
        stmt = select(func.count(Click.id)).where(Click.link_id == link_id)
        stmt = self._apply_date_filters(stmt, start_date, end_date)
        return db.execute(stmt).scalar_one()

    def get_daily_counts(
        self,
        db: Session,
        link_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[tuple[str, int]]:
        day = func.date(Click.timestamp).label("day")
        stmt = select(day, func.count(Click.id)).where(Click.link_id == link_id)
        stmt = self._apply_date_filters(stmt, start_date, end_date)
        stmt = stmt.group_by(day).order_by(day)
        return list(db.execute(stmt).all())

    def get_dimension_counts(
        self,
        db: Session,
        *,
        link_id: str,
        column_name: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[tuple[str, int]]:
        column = getattr(Click, column_name)
        stmt = select(column, func.count(Click.id)).where(Click.link_id == link_id)
        stmt = self._apply_date_filters(stmt, start_date, end_date)
        stmt = stmt.group_by(column).order_by(func.count(Click.id).desc(), column.asc())
        return [(label or "unknown", total) for label, total in db.execute(stmt).all()]

    def get_recent_clicks(
        self,
        db: Session,
        *,
        link_id: str,
        limit: int = 20,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Click]:
        stmt = select(Click).where(Click.link_id == link_id)
        stmt = self._apply_date_filters(stmt, start_date, end_date)
        stmt = stmt.order_by(Click.timestamp.desc()).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def list_for_export(
        self,
        db: Session,
        *,
        link_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Click]:
        stmt = select(Click).where(Click.link_id == link_id)
        stmt = self._apply_date_filters(stmt, start_date, end_date)
        stmt = stmt.order_by(Click.timestamp.desc())
        return list(db.execute(stmt).scalars().all())

    def count_all(self, db: Session, start_date: date | None = None, end_date: date | None = None) -> int:
        stmt = select(func.count(Click.id))
        stmt = self._apply_date_filters(stmt, start_date, end_date)
        return db.execute(stmt).scalar_one()

    def count_active_links(self, db: Session, start_date: date | None = None, end_date: date | None = None) -> int:
        stmt = select(func.count(func.distinct(Click.link_id)))
        stmt = self._apply_date_filters(stmt, start_date, end_date)
        return db.execute(stmt).scalar_one()

    def get_daily_counts_all(
        self,
        db: Session,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[tuple[str, int]]:
        day = func.date(Click.timestamp).label("day")
        stmt = select(day, func.count(Click.id))
        stmt = self._apply_date_filters(stmt, start_date, end_date)
        stmt = stmt.group_by(day).order_by(day)
        return list(db.execute(stmt).all())

    def get_dimension_counts_all(
        self,
        db: Session,
        *,
        column_name: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[tuple[str, int]]:
        column = getattr(Click, column_name)
        stmt = select(column, func.count(Click.id))
        stmt = self._apply_date_filters(stmt, start_date, end_date)
        stmt = stmt.group_by(column).order_by(func.count(Click.id).desc(), column.asc())
        return [(label or "unknown", total) for label, total in db.execute(stmt).all()]

    def get_recent_clicks_all(
        self,
        db: Session,
        *,
        limit: int = 12,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[tuple[Click, str, str | None]]:
        stmt = select(Click, Link.short_code, Link.description).join(Link, Link.id == Click.link_id)
        stmt = self._apply_date_filters(stmt, start_date, end_date)
        stmt = stmt.order_by(Click.timestamp.desc()).limit(limit)
        return list(db.execute(stmt).all())

    def _apply_date_filters(self, stmt, start_date: date | None, end_date: date | None):
        if start_date:
            start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
            stmt = stmt.where(Click.timestamp >= start_dt)
        if end_date:
            end_dt = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=timezone.utc)
            stmt = stmt.where(Click.timestamp < end_dt)
        return stmt
