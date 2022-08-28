from collections import OrderedDict
import math
import random

from randomizer import RNG_CHANGING_OPTIONS, Randomizer
from randomizers import items
from logic.logic import Logic

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
  "sword_mode": [("Start with Hero's Sword", 60), ("No Starting Sword", 35), ("Swordless", 5)],
  "race_mode": [(True, 90), (False, 10)],
  "num_race_mode_dungeons": [(1, 5), (2, 15), (3, 25), (4, 30), (5, 15), (6, 10)],
  "skip_rematch_bosses": [(True, 75), (False, 25)],
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

# Initial check "cost" is inversely related to likelihood of setting, with a flat cost of 1 for 50/50 settings
TARGET_CHECKS_SLACK = 0.15
# Options that are only used to decide on the settings, and not passed down to the item randomizer
SETTINGS_RANDO_ONLY_OPTIONS = [
  "target_checks",
  "hint_placement",
  "num_starting_items",
  "start_with_maps_and_compasses",
]

DUNGEON_NONPROGRESS_ITEMS = \
  ["DRC Dungeon Map", "DRC Compass"] + \
  ["FW Dungeon Map", "FW Compass"] + \
  ["TotG Dungeon Map", "TotG Compass"] + \
  ["FF Dungeon Map", "FF Compass"] + \
  ["ET Dungeon Map", "ET Compass"] + \
  ["WT Dungeon Map", "WT Compass"]

def weights_to_option_cost(weights):
  # Assume options are True/False, with True listed first, and weights sum to 100.
  # remove the if to enforce this for testing
  if True:
    if (
      len(weights) > 2 or
      weights[0][1] + weights[1][1] != 100 or
      (weights[0][0], weights[1][0]) != (True,False)
    ):
      raise ValueError("Options must be True/False and weigths must sum to 100")

  return 100 / (2 * weights[0][1])

