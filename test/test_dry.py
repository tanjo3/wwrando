import dataclasses
import io
import os
import pytest
from wwrando import make_argparser
from randomizer import WWRandomizer, Plando
import tweaks
from randomizers.entrances import ZoneEntrance
from randomizers.hints import HintsRandomizer
from options.wwrando_options import Options, TrickDifficulty, KeyLunacyMode
from enum import StrEnum
from test_helpers import *

def dry_rando_with_options(options, plando: Plando | None = None) -> WWRandomizer:
  args = make_argparser().parse_args(args=["--dry"])
  rando_kwargs = {
    "seed": "pytestseed",
    "clean_iso_path": None,
    "randomized_output_folder": os.environ["WW_RANDO_OUTPUT_DIR"],
    "options": options,
    "plando": plando or make_test_plando(options),
    "cmd_line_args": args,
  }
  return WWRandomizer(**rando_kwargs)

def test_dry_default_options():
  options = Options()
  rando = dry_rando_with_options(options)
  rando.randomize_all()

def test_dry_all_options():
  options = Options()
  enable_all_options(options)
  rando = dry_rando_with_options(options)
  rando.randomize_all()

@pytest.mark.skip(reason="The APWorld places items and entrances on the Archipelago build, so this code never runs here.")
def test_tricks_precise_no_obscure():
  options = Options()
  enable_all_progression_location_options(options)
  options.logic_obscurity = TrickDifficulty.NONE
  options.logic_precision = TrickDifficulty.VERY_HARD
  rando = dry_rando_with_options(options)
  rando.randomize_all()

@pytest.mark.skip(reason="The APWorld places items and entrances on the Archipelago build, so this code never runs here.")
def test_tricks_obscure_no_precise():
  options = Options()
  enable_all_progression_location_options(options)
  options.logic_obscurity = TrickDifficulty.VERY_HARD
  options.logic_precision = TrickDifficulty.NONE
  rando = dry_rando_with_options(options)
  rando.randomize_all()

def test_entrance_rando_enables():
  options = Options()
  options.randomize_dungeon_entrances = True
  rando = dry_rando_with_options(options)
  assert rando.entrances.is_enabled()

@pytest.mark.skip(reason="The APWorld places items and entrances on the Archipelago build, so this code never runs here.")
def test_regression_entrance_inner_rando():
  # https://github.com/LagoLunatic/wwrando/pull/390
  
  options = Options()
  disable_all_progression_location_options(options)
  options.progression_dungeons = True
  options.progression_dungeon_secrets = True
  options.progression_free_gifts = True
  options.progression_misc = True
  
  options.randomize_secret_cave_inner_entrances = True
  
  options.randomize_boss_entrances = True
  options.required_bosses = True
  options.num_required_bosses = 3
  
  rando = dry_rando_with_options(options)
  rando.randomize_all()

def test_trick_logic_checks():
  options = Options()
  options.logic_obscurity = TrickDifficulty.HARD
  options.logic_precision = TrickDifficulty.NORMAL
  rando = dry_rando_with_options(options)
  assert rando.logic.check_requirement_met("Obscure 2")
  assert not rando.logic.check_requirement_met("Obscure 3")
  assert rando.logic.check_requirement_met("Precise 1")
  assert not rando.logic.check_requirement_met("Precise 2")

def test_parse_string_option_to_enum():
  options = Options()
  options.logic_precision = "Normal" # pyright: ignore [reportAttributeAccessIssue]
  rando = dry_rando_with_options(options)
  assert isinstance(rando.options.logic_precision, StrEnum)

def test_convert_options_to_dict_and_back():
  default_options = Options()
  orig_options = Options(progression_dungeons=False, num_required_bosses=2, logic_precision=TrickDifficulty.HARD)
  options_dict = orig_options.dict()
  converted_options = Options(**options_dict)
  assert converted_options == orig_options
  assert orig_options != default_options
  assert converted_options != default_options

