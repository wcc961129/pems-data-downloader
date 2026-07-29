import pytest

from pems_data.cli import build_parser, main


def test_top_level_help_describes_discovery_commands():
    help_text = build_parser().format_help()
    assert "latest" in help_text
    assert "stations" in help_text
    assert "doctor" in help_text


def test_fetch_help_describes_units_and_selector_semantics():
    parser = build_parser()
    fetch_parser = parser._subparsers._group_actions[0].choices["fetch"]
    help_text = fetch_parser.format_help()
    assert "inclusive ISO date/time" in help_text
    assert "logical AND" in help_text
    assert "--allow-empty" in help_text


def test_fetch_requires_explicit_district(tmp_path):
    with pytest.raises(SystemExit):
        main(
            [
                "fetch",
                "--start",
                "2026-07-27T00:00",
                "--end",
                "2026-07-27T00:10",
                "--station-id",
                "760063",
                "--output",
                str(tmp_path / "output"),
            ]
        )


def test_fetch_rejects_invalid_direction_before_network(tmp_path, capsys):
    result = main(
        [
            "fetch",
            "--district",
            "7",
            "--start",
            "2026-07-27T00:00",
            "--end",
            "2026-07-27T00:10",
            "--direction",
            "X",
            "--output",
            str(tmp_path / "output"),
        ]
    )
    assert result == 2
    assert "Direction must be N, S, E, or W" in capsys.readouterr().err
