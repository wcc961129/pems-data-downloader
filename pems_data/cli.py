import argparse
import sys
from pathlib import Path

from .browser import authorize, run
from .fetch import execute
from .models import FetchPlan, Region
from .planner import SUPPORTED_DISTRICTS, parse_datetime
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pems-data")
    parser.add_argument(
        "--state",
        type=Path,
        default=Path(".pems/storage-state.json"),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    auth = subparsers.add_parser("auth")
    auth.add_argument("--timeout-seconds", type=int, default=180)

    subparsers.add_parser("profiles")

    fetch = subparsers.add_parser("fetch")
    fetch.add_argument("--profile", choices=sorted(PROFILES))
    fetch.add_argument("--start")
    fetch.add_argument("--end")
    fetch.add_argument("--district", action="append")
    fetch.add_argument("--bbox")
    fetch.add_argument("--station-id", action="append")
    fetch.add_argument("--freeway", action="append")
    fetch.add_argument("--direction", action="append")
    fetch.add_argument("--lane-type", action="append")
    fetch.add_argument("--county", action="append")
    fetch.add_argument("--output", type=Path, required=True)
    fetch.add_argument("--keep-raw", action="store_true")
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
            profile = get_profile(args.profile)
            districts = (profile.district,)
            start = parse_datetime(profile.start)
            end = parse_datetime(profile.end, end_of_day=True)
            region = Region(station_ids=frozenset(profile.station_ids))
        else:
            if not args.start or not args.end:
                parser.error("fetch requires --start and --end unless --profile is used")
            stations = _csv_ints(args.station_id)
            bbox = _bbox(args.bbox)
            if not stations and not bbox and not any(
                (args.freeway, args.direction, args.lane_type, args.county)
            ):
                parser.error(
                    "fetch requires at least one region selector: --bbox, --station-id, "
                    "--freeway, --direction, --lane-type, or --county"
                )
            districts = tuple(_csv_ints(args.district)) or SUPPORTED_DISTRICTS
            start = parse_datetime(args.start)
            end = parse_datetime(args.end, end_of_day=True)
            region = Region(
                station_ids=stations,
                bbox=bbox,
                freeways=_csv_ints(args.freeway),
                directions=_csv_strings(args.direction),
                lane_types=_csv_strings(args.lane_type),
                counties=_csv_ints(args.county),
            )
        unsupported = sorted(set(districts) - set(SUPPORTED_DISTRICTS))
        if unsupported:
            raise ValueError(f"Unsupported PeMS districts: {unsupported}")
        plan = FetchPlan(
            districts=tuple(sorted(districts)),
            start=start,
            end=end,
            region=region,
            output=args.output,
            keep_raw=args.keep_raw,
            profile=args.profile,
        )
        manifest = run(execute(plan, args.state))
        print(f"Completed: {manifest}")
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