@pytest.mark.skip(reason="The Archipelago build doesn't use permalinks, and they don't support KeyLunacyMode options.")
def test_convert_options_to_permalink_and_back():
  default_options = Options()
  orig_options = Options(progression_dungeons=False, num_required_bosses=2, logic_precision=TrickDifficulty.HARD)
  orig_seed = "test"
  permalink = WWRandomizer.encode_permalink(orig_seed, orig_options)
  converted_seed, converted_options = WWRandomizer.decode_permalink(permalink)
  assert converted_seed == orig_seed
  assert converted_options == orig_options
  assert orig_options != default_options
  assert converted_options != default_options

#region Archipelago
BIG_OCTO_FAIRY = "Two-Eye Reef - Big Octo Great Fairy"
FIRST_ROOM = "Dragon Roost Cavern - First Room"
ROCK_SPIRE_500 = "Rock Spire Isle - Beedle's Special Shop Ship - 500 Rupee Item"
ROCK_SPIRE_SLOTS = {
  "Rock Spire Isle - Beedle's Special Shop Ship - 500 Rupee Item": "Green Rupee",
  "Rock Spire Isle - Beedle's Special Shop Ship - 950 Rupee Item": "Yellow Rupee",
  "Rock Spire Isle - Beedle's Special Shop Ship - 900 Rupee Item": "Blue Rupee",
}

def randomized(options: Options, plando: Plando | None = None) -> WWRandomizer:
  rando = dry_rando_with_options(options, plando)
  rando.randomize_all()
  return rando

@pytest.mark.parametrize("item_info, expected", [
  (own_item("Bombs"), "Bombs"),
  ({"player": 2, "name": "Bombs", "game": "The Wind Waker", "classification": "progression"}, "Bombs"),
  (foreign_item(), "Archipelago Item"),
  (nothing_item(), "Red Rupee"),
], ids=["own item", "other player's item from this game", "other game", "empty location"])
def test_item_from_the_file_is_placed(item_info, expected):
  options = Options()
  plando = make_test_plando(options)
  plando.locations[FIRST_ROOM] = item_info
  rando = randomized(options, plando)
  assert rando.logic.done_item_locations[FIRST_ROOM] == expected

def test_location_missing_from_the_file_gets_the_joke_rupee():
  rando = randomized(Options())
  assert "Outset Island - Savage Labyrinth - Floor 30" not in rando.plando.locations
  assert rando.logic.done_item_locations["Outset Island - Savage Labyrinth - Floor 30"] == "Yellow Rupee (Joke Message)"

@pytest.mark.parametrize("location_name, expected", ROCK_SPIRE_SLOTS.items(), ids=["500 rupee slot", "950 rupee slot", "900 rupee slot"])
def test_missing_rock_spire_slots_sell_distinct_rupees(location_name, expected):
  # Beedle uses the item ID to tell the slots apart, so these can't all be the joke rupee.
  options = Options()
  options.progression_expensive_purchases = False
  rando = randomized(options)
  assert location_name not in rando.plando.locations
  assert rando.logic.done_item_locations[location_name] == expected

@pytest.mark.parametrize("item_name, item_info, expected", [
  ("DRC Small Key", own_item("DRC Small Key"), 1),
  ("DRC Big Key", own_item("DRC Big Key"), 1),
  ("DRC Small Key", {"player": 2, "name": "DRC Small Key", "game": "The Wind Waker", "classification": "progression"}, 1),
  ("Some Key", foreign_item("Some Key"), 2),
  ("Deku Leaf", own_item("Deku Leaf"), 2),
  ("Archipelago Item", foreign_item("Some Trap", "trap"), 2),
  ("Red Rupee", own_item("Red Rupee", "useful"), 0),
  ("Red Rupee", own_item("Red Rupee", "filler"), 0),
], ids=["small key", "big key", "other player's key", "other game's item named like a key", "progression", "trap", "useful", "filler"])
def test_chest_type_matches_contents(item_name, item_info, expected):
  rando = dry_rando_with_options(Options())
  assert rando.items.get_ctmc_chest_type_for_item(item_name, item_info) == expected

