import dataclasses
import os
import pytest
from ruamel.yaml import YAML
from wwrando import make_argparser
from gclib import fs_helpers as fs
from randomizer import WWRandomizer, Plando
from randomizers.hints import Hint, HintType
from options.wwrando_options import Options, SwordMode
from wwrando_paths import ASM_PATH
from test_helpers import *
import customizer
import aptww

def rando_with_options(options, plando: Plando | None = None, output_folder: str | None = None) -> WWRandomizer:
  args = make_argparser().parse_args(args=[])
  rando_kwargs = {
    "seed": "pytestseed",
    "clean_iso_path": os.environ["WW_GZLE01_STRIPPED_PATH"],
    "randomized_output_folder": output_folder or os.environ["WW_RANDO_OUTPUT_DIR"],
    "options": options,
    "plando": plando or make_test_plando(options),
    "cmd_line_args": args,
  }
  os.makedirs(rando_kwargs["randomized_output_folder"], exist_ok=True)
  return WWRandomizer(**rando_kwargs)

def test_save_all_options():
  options = Options()
  enable_all_options(options)
  rando = rando_with_options(options)
  rando.randomize_all()

def test_save_customizer():
  options = Options()
  options.custom_player_model = "Link"
  options.custom_color_preset = "Dark Link"
  link_presets = customizer.get_model_metadata(options.custom_player_model).get("hero_color_presets")
  preset_colors = link_presets[options.custom_color_preset]
  options.custom_colors = preset_colors
  rando = rando_with_options(options)
  rando.randomize_all()

#region Archipelago
PLAYER_NAME = "Pla:y\te r\n?1"
LONGEST_PLAYER_NAME = "😀" * 16
UNUSUAL_ITEM_NAME = "AC/DC (...TM)"
LONG_ITEM_NAME = "Word " * 11 + "Word"
ITEM_COLOR = "\\{1A 06 FF 00 00 01}"
WHITE = "\\{1A 06 FF 00 00 00}"
SHIFTED_CHARTS = list(range(2, 49+1)) + [1]

def read_main_dol_symbol(rando: WWRandomizer, read_func, symbol_name: str, *args):
  return rando.dol.read_data(read_func, rando.main_custom_symbols[symbol_name], *args)

def is_swordless_patch_applied(rando: WWRandomizer) -> bool:
  # Checks the patch's edits to Phantom Ganon, since that file exists whether or not the patch was applied.
  with open(os.path.join(ASM_PATH, "patch_diffs", "swordless_diff.txt")) as f:
    patch = YAML(typ="safe").load(f)
  rel = rando.get_rel("files/rels/d_a_fganon.rel")
  return all(
    rel.read_data(fs.read_bytes, offset, len(edit["Data"])) == bytes(edit["Data"])
    for offset, edit in patch["files/rels/d_a_fganon.rel"].items()
  )

def read_fairy_bow_check(rando: WWRandomizer) -> int:
  # The branch that only lets the Big Octo Great Fairy give her hint if you have the Hero's Bow.
  return rando.get_rel("files/rels/d_a_bigelf.rel").read_data(fs.read_u32, 0x22A4)

def restore_messages_after_test(monkeypatch, rando: WWRandomizer, *message_ids):
  for message_id in message_ids:
    message = rando.bmg.messages_by_id[message_id]
    monkeypatch.setattr(message, "string", message.string)

def read_unwrapped_message(rando: WWRandomizer, message_id: int) -> str:
  return rando.bmg.messages_by_id[message_id].string.replace("\n", " ")

@pytest.fixture(scope="module")
def saved_rando(tmp_path_factory):
  options = Options()
  plando = dataclasses.replace(make_test_plando(options), name=PLAYER_NAME, charts=SHIFTED_CHARTS)
  rando = rando_with_options(options, plando, str(tmp_path_factory.mktemp("default")))
  rando.randomize_all()
  return rando

@pytest.fixture(scope="module")
def swords_optional_rando(tmp_path_factory):
  options = Options()
  options.sword_mode = SwordMode.SWORDS_OPTIONAL
  rando = rando_with_options(options, output_folder=str(tmp_path_factory.mktemp("swords_optional")))
  rando.randomize_all()
  return rando

