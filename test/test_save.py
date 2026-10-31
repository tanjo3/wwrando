import dataclasses
import os
import pytest
from ruamel.yaml import YAML
from wwrando import make_argparser
from gclib import fs_helpers as fs
from randomizer import WWRandomizer, Plando
from options.wwrando_options import Options, SwordMode
from wwrando_paths import ASM_PATH
from test_helpers import *
import customizer

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
PLAYER_NAME = "Pla:yer?1"
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

def test_slot_name_is_written_for_the_client(saved_rando):
  slot_name = read_main_dol_symbol(saved_rando, fs.read_bytes, "archipelago_slot_name", 0x40)
  assert slot_name == b"Pla:yer?1" + b"\0" * 55

def test_charts_are_written_for_the_client(saved_rando):
  address = saved_rando.main_custom_symbols["archipelago_charts_mapping"]
  written_charts = [saved_rando.dol.read_data(fs.read_u16, address + offset * 2) for offset in range(49)]
  assert written_charts == SHIFTED_CHARTS

def test_iso_is_named_after_the_player_without_reserved_characters(saved_rando):
  assert os.listdir(saved_rando.randomized_output_folder) == ["TWW pytestseed (Player1).iso"]

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
