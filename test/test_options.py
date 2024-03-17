from options.wwrando_options import Options
from randomizers.settings import DEFAULT_WEIGHTS as RSL_WEIGHTS


def test_random_settings_covers_all_options():
    programmatic_rs_options = {
        "starting_gear",
        "hoho_hints",
        "korl_hints",
        "fishmen_hints",
        "stone_tablet_hints",
        "randomized_gear",
    }
    synthetic_rs_options = {"num_starting_items", "start_with_maps_and_compasses", "hint_placement"}
    rs_togglable = {opt.name for opt in Options.all if not opt.random_settings_togglable}

    missing_options = rs_togglable - programmatic_rs_options - set(RSL_WEIGHTS.keys())
    assert len(missing_options) == 0

    unknown_options = set(RSL_WEIGHTS.keys()) - rs_togglable - synthetic_rs_options
    assert len(unknown_options) == 0
