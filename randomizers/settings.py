import random

from logic.item_types import DUNGEON_NONPROGRESS_ITEMS

from randomizer import WWRandomizer

DEFAULT_WEIGHTS = {
  "progression_dungeons": [(True, 80), (False, 20)],
  "progression_great_fairies": [(True, 50), (False, 50)],
  "progression_puzzle_secret_caves": [(True, 50), (False, 50)],
  "progression_combat_secret_caves": [(True, 50), (False, 50)],
  "progression_short_sidequests": [(True, 50), (False, 50)],
  "progression_long_sidequests": [(True, 20), (False, 80)],
  "progression_spoils_trading": [(True, 10), (False, 90)],
  "progression_minigames": [(True, 50), (False, 50)],
  "progression_free_gifts": [(True, 80), (False, 20)],
  "progression_mail": [(True, 50), (False, 50)],
  "progression_platforms_rafts": [(True, 50), (False, 50)],
  "progression_submarines": [(True, 50), (False, 50)],
  "progression_eye_reef_chests": [(True, 50), (False, 50)],
  "progression_big_octos_gunboats": [(True, 50), (False, 50)],
  "progression_triforce_charts": [(True, 20), (False, 80)],
  "progression_treasure_charts": [(True, 5), (False, 95)],
  "progression_expensive_purchases": [(True, 20), (False, 80)],
  "progression_misc": [(True, 50), (False, 50)],
  "progression_tingle_chests": [(True, 50), (False, 50)],
  "progression_battlesquid": [(True, 20), (False, 80)],
  "progression_savage_labyrinth": [(True, 35), (False, 65)],
  "progression_island_puzzles": [(True, 50), (False, 50)],
  "progression_dungeon_secrets": [(True, 50), (False, 50)],
  
  "keylunacy": [(True, 40), (False, 60)],
  "randomize_dungeon_entrances": [(True, 50), (False, 50)],
  "randomize_secret_cave_entrances": [(True, 30), (False, 70)],
  "randomize_secret_cave_inner_entrances": [(True, 50), (False, 50)],
  "randomize_boss_entrances": [(True, 50), (False, 50)],
  "randomize_miniboss_entrances": [(True, 50), (False, 50)],
  "randomize_fairy_fountain_entrances": [(True, 50), (False, 50)],
  "mix_entrances": [("Separate Dungeons From Caves & Fountains", 75), ("Mix Dungeons & Caves & Fountains", 25)],
  "randomize_charts": [(True, 50), (False, 50)],
  "randomize_starting_island": [(True, 100), (False, 0)],
  "chest_type_matches_contents": [(True, 100), (False, 0)],
  
  "num_path_hints": [(6, 100)],
  "num_barren_hints": [(6, 100)],
  "num_location_hints": [(8, 100)],
  "num_item_hints": [(0, 100)],
  "cryptic_hints": [(False, 100), (True, 0)],
  "prioritize_remote_hints": [(True, 100), (False, 0)],
  
  "swift_sail": [(True, 100), (False, 0)],
  "num_starting_triforce_shards": [(0, 60), (1, 9), (2, 8), (3, 8), (4, 5), (5, 5), (6, 2), (7, 2), (8, 1)],
  "add_shortcut_warps_between_dungeons": [(True, 80), (False, 20)],
  "sword_mode": [("Start with Hero's Sword", 60), ("No Starting Sword", 35), ("Swordless", 5)],
  "required_bosses": [(True, 90), (False, 10)],
  "num_required_bosses": [(1, 5), (2, 15), (3, 25), (4, 30), (5, 15), (6, 10)],
  "starting_pohs": [(0, 100)],
  "starting_hcs": [(0, 100)],
  "randomize_enemies": [(True, 0), (False, 100)],
  
  "skip_rematch_bosses": [(True, 75), (False, 25)],
  "hint_placement": [("fishmen_hints", 0), ("hoho_hints", 10), ("korl_hints", 80), ("stone_tablet_hints", 10)],
  "num_extra_starting_items": [(0, 25), (1, 40), (2, 25), (3, 10)],
  "start_with_maps_and_compasses": [(True, 80), (False, 20)],
}

def randomize_settings(seed=None):
  random.seed(seed)
  
  settings_dict = {
    "starting_gear": ["Telescope", "Ballad of Gales", "Song of Passing"],
  }
  for option_name, option_values in DEFAULT_WEIGHTS.items():
    values, weights = zip(*option_values)
    
    if option_name == "hint_placement":
      chosen_hint_placement = random.choices(values, weights=weights)[0]
      for hint_placement in values:
        settings_dict[hint_placement] = (hint_placement == chosen_hint_placement)
    elif option_name == "start_with_maps_and_compasses":
      start_with_maps_and_compasses = random.choices(values, weights=weights)[0]
      if start_with_maps_and_compasses:
        settings_dict["starting_gear"] += DUNGEON_NONPROGRESS_ITEMS
    elif option_name == "skip_rematch_bosses":
      if settings_dict["progression_dungeons"] or settings_dict["required_bosses"]:
        settings_dict["skip_rematch_bosses"] = True
      else:
        settings_dict["skip_rematch_bosses"] = random.choices(values, weights=weights)[0]

    else:
      chosen_option = random.choices(values, weights=weights)[0]
      settings_dict[option_name] = chosen_option
  
  ensure_valid_settings(settings_dict)

  return settings_dict

def ensure_valid_settings(settings):
  # Disable some invalid combinations of settings to maximize likelihood that
  # the seed will randomize successfully. Some overlap with
  # wwr_ui.randomizer_window.WWRandomizerWindow.ensure_valid_combination_of_options
  if not settings["progression_dungeons"]:
    settings["required_bosses"] = False