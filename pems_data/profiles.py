from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchProfile:
    name: str
    title: str
    district: int
    start: str
    end: str
    station_ids: tuple[int, ...]
    paper_url: str
    code_url: str
    doi: str


GE_GAN_D7_2014 = ResearchProfile(
    name="ge-gan-d7-2014",
    title="GE-GAN Caltrans District 7 source period",
    district=7,
    start="2014-05-01",
    end="2014-06-30",
    station_ids=(
        767838,
        773656,
        760074,
        760080,
        716414,
        760101,
        760112,
        716419,
        716421,
        716424,
        765476,
        760167,
        716427,
        716431,
        716433,
        760187,
        760196,
        716440,
        760226,
        760236,
        716449,
        718155,
        716453,
    ),
    paper_url="https://doi.org/10.1016/j.trc.2020.102635",
    code_url="https://github.com/wcc961129/GE-GAN",
    doi="10.1016/j.trc.2020.102635",
)

PROFILES = {GE_GAN_D7_2014.name: GE_GAN_D7_2014}


def get_profile(name: str) -> ResearchProfile:
    try:
        return PROFILES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown research profile: {name}") from exc