@pytest.fixture(scope="module")
def unusual_file_rando(tmp_path_factory):
  options = Options()
  options.progression_savage_labyrinth = True
  plando = make_filler_plando(options)
  unusual_item = foreign_item(aptww.sanitize_foreign_item_name("AC\\DC {…™}"), "filler")
  plando.locations["Outset Island - Savage Labyrinth - Floor 30"] = nothing_item()
  plando.locations["Outset Island - Savage Labyrinth - Floor 50"] = unusual_item
  plando.locations.update({
    "The Great Sea - Beedle's Shop Ship - 20 Rupee Item": unusual_item,
    "Rock Spire Isle - Beedle's Special Shop Ship - 950 Rupee Item": own_item("Deku Leaf", "useful"),
    "Rock Spire Isle - Beedle's Special Shop Ship - 900 Rupee Item": nothing_item(),
    "Windfall Island - 40 Rupee Auction": nothing_item(),
    "Windfall Island - 60 Rupee Auction": own_item("Bombs", "useful"),
    "Windfall Island - 80 Rupee Auction": foreign_item(LONG_ITEM_NAME, "filler"),
    "Windfall Island - Battlesquid - First Prize": foreign_item(LONG_ITEM_NAME, "filler"),
  })
  for location_name in ["Rock Spire Isle - Beedle's Special Shop Ship - 500 Rupee Item", "Windfall Island - 5 Rupee Auction", "Windfall Island - Battlesquid - Second Prize"]:
    plando.locations.pop(location_name, None)
  plando = dataclasses.replace(plando, name=LONGEST_PLAYER_NAME)
  rando = rando_with_options(options, plando, str(tmp_path_factory.mktemp("unusual_file")))
  rando.randomize_all()
  return rando

def test_big_octo_fairy_gives_a_hint(saved_rando):
  assert read_fairy_bow_check(saved_rando) == 0x60000000 # nop
  assert "you will find an item" in read_unwrapped_message(saved_rando, 12015)
  assert "which may help you on your quest" in read_unwrapped_message(saved_rando, 12016)

def test_big_octo_fairy_stays_vanilla_without_a_hint(unusual_file_rando):
  assert read_fairy_bow_check(unusual_file_rando) == 0x4082000C # bne
  assert "place where the wind god guides you" in read_unwrapped_message(unusual_file_rando, 12015)

def test_savage_labyrinth_tablet_does_not_name_an_empty_location(unusual_file_rando):
  tablet = read_unwrapped_message(unusual_file_rando, 837)
  assert tablet.endswith(f"the way to challenge and {ITEM_COLOR}P2's {UNUSUAL_ITEM_NAME}{WHITE} await.")

@pytest.mark.parametrize("floor_30_reward, floor_50_reward, expected", [
  (own_item("Bombs"), foreign_item("Lantern"), f"{ITEM_COLOR}your Bombs{WHITE} and {ITEM_COLOR}P2's Lantern{WHITE} await."),
  (foreign_item("Lantern"), own_item("Bombs"), f"{ITEM_COLOR}P2's Lantern{WHITE} and {ITEM_COLOR}your Bombs{WHITE} await."),
  (own_item("Bombs"), None, f"{ITEM_COLOR}your Bombs{WHITE} and challenge await."),
  (None, own_item("Bombs"), f"challenge and {ITEM_COLOR}your Bombs{WHITE} await."),
], ids=["own then other", "other then own", "own then empty", "empty then own"])
def test_savage_labyrinth_tablet_says_whose_items_wait(saved_rando, monkeypatch, floor_30_reward, floor_50_reward, expected):
  restore_messages_after_test(monkeypatch, saved_rando, 837)
  floor_30_hint = floor_30_reward and Hint(HintType.FIXED_LOCATION, "Floor 30", floor_30_reward, None)
  floor_50_hint = floor_50_reward and Hint(HintType.FIXED_LOCATION, "Floor 50", floor_50_reward, None)
  saved_rando.hints.update_savage_labyrinth_hint_tablet(floor_30_hint, floor_50_hint, False)
  assert read_unwrapped_message(saved_rando, 837).endswith(f"the way to {expected}")

def test_unusual_item_name_is_written_to_the_message_as_plain_text(unusual_file_rando):
  message = unusual_file_rando.bmg.messages_by_id[3906]
  written = fs.read_bytes(unusual_file_rando.bmg.dat1.data, 8 + message.string_offset, message.encoded_string_length)
  assert written == b"\x1A\x06\xFF\x00\x00\x01P2's AC/DC (...TM)  20 Rupees\x1A\x06\xFF\x00\x00\x00\x00"

