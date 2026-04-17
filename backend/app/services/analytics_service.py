import csv
from datetime import date, datetime, time, timedelta, timezone
from io import StringIO

from sqlalchemy.orm import Session

from backend.app.repositories.click_repository import ClickRepository
from backend.app.schemas.link import ClickRead, DailyClicks, DimensionClicks, LinkStats
from backend.app.schemas.analytics import OverviewLinkRank, OverviewRecentClick, OverviewStats, OverviewSummary
from backend.app.services.link_service import LinkService
from backend.app.utils.qr_code import generate_qr_code_png


class AnalyticsService:
    def __init__(self) -> None:
        self.link_service = LinkService()
        self.click_repository = ClickRepository()

    def get_stats(self, db: Session, link_id: str, start_date: date | None = None, end_date: date | None = None) -> LinkStats:
        link = self.link_service.get_link_entity(db, link_id)
        total_clicks = self.click_repository.count_for_link(db, link.id, start_date, end_date)
        daily = self.click_repository.get_daily_counts(db, link.id, start_date, end_date)
        device = self.click_repository.get_dimension_counts(
            db,
            link_id=link.id,
            column_name="device_type",
            start_date=start_date,
            end_date=end_date,
        )
        source = self.click_repository.get_dimension_counts(
            db,
            link_id=link.id,
            column_name="source",
            start_date=start_date,
            end_date=end_date,
        )
        recent = self.click_repository.get_recent_clicks(
            db,
            link_id=link.id,
            start_date=start_date,
            end_date=end_date,
        )

        return LinkStats(
            link=self.link_service.serialize_summary(link),
            total_clicks=total_clicks,
            clicks_by_day=[DailyClicks(date=self._coerce_grouped_day(day), clicks=clicks) for day, clicks in daily],
            clicks_by_device=[DimensionClicks(label=label, clicks=clicks) for label, clicks in device],
            clicks_by_source=[DimensionClicks(label=label, clicks=clicks) for label, clicks in source],
            recent_clicks=[ClickRead.model_validate(click) for click in recent],
        )

    def export_clicks_csv(
        self,
        db: Session,
        link_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[str, str]:
        link = self.link_service.get_link_entity(db, link_id)
        clicks = self.click_repository.list_for_export(db, link_id=link.id, start_date=start_date, end_date=end_date)

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "click_id",
                "link_id",
                "short_code",
                "original_url",
                "timestamp",
                "ip",
                "user_agent",
                "referer",
                "country",
                "device_type",
                "source",
            ]
        )
        for click in clicks:
            writer.writerow(
                [
                    click.id,
                    link.id,
                    link.short_code,
                    link.original_url,
                    click.timestamp.isoformat(),
                    click.ip,
                    click.user_agent,
                    click.referer or "",
                    click.country or "",
                    click.device_type,
                    click.source,
                ]
            )

        return buffer.getvalue(), f"d3-links-{link.short_code}-clicks.csv"

    def generate_qr_code(self, db: Session, link_id: str) -> bytes:
        link = self.link_service.get_link_entity(db, link_id)
        return generate_qr_code_png(self.link_service.build_short_url(link.short_code))

    def get_overview(
        self,
        db: Session,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        top_n: int = 6,
    ) -> OverviewStats:
        total_links = self.link_service.link_repository.count_all(db)
        period_clicks = self.click_repository.count_all(db, start_date, end_date)
        active_links = self.click_repository.count_active_links(db, start_date, end_date)
        daily = self.click_repository.get_daily_counts_all(db, start_date, end_date)
        source = self.click_repository.get_dimension_counts_all(
            db,
            column_name="source",
            start_date=start_date,
            end_date=end_date,
        )
        device = self.click_repository.get_dimension_counts_all(
            db,
            column_name="device_type",
            start_date=start_date,
            end_date=end_date,
        )
        recent = self.click_repository.get_recent_clicks_all(
            db,
            start_date=start_date,
            end_date=end_date,
        )

        start_dt, end_dt = self._build_datetime_range(start_date, end_date)
        ranked_links_rows = self.link_service.link_repository.get_ranked_links(
            db,
            limit=top_n,
            start_date=start_dt,
            end_date=end_dt,
        )

        previous_clicks = None
        change_percent = None
        period_days = None
        if start_date and end_date:
            period_days = (end_date - start_date).days + 1
            previous_start, previous_end = self._previous_period(start_date, end_date)
            previous_clicks = self.click_repository.count_all(db, previous_start, previous_end)
            if previous_clicks == 0:
                change_percent = 100.0 if period_clicks > 0 else 0.0
            else:
                change_percent = round(((period_clicks - previous_clicks) / previous_clicks) * 100, 1)

        top_links = [
            OverviewLinkRank(
                id=link.id,
                short_code=link.short_code,
                description=link.description,
                tags=link.tags or [],
                short_url=self.link_service.build_short_url(link.short_code),
                total_clicks=total_clicks,
                period_clicks=period_link_clicks,
                share_percent=round((period_link_clicks / period_clicks) * 100, 1) if period_clicks else 0.0,
                last_click_at=last_click_at,
            )
            for link, period_link_clicks, total_clicks, last_click_at in ranked_links_rows
        ]

        top_link = next((item for item in top_links if item.period_clicks > 0 or item.total_clicks > 0), None)
        top_source = source[0] if source else (None, 0)

        return OverviewStats(
            summary=OverviewSummary(
                start_date=start_date,
                end_date=end_date,
                period_days=period_days,
                total_links=total_links,
                active_links=active_links,
                period_clicks=period_clicks,
                previous_period_clicks=previous_clicks,
                period_change_percent=change_percent,
                top_link_id=top_link.id if top_link else None,
                top_link_short_code=top_link.short_code if top_link else None,
                top_link_clicks=top_link.period_clicks if top_link else 0,
                top_source=top_source[0],
                top_source_clicks=top_source[1],
            ),
            clicks_by_day=[DailyClicks(date=self._coerce_grouped_day(day), clicks=clicks) for day, clicks in daily],
            clicks_by_source=[DimensionClicks(label=label, clicks=clicks) for label, clicks in source],
            clicks_by_device=[DimensionClicks(label=label, clicks=clicks) for label, clicks in device],
            top_links=top_links,
            recent_clicks=[
                OverviewRecentClick(
                    link_id=click.link_id,
                    short_code=short_code,
                    description=description,
                    timestamp=click.timestamp,
                    source=click.source,
                    device_type=click.device_type,
                    country=click.country,
                    referer=click.referer,
                    ip=click.ip,
                )
                for click, short_code, description in recent
            ],
        )

    def _build_datetime_range(
        self,
        start_date: date | None,
        end_date: date | None,
    ) -> tuple[datetime | None, datetime | None]:
        start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc) if start_date else None
        end_dt = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=timezone.utc) if end_date else None
        return start_dt, end_dt

    def _previous_period(self, start_date: date, end_date: date) -> tuple[date, date]:
        span = (end_date - start_date).days + 1
        previous_end = start_date - timedelta(days=1)
        previous_start = previous_end - timedelta(days=span - 1)
        return previous_start, previous_end

    def _coerce_grouped_day(self, value: date | datetime | str) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return date.fromisoformat(value)
