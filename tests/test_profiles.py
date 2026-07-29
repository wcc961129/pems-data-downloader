from pems_data.profiles import GE_GAN_D7_2014, get_profile


def test_ge_gan_profile_matches_published_data_header():
    profile = get_profile("ge-gan-d7-2014")
    assert profile is GE_GAN_D7_2014
    assert profile.district == 7
    assert profile.start == "2014-05-01"
    assert profile.end == "2014-06-30"
    assert len(profile.station_ids) == 23
    assert profile.station_ids[0] == 767838
    assert profile.station_ids[-1] == 716453

