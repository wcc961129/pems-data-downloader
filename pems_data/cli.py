import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

from . import __version__
from .browser import authorize, run
from .diagnostics import diagnose_environment
from .discovery import discover_latest, discover_stations
from .fetch import execute
from .models import FetchPlan, Region
from .planner import PACIFIC, SUPPORTED_DISTRICTS, parse_datetime
from .profiles import PROFILES, get_profile


def _csv_ints(values: list[str] | None) -> frozenset[int]:
    return frozenset(int(part) for value in values or [] for part in value.split(",") if part)


def _csv_strings(values: list[str] | None) -> frozenset[str]:
    return frozenset(
        part.strip().upper()
        for value in values or []
        for part in value.split(",")
        if part.strip()
    )


def _bbox(value: str | None):
    if not value:
        return None
    numbers = tuple(float(item) for item in value.split(","))
    if len(numbers) != 4:
        raise ValueError("Bounding box must be west,south,east,north")
    west, south, east, north = numbers
    if west >= east or south >= north:
        raise ValueError("Bounding box west/south must be smaller than east/north")
    return numbers


def _add_region_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--bbox",
        help="WGS84 bounding box as west,south,east,north",
    )
    parser.add_argument(
        "--station-id",
        action="append",
        help="station ID or comma-separated IDs; may be repeated",
    )
    parser.add_argument(
        "--freeway",
        action="append",
        help="freeway number or comma-separated numbers; may be repeated",
    )
    parser.add_argument(
        "--direction",
        action="append",
        help="N, S, E, or W; comma-separated values are accepted",
    )
    parser.add_argument(
        "--lane-type",
        action="append",
        help="PeMS lane type such as ML, HV, OR, or FR",
    )
    parser.add_argument(
        "--county",
        action="append",
        help="numeric county FIPS code; comma-separated values are accepted",
    )


def _region_from_args(args) -> Region:
    region = Region(
        station_ids=_csv_ints(args.station_id),
        bbox=_bbox(args.bbox),
        freeways=_csv_ints(args.freeway),
        directions=_csv_strings(args.direction),
        lane_types=_csv_strings(args.lane_type),
        counties=_csv_ints(args.county),
    )
    invalid_directions = sorted(region.directions - {"N", "S", "E", "W"})
    if invalid_directions:
        raise ValueError(
            "Direction must be N, S, E, or W: "
            + ", ".join(invalid_directions)
        )
    return region


