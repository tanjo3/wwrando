from collections import OrderedDict
import random

from randomizer import Randomizer
from randomizers import items

DEFAULT_WEIGHTS = OrderedDict({
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
  
  "keylunacy": [(True, 40), (False, 60)],
  "randomize_entrances": [("Disabled", 20), ("Dungeons", 20), ("Secret Caves", 20), ("Dungeons & Secret Caves (Separately)", 20), ("Dungeons & Secret Caves (Together)", 20)],
  "randomize_charts": [(True, 50), (False, 50)],
  "randomize_starting_island": [(True, 100), (False, 0)],
  "chest_type_matches_contents": [(True, 100), (False, 0)],
  "keep_duplicates_in_logic": [(True, 50), (False, 50)],
  
  "num_path_hints": [(6, 100)],
  "num_barren_hints": [(6, 100)],
  "num_location_hints": [(8, 100)],
  "num_item_hints": [(0, 100)],
  "only_use_ganondorf_paths": [(True, 25), (False, 75)],
  "clearer_hints": [(True, 100), (False, 0)],
  "use_always_hints": [(True, 100), (False, 0)],
  
  "swift_sail": [(True, 100), (False, 0)],
  "instant_text_boxes": [(True, 100), (False, 0)],
  "reveal_full_sea_chart": [(True, 100), (False, 0)],
  "num_starting_triforce_shards": [(0, 60), (1, 9), (2, 8), (3, 8), (4, 5), (5, 5), (6, 2), (7, 2), (8, 1)],
  "add_shortcut_warps_between_dungeons": [(True, 80), (False, 20)],
  "do_not_generate_spoiler_log": [(True, 100), (False, 0)],
  "sword_mode": [("Start with Hero's Sword", 60), ("No Starting Sword", 35), ("Swordless", 5)],
  "skip_rematch_bosses": [(True, 100), (False, 0)],
  "race_mode": [(True, 90), (False, 10)],
  "num_race_mode_dungeons": [(1, 5), (2, 15), (3, 25), (4, 30), (5, 15), (6, 10)],
  "randomize_music": [(True, 0), (False, 100)],
  "starting_gear": [
    (["Progressive Picto Box"], 5.6),
    (["Spoils Bag"], 5.6),
    (["Grappling Hook"], 5.6),
    (["Progressive Bow"], 5.6),
    (["Power Bracelets"], 5.6),
    (["Iron Boots"], 5.6),
    (["Bait Bag"], 5.6),
    (["Boomerang"], 5.6),
    (["Hookshot"], 5.6),
    (["Bombs"], 5.6),
    (["Skull Hammer"], 5.6),
    (["Deku Leaf"], 5.6),
    (["Progressive Shield"], 5.6),
    (["Empty Bottle"], 5.6),
    (["Ghost Ship Chart"], 5.6),
    (["Progressive Magic Meter"], 5.6),
    (["Nayru's Pearl", "Din's Pearl", "Farore's Pearl"], 5.6),
    (["Delivery Bag"], 1.16),
    (["Delivery Bag", "Note to Mom"], 0.91),
    (["Delivery Bag", "Maggie's Letter"], 0.91),
    (["Delivery Bag", "Moblin's Letter"], 0.91),
    (["Delivery Bag", "Cabana Deed"], 0.91),
  ],
  "starting_pohs": [(0, 100)],
  "starting_hcs": [(0, 100)],
  "remove_music": [(True, 0), (False, 100)],
  "randomize_enemies": [(True, 0), (False, 100)],
  
  "hint_placement": [("fishmen_hints", 0), ("hoho_hints", 10), ("korl_hints", 80), ("stone_tablet_hints", 10)],
  "num_starting_items": [(0, 25), (1, 40), (2, 25), (3, 10)],
  "start_with_maps_and_compasses": [(True, 80), (False, 20)],
})

# add `skip_rematch_bosses` after initialization to ensure `progression_dungeons` is sampled first
DEFAULT_WEIGHTS["skip_rematch_bosses"] = [(True, 75), (False, 25)]

DUNGEON_NONPROGRESS_ITEMS = \
  ["DRC Dungeon Map", "DRC Compass"] + \
  ["FW Dungeon Map", "FW Compass"] + \
  ["TotG Dungeon Map", "TotG Compass"] + \
  ["FF Dungeon Map", "FF Compass"] + \
  ["ET Dungeon Map", "ET Compass"] + \
  ["WT Dungeon Map", "WT Compass"]


def weighted_sample_without_replacement(population, weights, k=1):
  # Perform a weighted sample of `k`` elements from `population` without replacement.
  # Taken from: https://stackoverflow.com/a/43649323
  weights = list(weights)
  positions = range(len(population))
  indices = []
  while True:
    needed = k - len(indices)
    if not needed:
      break
    for i in random.choices(positions, weights, k=needed):
      if weights[i]:
        weights[i] = 0.0
        indices.append(i)
  return [population[i] for i in indices]

def randomize_settings(seed=None):
  random.seed(seed)
  
  settings_dict = {
    "starting_gear": [],
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
    elif option_name == "starting_gear":
      # Randomize starting gear after all the other settings are generated by calling `randomize_starting_gear`
      continue
    elif option_name == "num_starting_items":
      continue
    elif option_name == "skip_rematch_bosses":
      if settings_dict["progression_dungeons"]:
        chosen_option = True
      else:
        chosen_option = random.choices(values, weights=weights)[0]
      settings_dict["skip_rematch_bosses"] = chosen_option
    else:
      chosen_option = random.choices(values, weights=weights)[0]
      settings_dict[option_name] = chosen_option
  
  # Randomize starting gear dynamically based on items which have logical implications in this seed
  settings_dict["starting_gear"] = randomize_starting_gear(settings_dict, seed=seed)
  
  return settings_dict

def randomize_starting_gear(options, seed=None):
  starting_gear = ["Telescope", "Ballad of Gales", "Song of Passing"]
  
  values, weights = zip(*DEFAULT_WEIGHTS["num_starting_items"])
  num_starting_items = random.choices(values, weights=weights)[0]
  if num_starting_items == 0:
    return starting_gear
  
  try:
    rando = Randomizer(seed, "", "", "", options, cmd_line_args={"-dry": None})
  except Exception:
    return starting_gear
  
  # Determine which members of the starting items pool are valid based on their CTMC chest type
  valid_starting_gear_indices = []
  excess_weight = 0
  for i, (gear, weight) in enumerate(DEFAULT_WEIGHTS["starting_gear"]):
    if any(items.get_ctmc_chest_type_for_item(rando, item_name) for item_name in gear):
      valid_starting_gear_indices.append(i)
    else:
      excess_weight += weight
  
  if len(valid_starting_gear_indices) == 0:
    return starting_gear
  
  # Filter out starting items with no logical use and distribute its weight evenly across remaining options
  modified_pool = []
  distributed_weight = excess_weight / len(valid_starting_gear_indices)
  for i, (gear, weight) in enumerate(DEFAULT_WEIGHTS["starting_gear"]):
    if i in valid_starting_gear_indices:
      modified_pool.append((gear, weight + distributed_weight))
  
  values, weights = zip(*modified_pool)
  num_starting_items = min(num_starting_items, len(modified_pool))
  for selected_items in weighted_sample_without_replacement(values, weights, k=num_starting_items):
    starting_gear += selected_items
  
  return list(set(starting_gear))