@pytest.mark.parametrize("message_id, expected_text", [
  (3906, f"{ITEM_COLOR}P2's {UNUSUAL_ITEM_NAME}  20 Rupees"),
  (3909, f"P2's {UNUSUAL_ITEM_NAME}   20 Rupees"),
  (12106, f"{ITEM_COLOR}Green Rupee  500 Rupees"),
  (12109, f"This {ITEM_COLOR}Green Rupee{WHITE} is a mere"),
  (12107, f"{ITEM_COLOR}Deku Leaf  950 Rupees"),
  (12110, f"This {ITEM_COLOR}Deku Leaf{WHITE} is only"),
  (12108, f"{ITEM_COLOR}Red Rupee  900 Rupees"),
  (12111, f"This {ITEM_COLOR}Red Rupee {WHITE}is just"),
  (7441, f"{ITEM_COLOR}Yellow Rupee"),
  (7440, f"{ITEM_COLOR}Red Rupee"),
  (7442, f"{ITEM_COLOR}Bombs"),
  (7520, f"Please take this {ITEM_COLOR}P2's {LONG_ITEM_NAME}{WHITE} as a sign"),
  (7521, f"Please accept this {ITEM_COLOR}Yellow Rupee{WHITE}!"),
], ids=lambda value: str(value) if isinstance(value, int) else "")
def test_item_names_reach_the_shop_auction_and_battlesquid_text(unusual_file_rando, message_id, expected_text):
  assert expected_text in read_unwrapped_message(unusual_file_rando, message_id)

def test_long_auction_item_name_is_shortened(unusual_file_rando):
  assert read_unwrapped_message(unusual_file_rando, 7443) == f"{ITEM_COLOR}P2's Word Word Word Word Word Word Word Wor"

def test_rock_spire_letter_names_the_placed_items(unusual_file_rando):
  letter = " ".join(unusual_file_rando.bmg.messages_by_id[3325].string.split())
  assert f"Do you have need of {ITEM_COLOR}a Green Rupee{WHITE}, {ITEM_COLOR}your Deku Leaf{WHITE}, or {ITEM_COLOR}a Red Rupee{WHITE}?" in letter

@pytest.mark.parametrize("reward, expected_item, expected_owner", [
  (own_item("Bombs"), "Your Bombs", "When you find you have need"),
  (foreign_item("Lantern"), "P2's Lantern", "When they find they have need"),
], ids=["own item", "other player's item"])
def test_big_octo_fairy_speaks_to_the_item_owner(saved_rando, monkeypatch, reward, expected_item, expected_owner):
  restore_messages_after_test(monkeypatch, saved_rando, 12015, 12016, 12017)
  hint = Hint(HintType.ITEM, "Dragon Roost Island", reward, None)
  saved_rando.hints.update_big_octo_great_fairy_item_name_hint(hint, False)
  assert expected_item in read_unwrapped_message(saved_rando, 12016)
  assert expected_owner in read_unwrapped_message(saved_rando, 12017)

def test_slot_name_is_written_for_the_client(saved_rando):
  slot_name = read_main_dol_symbol(saved_rando, fs.read_bytes, "archipelago_slot_name", 0x40)
  assert slot_name == b"Pla:y\te r\n?1" + b"\0" * 52

def test_banner_names_the_seed_and_player(saved_rando):
  banner = fs.read_bytes(saved_rando.get_raw_file("files/opening.bnr"), 0x1860, 0x40)
  assert banner == b"TWW pytestseed (Pla:y\te r\n?1)".ljust(0x40, b"\0")

def test_longest_possible_player_name_is_written_in_full(unusual_file_rando):
  assert read_main_dol_symbol(unusual_file_rando, fs.read_bytes, "archipelago_slot_name", 0x40) == LONGEST_PLAYER_NAME.encode()
  assert os.listdir(unusual_file_rando.randomized_output_folder) == [f"TWW pytestseed ({LONGEST_PLAYER_NAME}).iso"]

def test_charts_are_written_for_the_client(saved_rando):
  address = saved_rando.main_custom_symbols["archipelago_charts_mapping"]
  written_charts = [saved_rando.dol.read_data(fs.read_u16, address + offset * 2) for offset in range(49)]
  assert written_charts == SHIFTED_CHARTS

def test_iso_is_named_after_the_player_without_reserved_or_control_characters(saved_rando):
  assert os.listdir(saved_rando.randomized_output_folder) == ["TWW pytestseed (Playe r1).iso"]

def test_start_with_sword_uses_the_normal_game(saved_rando):
  assert read_main_dol_symbol(saved_rando, fs.read_u8, "sword_mode") == 1
  assert not is_swordless_patch_applied(saved_rando)

def test_swords_optional_sets_the_sword_mode_variable(swords_optional_rando):
  assert read_main_dol_symbol(swords_optional_rando, fs.read_u8, "sword_mode") == 2

def test_swords_optional_applies_the_swordless_patch(swords_optional_rando):
  assert is_swordless_patch_applied(swords_optional_rando)

def test_swords_optional_changes_the_hint_about_the_master_sword(swords_optional_rando):
  message = swords_optional_rando.bmg.messages_by_id[1128].string
  assert "even if you have the" in message
  assert "you may not have the" not in message
#endregion