@pytest.mark.parametrize("mode, expected", [
  (KeyLunacyMode.START_WITH, True),
  (KeyLunacyMode.VANILLA, False),
  (KeyLunacyMode.DUNGEON, False),
  (KeyLunacyMode.ANY_DUNGEON, True),
  (KeyLunacyMode.LOCAL, True),
  (KeyLunacyMode.KEYLUNACY, True),
], ids=lambda value: value.name if isinstance(value, KeyLunacyMode) else str(value))
def test_own_keys_are_only_hinted_outside_their_dungeon(mode, expected):
  options = Options()
  options.randomize_smallkeys = mode
  options.randomize_bigkeys = mode
  rando = dry_rando_with_options(options)
  assert rando.hints.check_item_can_be_hinted_at(own_item("DRC Small Key")) == expected
  assert rando.hints.check_item_can_be_hinted_at(own_item("DRC Big Key")) == expected

@pytest.mark.parametrize("small_key_mode, big_key_mode, small_key_hinted, big_key_hinted", [
  (KeyLunacyMode.DUNGEON, KeyLunacyMode.KEYLUNACY, False, True),
  (KeyLunacyMode.KEYLUNACY, KeyLunacyMode.DUNGEON, True, False),
], ids=["only big keys outside", "only small keys outside"])
def test_small_and_big_key_modes_are_independent(small_key_mode, big_key_mode, small_key_hinted, big_key_hinted):
  options = Options()
  options.randomize_smallkeys = small_key_mode
  options.randomize_bigkeys = big_key_mode
  rando = dry_rando_with_options(options)
  assert rando.hints.check_item_can_be_hinted_at(own_item("DRC Small Key")) == small_key_hinted
  assert rando.hints.check_item_can_be_hinted_at(own_item("DRC Big Key")) == big_key_hinted

@pytest.mark.parametrize("item_info, expected", [
  (own_item("Bombs"), True),
  (foreign_item(), True),
  ({"player": 1, "name": "DRC Small Key", "game": "Other Game", "classification": "progression"}, True),
  ({"player": 2, "name": "DRC Small Key", "game": "The Wind Waker", "classification": "progression"}, True),
  (own_item("Bombs", "useful"), False),
  (own_item("Green Rupee", "filler"), False),
  (foreign_item("Lantern", "useful"), False),
  (foreign_item("Some Trap", "trap"), False),
  (nothing_item(), False),
], ids=["progression", "other game", "other game's item named like a key", "other player's key", "useful", "filler", "other game's useful", "trap", "empty location"])
def test_only_progression_items_are_hinted(item_info, expected):
  options = Options()
  options.randomize_smallkeys = KeyLunacyMode.DUNGEON
  options.randomize_bigkeys = KeyLunacyMode.DUNGEON
  rando = dry_rando_with_options(options)
  assert rando.hints.check_item_can_be_hinted_at(item_info) == expected

def test_big_octo_fairy_does_not_hint_at_her_own_item():
  options = Options()
  options.progression_great_fairies = True
  options.progression_big_octos_gunboats = True
  plando = make_filler_plando(options)
  plando.locations[BIG_OCTO_FAIRY] = own_item("Bombs")
  plando.locations[FIRST_ROOM] = own_item("Deku Leaf")
  rando = randomized(options, plando)
  rando.hints.reset_rng()
  hinted_items = {rando.hints.generate_octo_fairy_hint().reward["name"] for _ in range(20)}
  assert hinted_items == {"Deku Leaf"}

def test_big_octo_fairy_has_no_hint_without_a_progression_item():
  options = Options()
  rando = randomized(options, make_filler_plando(options))
  assert rando.hints.octo_fairy_hint is None

