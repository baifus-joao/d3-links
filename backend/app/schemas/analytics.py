from datetime import date, datetime

from pydantic import BaseModel

from backend.app.schemas.link import DailyClicks, DimensionClicks


class OverviewSummary(BaseModel):
    start_date: date | None
    end_date: date | None
    period_days: int | None
    total_links: int
    active_links: int
    period_clicks: int
    previous_period_clicks: int | None
    period_change_percent: float | None
    top_link_id: str | None
    top_link_short_code: str | None
    top_link_clicks: int
    top_source: str | None
    top_source_clicks: int


class OverviewLinkRank(BaseModel):
    id: str
    short_code: str
    description: str | None
    tags: list[str]
    short_url: str
    total_clicks: int
    period_clicks: int
    share_percent: float
    last_click_at: datetime | None


class OverviewRecentClick(BaseModel):
    link_id: str
    short_code: str
    description: str | None
    timestamp: datetime
    source: str
    device_type: str
    country: str | None
    referer: str | None
    ip: str


class OverviewStats(BaseModel):
    summary: OverviewSummary
    clicks_by_day: list[DailyClicks]
    clicks_by_source: list[DimensionClicks]
    clicks_by_device: list[DimensionClicks]
    top_links: list[OverviewLinkRank]
    recent_clicks: list[OverviewRecentClick]
