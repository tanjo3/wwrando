import random

from logic.item_types import DUNGEON_NONPROGRESS_ITEMS

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
  
  "keylunacy": [(True, 40), (False, 60)],
  "randomize_entrances": [("Disabled", 20), ("Dungeons", 20), ("Secret Caves", 20), ("Dungeons & Secret Caves (Separately)", 20), ("Dungeons & Secret Caves (Together)", 20)],
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
  "randomize_music": [(True, 0), (False, 100)],
  "starting_gear": [
    (["Progressive Picto Box"], 5.88),
    (["Spoils Bag"], 5.88),
    (["Grappling Hook"], 5.88),
    (["Progressive Bow"], 5.88),
    (["Power Bracelets"], 5.88),
    (["Iron Boots"], 5.88),
    (["Bait Bag"], 5.88),
    (["Boomerang"], 5.88),
    (["Hookshot"], 5.88),
    (["Bombs"], 5.88),
    (["Skull Hammer"], 5.88),
    (["Deku Leaf"], 5.88),
    (["Progressive Shield"], 5.88),
    (["Empty Bottle"], 5.88),
    (["Ghost Ship Chart"], 5.88),
    (["Nayru's Pearl", "Din's Pearl", "Farore's Pearl"], 5.88),
    (["Delivery Bag"], 1.20),
    (["Delivery Bag", "Note to Mom"], 1.18),
    (["Delivery Bag", "Maggie's Letter"], 1.18),
    (["Delivery Bag", "Moblin's Letter"], 1.18),
    (["Delivery Bag", "Cabana Deed"], 1.18),
  ],
  "starting_pohs": [(0, 100)],
  "starting_hcs": [(0, 100)],
  "randomize_enemies": [(True, 0), (False, 100)],
  
  "skip_rematch_bosses": [(True, 75), (False, 25)],
  "hint_placement": [("fishmen_hints", 0), ("hoho_hints", 10), ("korl_hints", 80), ("stone_tablet_hints", 10)],
  "num_starting_items": [(0, 25), (1, 40), (2, 25), (3, 10)],
  "start_with_maps_and_compasses": [(True, 80), (False, 20)],
}

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
  
  values, weights = zip(*DEFAULT_WEIGHTS["num_starting_items"])
  num_starting_items = random.choices(values, weights=weights)[0]
  
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
      settings_dict["starting_gear"] += ["Telescope", "Progressive Magic Meter", "Ballad of Gales", "Song of Passing"]
      for items in weighted_sample_without_replacement(values, weights, k=num_starting_items):
        settings_dict["starting_gear"] += items
    elif option_name == "num_starting_items":
      continue
    elif option_name == "skip_rematch_bosses":
      if settings_dict["progression_dungeons"] or settings_dict["required_bosses"]:
        settings_dict["skip_rematch_bosses"] = True
      else:
        settings_dict["skip_rematch_bosses"] = random.choices(values, weights=weights)[0]

    else:
      chosen_option = random.choices(values, weights=weights)[0]
      settings_dict[option_name] = chosen_option
    
    settings_dict["starting_gear"] = list(set(settings_dict["starting_gear"]))
  
  return settings_dict