def test_big_octo_fairy_has_no_hint_when_she_holds_the_only_progression_item():
  options = Options()
  options.progression_great_fairies = True
  options.progression_big_octos_gunboats = True
  plando = make_filler_plando(options)
  plando.locations[BIG_OCTO_FAIRY] = own_item("Bombs")
  rando = randomized(options, plando)
  assert rando.hints.octo_fairy_hint is None

@pytest.mark.parametrize("item_info, expected", [
  (foreign_item("Lantern"), "P2's Lantern"),
  (foreign_item("DRC Small Key"), "P2's DRC Small Key"),
  ({"player": 2, "name": "DRC Small Key", "game": "The Wind Waker", "classification": "progression"}, "P2's Dragon Roost Cavern small key"),
  (own_item("DRC Small Key"), "your Dragon Roost Cavern small key"),
  (own_item("DRC Big Key"), "your Dragon Roost Cavern Big Key"),
  (own_item("DRC Dungeon Map"), "your Dragon Roost Cavern Dungeon Map"),
  (own_item("DRC Compass"), "your Dragon Roost Cavern Compass"),
], ids=["other game", "other game's item named like a key", "other player's key", "small key", "big key", "map", "compass"])
def test_hinted_item_name_says_whose_it_is(item_info, expected):
  assert HintsRandomizer.get_formatted_item_name(item_info, 1) == expected

@pytest.mark.parametrize("location_name, item_info, expected_shop_name, expected_letter_name", [
  (ROCK_SPIRE_500, own_item("Deku Leaf"), "Deku Leaf", "your Deku Leaf"),
  (ROCK_SPIRE_500, foreign_item("Lantern"), "P2's Lantern", "P2's Lantern"),
  (ROCK_SPIRE_500, {"player": 2, "name": "Bombs", "game": "The Wind Waker", "classification": "progression"}, "P2's Bombs", "P2's Bombs"),
  (ROCK_SPIRE_500, nothing_item(), "Red Rupee", "a Red Rupee"),
  (ROCK_SPIRE_500, None, "Green Rupee", "a Green Rupee"),
  ("Rock Spire Isle - Beedle's Special Shop Ship - 950 Rupee Item", None, "Yellow Rupee", "a Yellow Rupee"),
  ("Rock Spire Isle - Beedle's Special Shop Ship - 900 Rupee Item", None, "Blue Rupee", "a Blue Rupee"),
  ("Windfall Island - 5 Rupee Auction", None, "Yellow Rupee", "a Yellow Rupee"),
], ids=["own item", "other game", "other player's item from this game", "empty location", "unrandomized 500 rupee slot", "unrandomized 950 rupee slot", "unrandomized 900 rupee slot", "unrandomized joke rupee"])
def test_shop_and_letter_name_the_placed_item(location_name, item_info, expected_shop_name, expected_letter_name):
  options = Options()
  plando = make_test_plando(options)
  plando.locations.pop(location_name, None)
  if item_info is not None:
    plando.locations[location_name] = item_info
  rando = randomized(options, plando)
  assert tweaks.get_shop_item_name(rando, location_name) == expected_shop_name
  assert tweaks.get_letter_item_name(rando, location_name) == expected_letter_name

@pytest.mark.parametrize("item_name, expected", [
  ("x" * 38, "P2's " + "x" * 38),
  ("x" * 39, "P2's " + "x" * 38),
], ids=["longest that fits", "too long"])
def test_auction_item_name_fits_in_the_game_buffer(item_name, expected):
  options = Options()
  plando = make_test_plando(options)
  plando.locations["Windfall Island - 5 Rupee Auction"] = foreign_item(item_name)
  rando = randomized(options, plando)
  assert tweaks.get_auction_item_name(rando, "Windfall Island - 5 Rupee Auction") == expected

