import re
from datetime import date, datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


SHORT_CODE_PATTERN = re.compile(r"^[a-z0-9_-]+$")


class LinkCreate(BaseModel):
    original_url: AnyHttpUrl
    short_code: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    tags: list[str] = Field(default_factory=list)

    @field_validator("short_code")
    @classmethod
    def normalize_short_code(cls, value: str) -> str:
        short_code = value.strip().lower()
        if not SHORT_CODE_PATTERN.match(short_code):
            raise ValueError("short_code deve conter apenas letras minusculas, numeros, hifen ou underline")
        return short_code

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        normalized: list[str] = []
        for tag in value:
            item = tag.strip().lower()
            if item and item not in seen:
                normalized.append(item)
                seen.add(item)
        return normalized


class LinkSummary(BaseModel):
    id: str
    short_code: str
    original_url: str
    description: str | None
    tags: list[str]
    created_at: datetime
    short_url: str

    model_config = ConfigDict(from_attributes=True)


class LinkRead(LinkSummary):
    total_clicks: int


class ClickRead(BaseModel):
    id: str
    timestamp: datetime
    ip: str
    user_agent: str
    referer: str | None
    country: str | None
    device_type: str
    source: str

    model_config = ConfigDict(from_attributes=True)


class DailyClicks(BaseModel):
    date: date
    clicks: int


class DimensionClicks(BaseModel):
    label: str
    clicks: int


class LinkStats(BaseModel):
    link: LinkSummary
    total_clicks: int
    clicks_by_day: list[DailyClicks]
    clicks_by_device: list[DimensionClicks]
    clicks_by_source: list[DimensionClicks]
    recent_clicks: list[ClickRead]