PROGRESSION_SETTINGS_CHECK_COSTS = {
  k: weights_to_option_cost(v)
  for k,v in DEFAULT_WEIGHTS.items()
  if k.startswith("progression_")
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

def randomize_settings(seed=None, prefilled_options={}):
  random.seed(seed)

  for i, option in enumerate(RNG_CHANGING_OPTIONS + ["target_checks"]):
    value = prefilled_options.get(option, None)
    if value is None:
      continue # Ignore non-prefillable options
    if isinstance(value, str):
      value = len(value)
    for j in range(1, 100 + i):
      random.getrandbits(value + 20 * i + j)

  settings_dict = {
    "starting_gear": [],
  }
  settings_dict.update(prefilled_options)

  for option_name, option_values in DEFAULT_WEIGHTS.items():
    values, weights = zip(*option_values)
    
    if option_name == "starting_gear":
      # Handled in second_pass_options
      continue
    else:
      chosen_option = random.choices(values, weights=weights)[0]
      settings_dict[option_name] = chosen_option
  
  if settings_dict["target_checks"] > 0:
    settings_dict = adjust_settings_to_target(settings_dict, settings_dict["target_checks"])

  adjust_second_pass_options(settings_dict)
  # Randomize starting gear dynamically based on items which have logical implications in this seed
  settings_dict["starting_gear"] = randomize_starting_gear(settings_dict, seed=seed)

  for o in SETTINGS_RANDO_ONLY_OPTIONS:
    if o in settings_dict:
      del settings_dict[o]
  return settings_dict

# This is where we can change options that depend on other options
def adjust_second_pass_options(options):
  if options["progression_dungeons"]:
    options["skip_rematch_bosses"] = True

  # Adapt hint_placement to the format the randomizer expects (individual bools for each possible placement)
  for (hint_placement, _weight) in DEFAULT_WEIGHTS["hint_placement"]:
    options[hint_placement] = (hint_placement == options["hint_placement"])

def randomize_starting_gear(options, seed=None):
  starting_gear = ["Telescope", "Ballad of Gales", "Song of Passing"]

  if options["start_with_maps_and_compasses"]:
    starting_gear += DUNGEON_NONPROGRESS_ITEMS
  
  if options["num_starting_items"] == 0:
    return starting_gear
  
  # Avoid passing options the randomizer doesn't know about
  # It changes seeds, and if they have the wrong type it can make randomization fail too
  try:
    rando_options = {o:v for o,v in options.items() if o not in SETTINGS_RANDO_ONLY_OPTIONS}
    rando = Randomizer(seed, "", "", "", rando_options, cmd_line_args={"-dry": None})
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
  num_starting_items = min(options["num_starting_items"], len(modified_pool))
  for selected_items in weighted_sample_without_replacement(values, weights, k=num_starting_items):
    starting_gear += selected_items
  
  return list(set(starting_gear))

def get_incremental_locations_for_setting(cached_item_locations, all_options, incremental_option):
  options = all_options.copy()

  options[incremental_option] = False
  before = Logic.get_num_progression_locations_static(cached_item_locations, options)
  options[incremental_option] = True
  after = Logic.get_num_progression_locations_static(cached_item_locations, options)

  return after - before

def compute_weighted_locations(settings_dict):
  cached_item_locations = Logic.load_and_parse_item_locations()
  location_cost = lambda opt: int(settings_dict[opt]) * get_incremental_locations_for_setting(cached_item_locations, settings_dict, opt)

  # As the base case, we compute a total "cost" which is the number of checks in
  # a setting times a weight intented to convey the penibility of the setting
  total_cost = sum(
    PROGRESSION_SETTINGS_CHECK_COSTS[s] * location_cost(s)
    for s, value in settings_dict.items() if s.startswith("progression_")
  )

  combat_caves_cost = location_cost("progression_combat_secret_caves")
  secret_caves_cost = location_cost("progression_puzzle_secret_caves")
  if combat_caves_cost+secret_caves_cost > 0 and "Secret Caves" in settings_dict["randomize_entrances"]:
    # If only one of combat, secret caves are enabled, randomize entrances is
    # "worse" as it can get you to an ool location and be a waste of time
    # If both are enabled, it's not as bad since any entrance is probably a place you'd have needed to visit anyway

    # Since we already counted them as a full 1 in base_weight, this is "on top". so a 1 additional_multiplier is a total of 2 for the weight
    if combat_caves_cost == 0 or secret_caves_cost == 0:
      additional_multiplier = 0.75
      # If dungeons are also in the pool together, but aren't enabled, there's even more dead entrances so bump it a little more
      if settings_dict["randomize_entrances"] == "Dungeons & Secret Caves (Together)" and not settings_dict["progression_dungeons"]:
        additional_multiplier = 1
    else:
      additional_multiplier = 0.25
      if settings_dict["randomize_entrances"] == "Dungeons & Secret Caves (Together)" and not settings_dict["progression_dungeons"]:
        additional_multiplier = 0.40

    total_cost += (combat_caves_cost+secret_caves_cost) * additional_multiplier

  if settings_dict["sword_mode"] == "Swordless":
    # Bump the cost of combat caves when you have a higher likelihood of having to clear them without sword
    total_cost += 1 * combat_caves_cost
  elif settings_dict["sword_mode"] == "No Starting Sword":
    total_cost += 0.15 * combat_caves_cost

  if settings_dict["progression_dungeons"]:
    # Adjust for dungeons: If dungeons are on, put a sliding scale depending on
    # the number of race mode dungeons. Ideally we'd be able to independently
    # select which dungeons we want in logic but that'll do for now
    # Since each race mode dungeon means one less item in the item pool (boss
    # reward), each additional dungeon costs "less"
    # The first value is for no race mode
    DUNGEON_COSTS = [1.5, 0.20, 0.38, 0.56, 0.74, 0.92, 1.1]
    dungeon_total_cost = location_cost("progression_dungeons") * PROGRESSION_SETTINGS_CHECK_COSTS["progression_dungeons"]
    # Remove dungeons from the initial cost calculation; we'll recompute after the multipliers
    total_cost -= dungeon_total_cost

    if settings_dict["race_mode"]:
      dungeon_total_cost *= DUNGEON_COSTS[settings_dict["num_race_mode_dungeons"]]
      if settings_dict["only_use_ganondorf_paths"]:
        dungeon_total_cost *= 1.05
    else:
      dungeon_total_cost *= DUNGEON_COSTS[0]

    # Keylunacy means more items, and more potential dips in dungeons. Apply a flat multiplier
    if settings_dict["keylunacy"]:
      dungeon_total_cost *= 1.25
    # Small cost bump for dungeons randomized entrances
    if settings_dict["randomize_entrances"] in ("Dungeons", "Dungeons & Secret Caves (Separately)") :
      dungeon_total_cost *= 1.05
    # Larger cost bump for dungeons randomized together with caves, and even larger if
    # randomized with entrances to out-of-logic locations without race mode
    elif settings_dict["randomize_entrances"] == "Dungeons & Secret Caves (Together)":
      if settings_dict["race_mode"]:
        # minimal bump: in race mode we know where the entrances are immediately anyway
        dungeon_total_cost *= 1.05
      else:
        dungeon_total_cost *= 1.1
        # Additional weights for when entrances are mixed with places you don't
        # need to go to anyway
        if combat_caves_cost == 0:
          dungeon_total_cost *= 1.1
        if secret_caves_cost == 0: # There's more of these
          dungeon_total_cost *= 1.15
    # Another bump for missing warp pots, scaled by the number of dungeons in logic
    if not settings_dict["add_shortcut_warps_between_dungeons"]:
      if settings_dict["race_mode"]:
        dungeon_total_cost *= 1 + 0.025 * settings_dict["num_race_mode_dungeons"]
      else:
        dungeon_total_cost *= 1.15
    if settings_dict["sword_mode"] == "Swordless":
      dungeon_total_cost *= 1.15

    if not settings_dict["start_with_maps_and_compasses"]:
      # 2 dead items in each dungeon that can be inferred and skipped
      dungeon_total_cost *= 0.95

    total_cost += dungeon_total_cost

  triforce_charts_cost = location_cost("progression_triforce_charts")
  treasure_charts_cost = location_cost("progression_treasure_charts")
  if settings_dict["randomize_charts"]:
    if treasure_charts_cost > 0 and triforce_charts_cost == 0:
      # Nobody knows all the vanilla locations and we're going only from 41 locations to 49 so not a large change
      total_cost += treasure_charts_cost * 0.05
    elif treasure_charts_cost == 0 and triforce_charts_cost > 0:
      # In the other direction, triforce charts go from 8 locations to 49, which makes them way worse
      total_cost += triforce_charts_cost * 0.5
    # If all the charts were progression anyway, it really doesn't change anything where they are

# Below this, modifiers that apply multiplicatively to the total cost rather
# than adding or removing cost for specific subsets of checks

  starting_items = settings_dict["num_starting_items"] + settings_dict["num_starting_triforce_shards"]

  # Triforce shards that cause other, progression items to show up on bosses are worth double
  if settings_dict["progression_dungeons"] and settings_dict["race_mode"]:
    non_shard_dungeons = (settings_dict["num_starting_triforce_shards"] + settings_dict["num_race_mode_dungeons"] - 8)
    if non_shard_dungeons > 0:
      starting_items += non_shard_dungeons
  if settings_dict["sword_mode"] == "Start with Hero's Sword":
    starting_items += 1

  total_cost *= pow(0.98, starting_items)


  # Stone tablet and korl hints can end up on islands we wouldn't otherwise go
  # They also happen much later, so are less useful
  if settings_dict["hint_placement"] == "stone_tablet_hints":
    if "Secret Caves" in settings_dict["randomize_entrances"]:
      # 13% of hintstones are in pawprint / cliff plat
      total_cost *= 1.45
    else:
      total_cost *= 1.3
  elif settings_dict["hint_placement"] == "hoho_hints":
    # Still annoying but much less, and the locations are completely fixed. But 2 of them are item locked
    total_cost *= 1.2

  return total_cost

ADJUSTABLE_SETTINGS = {
  # True/False toggles
  # We want the most 50/50 options to have higher chances to be toggled, and the
  # most/least likely options to have lower chances to be toggled
  opt: 100 - abs(weights[0][1] - weights[1][1])
  for opt, weights in DEFAULT_WEIGHTS.items()
  if len(weights) == 2 and (weights[0][1] + weights[1][1]) == 100 and
    not any(w[1] == 100 for w in weights)
} | {
  # Multivalued toggles. Manually weighted
  "hint_placement": 30,
  "sword_mode": 30,
  "randomize_entrances": 30,
  "num_starting_triforce_shards": 20,
  "num_race_mode_dungeons": 100,
}

SECOND_PASS_ADJUSTABLE = {
  "num_race_mode_dungeons": 300,
  "num_starting_triforce_shards": 80,
  "num_starting_items": 100,
}

class NoAcceptableSettingsException(Exception):
  pass


def adjust_settings_to_target(settings_dict, target_checks):
  max_distance = round(target_checks * TARGET_CHECKS_SLACK)
  remaining_adjustable_settings = ADJUSTABLE_SETTINGS.copy()
  second_pass_settings = SECOND_PASS_ADJUSTABLE.copy()
  second_pass = False
  bonus_accuracy_toggles = target_checks // 60

  ensure_min_max_difficulty(settings_dict, target_checks)
  current_distance = float('inf')

  while bonus_accuracy_toggles > 0 or current_distance > max_distance:
    current_cost = compute_weighted_locations(settings_dict)
    current_distance = abs(current_cost - target_checks)

    # Set up available togglable options. This varies between first and second pass
    if second_pass:
      bonus_accuracy_toggles -= 1
      if len(remaining_adjustable_settings) == 0 or current_distance > max_distance:
        # Ran out of settings to toggle. Unlikely to happen
        # This combined with removing one element from
        # remaining_adjustable_settings on each iteration guarantees termination
        if current_distance < max_distance * 2:
          # We're within 2 times the target distance, that's not great but probably fine
          break
        else:
          raise NoAcceptableSettingsException("Couldn't reach an acceptable number of checks with the starting seed")

    else:
      if len(remaining_adjustable_settings) == 0 or current_distance < max_distance:
        second_pass = True
        remaining_adjustable_settings |= second_pass_settings
        bonus_accuracy_toggles -= 1

    togglable, weights = list(remaining_adjustable_settings.keys()), list(remaining_adjustable_settings.values())
    selected = random.choices(togglable,weights=weights)[0]

    # Small simplification, if there are only 2 options (yes/no) just try the other one
    # and see if it improves
    # for multivalued options we'll have to try the various options
    if len(DEFAULT_WEIGHTS[selected]) == 2:
      settings_dict[selected] = not settings_dict[selected]
      new_cost = compute_weighted_locations(settings_dict)

      if math.isclose(new_cost, current_cost):
        # Option has no impact, will retry later
        second_pass_settings[selected] = remaining_adjustable_settings[selected]
        settings_dict[selected] = not settings_dict[selected]
      elif abs(new_cost - target_checks) >= current_distance: # This is not getting us closer, revert
        settings_dict[selected] = not settings_dict[selected]

    # For multivalued options, we'll take the "best" one, that takes us closest to the target score
    # With the exception that if it doesn't change anything, we'll requeue it to retry last
    # Because all these options affect dungeons, this gives a chance for
    # dungeons to be enabled, then this will be retried
    else:
      option_scores = {}
      for value, w in DEFAULT_WEIGHTS[selected]:
        if w == 0:
          # Skip options that aren't allowed
          continue
        settings_dict[selected] = value
        option_scores[value] = abs(compute_weighted_locations(settings_dict) - target_checks)

      # If the option has no impact, reroll it in case a related option gets toggled later.
      # Also select it for reroll on the second phase, again if a related option gets toggled in between
      if math.isclose(min(option_scores.values()), max(option_scores.values())):
        if not selected in second_pass_settings:
          second_pass_settings[selected] = remaining_adjustable_settings[selected]

        values, weights = zip(*DEFAULT_WEIGHTS[selected])
        chosen_option = random.choices(values, weights=weights)[0]
        settings_dict[selected] = chosen_option
      else:
        # Often there are multiple minimal options, and min takes the first, so round and shuffle them first
        possible_values = list(option_scores.items())
        random.shuffle(possible_values)
        settings_dict[selected] = min(possible_values, key=lambda tup: int(tup[1]))[0]

    del remaining_adjustable_settings[selected]
    # Reapply constraints if we toggled them
    ensure_min_max_difficulty(settings_dict, target_checks)

  return settings_dict

def ensure_min_max_difficulty(settings_dict, target_checks):
  # Charts are only in at >=175 difficulty.
  # Not really as a difficulty thing, rather this helps ensure there are enough
  # non-charts location to reduce the likelihood of having to reroll, since
  # charts are worth 100+ locations on their own
  if target_checks < 175:
    settings_dict["progression_treasure_charts"] = False

  # 140 is the cutoff for "easy" seeds. Above this, almost anything goes, but
  # under we prevent some of the most egregious settings combinations

  # Swordless and savage are disproportionately hard for the number of checks
  if target_checks < 140:
    settings_dict["progression_savage_labyrinth"] = False
    settings_dict["skip_rematch_bosses"] = True
    # non-race mode is also too volatile and best kept for normal and high difficulty
    settings_dict["race_mode"] = True

    if settings_dict["sword_mode"] == "Swordless":
      settings_dict["sword_mode"] = "No Starting Sword"


  # Put some min and max numbers of race mode dungeons
  if settings_dict["num_race_mode_dungeons"] < target_checks // 100:
    settings_dict["num_race_mode_dungeons"] = target_checks // 100
  if settings_dict["num_race_mode_dungeons"] > target_checks // 25: # Need 150 for 6DRM
    settings_dict["num_race_mode_dungeons"] = target_checks // 25