@pytest.mark.parametrize("seed, player_name, expected_name", [
  ("AP_12345678901234567890_P1", "Player1", "Player1"),
  ("AP_12345678901234567890_P1", "Zoë", "Zoe"),
  ("AP_12345678901234567890_P1", "😀", "?"),
  ("AP_12345678901234567890_P1", "あ" * 16, "あ" * 15),
  ("AP_12345678901234567890_P100", "あ" * 16, "あ" * 14),
  ("AP_12345678901234567890_P1", "a" + "あ" * 15, "a" + "あ" * 15),
  ("AP_12345678901234567890_P1", "ﬃ" * 16, "ffi" * 10 + "f"),
], ids=["plain", "accent", "not in shift jis", "double-byte", "double-byte with a longer seed", "exact fit", "expands when cleaned"])
def test_banner_game_name_fits_without_splitting_a_character(seed, player_name, expected_name):
  game_name = tweaks.get_banner_game_name(seed, player_name)
  assert game_name == f"TWW {seed} ({expected_name})"

@pytest.mark.parametrize("player_name", ["Player1", "😀" * 16], ids=["plain", "longest possible"])
def test_client_reads_back_the_slot_name_it_logs_in_with(player_name):
  data = io.BytesIO()
  tweaks.write_slot_name(data, 0, player_name, 0x40)
  assert len(data.getvalue()) == 0x40
  assert data.getvalue().split(b"\0", 1)[0].decode() == player_name

def test_slot_name_too_long_for_its_space_is_refused():
  data = io.BytesIO()
  with pytest.raises(Exception, match="too long"):
    tweaks.write_slot_name(data, 0, "😀" * 17, 0x40)
  assert data.getvalue() == b""

def test_savage_labyrinth_hint_uses_the_item_from_the_file():
  options = Options()
  options.progression_savage_labyrinth = True
  plando = make_test_plando(options)
  plando.locations["Outset Island - Savage Labyrinth - Floor 30"] = foreign_item("Lantern")
  plando.locations["Outset Island - Savage Labyrinth - Floor 50"] = own_item("Bombs")
  rando = randomized(options, plando)
  assert rando.hints.floor_30_hint.reward == foreign_item("Lantern")
  assert rando.hints.floor_50_hint.reward == own_item("Bombs")

@pytest.mark.parametrize("item_info", [nothing_item(), foreign_item("Some Trap", "trap")], ids=["empty location", "trap"])
def test_savage_labyrinth_does_not_reveal_an_empty_location_or_a_trap(item_info):
  options = Options()
  options.progression_savage_labyrinth = True
  plando = make_test_plando(options)
  plando.locations["Outset Island - Savage Labyrinth - Floor 30"] = item_info
  plando.locations["Outset Island - Savage Labyrinth - Floor 50"] = foreign_item("Nothing", "filler")
  rando = randomized(options, plando)
  assert rando.hints.floor_30_hint is None
  assert rando.hints.floor_50_hint.reward == foreign_item("Nothing", "filler")

def test_savage_labyrinth_has_no_hint_when_missing_from_the_file():
  rando = randomized(Options())
  assert rando.hints.floor_30_hint is None
  assert rando.hints.floor_50_hint is None

def test_required_bosses_come_from_the_file():
  options = Options()
  options.required_bosses = True
  options.num_required_bosses = 2
  plando = dataclasses.replace(make_test_plando(options), required_bosses=[
    "Forbidden Woods - Kalle Demos Heart Container",
    "Wind Temple - Molgera Heart Container",
  ])
  rando = randomized(options, plando)
  assert sorted(rando.boss_reqs.required_dungeons) == ["Forbidden Woods", "Wind Temple"]
  assert sorted(rando.boss_reqs.required_bosses) == ["Kalle Demos", "Molgera"]
  assert "Dragon Roost Cavern" in rando.boss_reqs.banned_dungeons
  assert rando.logic.macros["Can Defeat All Required Bosses"] == [
    'Can Access Item Location "Forbidden Woods - Kalle Demos Heart Container"',
    "&",
    'Can Access Item Location "Wind Temple - Molgera Heart Container"',
  ]

