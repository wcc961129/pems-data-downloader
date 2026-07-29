import re
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from .models import RemoteFile


PACIFIC = ZoneInfo("America/Los_Angeles")
SUPPORTED_DISTRICTS = (3, 4, 5, 6, 7, 8, 10, 11, 12)
DAILY_PATTERN = re.compile(
    r"^d(?P<district>\d{2})_text_station_5min_"
    r"(?P<year>\d{4})_(?P<month>\d{2})_(?P<day>\d{2})\.txt\.gz$"
)
HOURLY_PATTERN = re.compile(
    r"^d(?P<district>\d{2})_text_station_hour_"
    r"(?P<year>\d{4})_(?P<month>\d{2})\.txt\.gz$"
)
META_PATTERN = re.compile(
    r"^d(?P<district>\d{2})_text_meta_"
    r"(?P<year>\d{4})_(?P<month>\d{2})_(?P<day>\d{2})\.(?:txt|csv)$"
)


def parse_datetime(value: str, end_of_day: bool = False) -> datetime:
    value = value.strip()
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO date/time: {value}") from exc
    if "T" not in value and " " not in value:
        parsed = datetime.combine(
            parsed.date(),
            time.max.replace(microsecond=0) if end_of_day else time.min,
        )
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=PACIFIC)
    return parsed.astimezone(PACIFIC)


def daily_filename(district: int, day: date) -> str:
    return f"d{district:02d}_text_station_5min_{day:%Y_%m_%d}.txt.gz"


def monthly_hour_filename(district: int, day: date) -> str:
    return f"d{district:02d}_text_station_hour_{day:%Y_%m}.txt.gz"


def parse_remote_file(name: str, url: str) -> RemoteFile | None:
    for dataset, pattern in (
        ("station_5min", DAILY_PATTERN),
        ("station_hour", HOURLY_PATTERN),
        ("meta", META_PATTERN),
    ):
        match = pattern.fullmatch(name)
        if match:
            values = {key: int(value) for key, value in match.groupdict().items()}
            file_date = date(
                values["year"],
                values["month"],
                values.get("day", 1),
            )
            return RemoteFile(
                name=name,
                url=url,
                district=values["district"],
                dataset=dataset,
                file_date=file_date,
            )
    return None


def expected_days(start: datetime, end: datetime) -> list[date]:
    if end < start:
        raise ValueError("End time must not be earlier than start time")
    count = (end.date() - start.date()).days
    return [date.fromordinal(start.date().toordinal() + offset) for offset in range(count + 1)]


def expected_filenames(
    district: int,
    days: list[date],
    granularity: str,
) -> dict[int, set[str]]:
    if granularity == "5min":
        filename = daily_filename
    elif granularity == "hour":
        filename = monthly_hour_filename
    else:
        raise ValueError(f"Unsupported granularity: {granularity}")
    expected_by_year: dict[int, set[str]] = {}
    for day in days:
        expected_by_year.setdefault(day.year, set()).add(filename(district, day))
    return expected_by_year