def _validated_districts(values: list[str] | None) -> tuple[int, ...]:
    districts = tuple(sorted(_csv_ints(values)))
    unsupported = sorted(set(districts) - set(SUPPORTED_DISTRICTS))
    if unsupported:
        raise ValueError(f"Unsupported PeMS districts: {unsupported}")
    return districts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pems-data",
        description=(
            "Discover and download authenticated Caltrans PeMS Station data "
            "at five-minute or hourly granularity."
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--state",
        type=Path,
        default=Path(".pems/storage-state.json"),
        help="PeMS browser session file (default: .pems/storage-state.json)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    auth = subparsers.add_parser(
        "auth",
        help="open Chromium and save an authenticated PeMS session",
    )
    auth.add_argument(
        "--timeout-seconds",
        type=int,
        default=180,
        help="login timeout in seconds (default: 180)",
    )

    subparsers.add_parser(
        "profiles",
        help="list built-in reproducible research profiles",
    )

    latest = subparsers.add_parser(
        "latest",
        help="show the latest available Station archive periods",
    )
    latest.add_argument(
        "--district",
        action="append",
        required=True,
        help="District number or comma-separated numbers; may be repeated",
    )
    latest.add_argument(
        "--granularity",
        action="append",
        choices=("5min", "hour"),
        help="source granularity; omit to show both",
    )

    stations = subparsers.add_parser(
        "stations",
        help="search station metadata before downloading observations",
    )
    stations.add_argument(
        "--district",
        type=int,
        required=True,
        help="single Caltrans District number",
    )
    stations.add_argument(
        "--date",
        help="metadata date in YYYY-MM-DD form (default: today)",
    )
    stations.add_argument(
        "--limit",
        type=int,
        default=20,
        help="maximum rows to display (default: 20)",
    )
    _add_region_arguments(stations)

    subparsers.add_parser(
        "doctor",
        help="check Python, timezone, Chromium, and PeMS session setup",
    )

    fetch = subparsers.add_parser(
        "fetch",
        help="download and filter PeMS Station observations",
        description=(
            "Download official PeMS Station archives, then apply exact time "
            "and metadata filters. Selectors are combined with logical AND."
        ),
    )
    fetch.add_argument(
        "--profile",
        choices=sorted(PROFILES),
        help="built-in research profile; cannot be combined with custom selectors",
    )
    fetch.add_argument(
        "--start",
        help="inclusive ISO date/time in America/Los_Angeles",
    )
    fetch.add_argument(
        "--end",
        help="inclusive ISO date/time; a date-only value includes the full day",
    )
    fetch.add_argument(
        "--granularity",
        choices=("5min", "hour"),
        help="official PeMS source granularity (default: 5min)",
    )
    fetch.add_argument(
        "--district",
        action="append",
        help=(
            "required District number or comma-separated numbers; may be repeated"
        ),
    )
    _add_region_arguments(fetch)
    fetch.add_argument(
        "--output",
        type=Path,
        required=True,
        help="dataset output directory",
    )
    fetch.add_argument(
        "--keep-raw",
        action="store_true",
        help="retain complete PeMS source archives after processing",
    )
    fetch.add_argument(
        "--allow-empty",
        action="store_true",
        help="allow a successful dataset with zero observation rows",
    )
    fetch.add_argument(
        "--with-road-network",
        action="store_true",
        help="download matching official Caltrans SHN geometry",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "auth":
            run(authorize(args.state, args.timeout_seconds * 1000))
            print(f"Session saved to {args.state}")
            return 0
        if args.command == "profiles":
            for profile in PROFILES.values():
                print(
                    f"{profile.name}: {profile.title}; District {profile.district}; "
                    f"{profile.start}..{profile.end}; {len(profile.station_ids)} stations"
                )
            return 0
        if args.command == "doctor":
            checks, failed = diagnose_environment(args.state)
            for status, name, detail in checks:
                print(f"{status:4} {name}: {detail}")
            return 2 if failed else 0
        if args.command == "latest":
            districts = _validated_districts(args.district)
            granularities = tuple(args.granularity or ("5min", "hour"))
            files = run(
                discover_latest(
                    args.state,
                    districts,
                    granularities,
                    datetime.now(PACIFIC).year,
                )
            )
            print("district,granularity,latest_period,source_file")
            for item in files:
                granularity = (
                    "5min" if item.dataset == "station_5min" else "hour"
                )
                period = (
                    item.file_date.isoformat()
                    if granularity == "5min"
                    else item.file_date.strftime("%Y-%m")
                )
                print(
                    f"{item.district},{granularity},{period},{item.name}"
                )
            return 0
        if args.command == "stations":
            districts = _validated_districts([str(args.district)])
            if not districts:
                raise ValueError("A District is required")
            if args.limit < 1:
                raise ValueError("--limit must be at least 1")
            target = (
                parse_datetime(args.date).date()
                if args.date
                else datetime.now(PACIFIC).date()
            )
            region = _region_from_args(args)
            rows, total, metadata = run(
                discover_stations(
                    args.state,
                    districts[0],
                    target,
                    region,
                    args.limit,
                )
            )
            columns = (
                "station_id",
                "freeway",
                "direction",
                "lane_type",
                "absolute_postmile",
                "latitude",
                "longitude",
                "name",
            )
            writer = csv.writer(sys.stdout, lineterminator="\n")
            writer.writerow(columns)
            for row in rows:
                writer.writerow(row.get(column, "") for column in columns)
            print(
                f"Matched {total} stations using {metadata.name}; "
                f"displayed {len(rows)}",
                file=sys.stderr,
            )
            return 0
        if args.profile:
            custom = any(
                (
                    args.start,
                    args.end,
                    args.district,
                    args.bbox,
                    args.station_id,
                    args.freeway,
                    args.direction,
                    args.lane_type,
                    args.county,
                )
            )
            if custom:
                raise ValueError(
                    "--profile cannot be combined with custom time, district, or region selectors"
                )
            if args.granularity not in (None, "5min"):
                raise ValueError("Research profiles currently require --granularity 5min")
            profile = get_profile(args.profile)
            districts = (profile.district,)
            start = parse_datetime(profile.start)
            end = parse_datetime(profile.end, end_of_day=True)
            region = Region(station_ids=frozenset(profile.station_ids))
            granularity = "5min"
        else:
            if not args.start or not args.end:
                parser.error("fetch requires --start and --end unless --profile is used")
            if not args.district:
                parser.error(
                    "fetch requires --district; repeat it or use comma-separated "
                    "values for a multi-District request"
                )
            region = _region_from_args(args)
            if not region.station_ids and not region.bbox and not any(
                (args.freeway, args.direction, args.lane_type, args.county)
            ):
                parser.error(
                    "fetch requires at least one region selector: --bbox, --station-id, "
                    "--freeway, --direction, --lane-type, or --county"
                )
            districts = _validated_districts(args.district)
            start = parse_datetime(args.start)
            end = parse_datetime(args.end, end_of_day=True)
            granularity = args.granularity or "5min"
        plan = FetchPlan(
            districts=tuple(sorted(districts)),
            start=start,
            end=end,
            region=region,
            output=args.output,
            keep_raw=args.keep_raw,
            granularity=granularity,
            allow_empty=args.allow_empty,
            profile=args.profile,
            with_road_network=args.with_road_network,
        )
        manifest = run(execute(plan, args.state))
        print(f"Completed: {manifest}")
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