@pytest.mark.parametrize("required_bosses", [
  ["Forbidden Woods - Kalle Demos Heart Container"],
  ["Forbidden Woods - Kalle Demos Heart Container", "Wind Temple - Molgera Heart Container", "Earth Temple - Jalhalla Heart Container"],
  ["Forbidden Woods - Kalle Demos Heart Container", "Forbidden Woods - Kalle Demos Heart Container"],
  ["Forbidden Woods - Kalle Demos Heart Container", "Not A Boss"],
  ["Forbidden Woods - Kalle Demos Heart Container", "Wind Temple - Molgera Heart Container", "Forbidden Woods - Kalle Demos Heart Container"],
  ["Forbidden Woods - Kalle Demos Heart Container", "Wind Temple - Molgera Heart Container", "Not A Boss"],
], ids=["too few", "too many", "duplicate", "unknown location", "extra duplicate", "extra unknown location"])
def test_wrong_required_bosses_in_the_file_are_refused(required_bosses):
  options = Options()
  options.required_bosses = True
  options.num_required_bosses = 2
  plando = dataclasses.replace(make_test_plando(options), required_bosses=required_bosses)
  with pytest.raises(Exception, match="Expected 2 required bosses"):
    randomized(options, plando)

def test_error_log_is_written_even_though_other_logs_are_off(tmp_path):
  rando = dry_rando_with_options(Options())
  rando.logs_output_folder = str(tmp_path)
  rando.write_error_log("Failed in C:\\Users\\日本語")
  assert os.listdir(tmp_path) == ["WW Random pytestseed - Error Log.txt"]
  log = (tmp_path / "WW Random pytestseed - Error Log.txt").read_text(encoding="utf-8")
  assert "Seed: pytestseed\n" in log
  assert log.endswith("Failed in C:\\Users\\日本語")

def test_error_log_respects_the_no_logs_argument(tmp_path):
  args = make_argparser().parse_args(args=["--dry", "--nologs"])
  options = Options()
  rando = WWRandomizer("pytestseed", None, str(tmp_path), options, make_test_plando(options), cmd_line_args=args)
  rando.write_error_log("Some error")
  assert os.listdir(tmp_path) == []

def test_spoiler_logs_stay_off(tmp_path):
  rando = dry_rando_with_options(Options())
  rando.logs_output_folder = str(tmp_path)
  rando.randomize_all()
  rando.write_non_spoiler_log()
  rando.write_spoiler_log()
  assert os.listdir(tmp_path) == []

def test_charts_come_from_the_file():
  options = Options()
  options.randomize_charts = True
  plando = dataclasses.replace(make_test_plando(options), charts=list(range(2, 49+1)) + [1])
  rando = randomized(options, plando)
  assert rando.charts.island_number_to_chart_name[2] == "Treasure Chart 25" # Originally for island 1
  assert rando.charts.island_number_to_chart_name[1] == "Treasure Chart 33" # Originally for island 49

def test_entrances_come_from_the_file():
  options = Options()
  options.randomize_dungeon_entrances = True
  plando = make_test_plando(options)
  plando.entrances["Dungeon Entrance on Dragon Roost Island"] = "Forbidden Woods"
  plando.entrances["Dungeon Entrance in Forest Haven Sector"] = "Dragon Roost Cavern"
  rando = randomized(options, plando)
  zone_entrance = ZoneEntrance.all["Dungeon Entrance on Dragon Roost Island"]
  zone_exit = rando.entrances.done_entrances_to_exits[zone_entrance]
  assert zone_exit.unique_name == "Forbidden Woods"
  assert rando.entrances.done_exits_to_entrances[zone_exit] == zone_entrance

def test_logic_starts_with_only_the_sail_whatever_the_options():
  # The APWorld decides on starting items and sends them through the multiworld, not the patcher.
  options = Options()
  options.starting_gear = ["Telescope"]
  options.num_starting_triforce_shards = 4
  assert dry_rando_with_options(options).starting_items == ["Boat's Sail"]
#endregion
