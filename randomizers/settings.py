from collections import OrderedDict
import functools
import math
import random

from randomizer import RNG_CHANGING_OPTIONS, Randomizer
from randomizers import items
from logic.logic import Logic

DEFAULT_WEIGHTS = OrderedDict({
  #"progression_dungeons": [(True, 80), (False, 20)], # This gets overwritten by num_race_mode_dungeons
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
  
  "num_path_hints": [(0, 0), (1, 0), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1000), (7, 1), (8, 1), (9, 1)],
  "num_barren_hints": [(0, 0), (1, 0), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1000), (7, 1), (8, 1), (9, 1), (10, 1)],
  "num_location_hints": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 1), (7, 1), (8, 1000), (9, 1), (10, 1), (11, 1), (12, 1)], # Need 6 because there are 6 always hints
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
  #"race_mode": [(True, 90), (False, 10)], # Overwritten by num_race_mode_dungeons
  # 0 -> progression_dungeons = off. 7 -> race_mode = off
  # Weights derived to be identical to tanjo's build
  # (7: dungeons on * no race mode, 0: dungeons off, others: dungeons on * race mode * initial probability)
  "num_race_mode_dungeons": [(0, 200), (1, 36), (2, 108), (3, 180), (4, 216), (5, 108), (6, 72), (7, 80)],
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
  "randomization_style",
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
} | {
  # We handle dungeons through num_race_mode_dungeons
  "progression_dungeons": weights_to_option_cost([(True, 80), (False, 20)]),
  # These are far from each other and kinda long, despite being 50/50 and few total checks
  "progression_eye_reef_chests": 1.5,
  # Some overrides for the most extreme weight, to avoid generation failures
  "progression_treasure_charts": 2,
}

class Distribution():
  @staticmethod
  def _possible_items(opt):
    return [v for v,w in DEFAULT_WEIGHTS[opt] if w > 0]

  @staticmethod
  def uniform(opt):
    values = Distribution._possible_items(opt)
    return values, [1 for _ in values]

  @staticmethod
  def _zipf(s, opt):
    values = Distribution._possible_items(opt)
    harmonic = sum(1/pow(i,s) for i in range(1,len(values)+1))
    return values, [round(100/(pow(k,s)*harmonic), 2) for k in range(1,len(values)+1)]

  @staticmethod
  def zipf(s):
    return functools.partial(Distribution._zipf, s)

  @staticmethod
  def _binomial(p, opt): # N taken from passed list length
    values = Distribution._possible_items(opt)
    return values, [
      round(100*math.comb(len(values),k)*pow(p,k)*pow(1-p,len(values)-k), 2)
      for k in range(1,len(values)+1)
    ]

  @staticmethod
  def binomial(p):
    return functools.partial(Distribution._binomial, p)

  @staticmethod
  def default_weights(opt):
    return zip(*DEFAULT_WEIGHTS[opt])

CHAOTIC_OPTION_DISTRIBUTIONS = {
  "num_race_mode_dungeons": Distribution.uniform,
  "num_starting_triforce_shards": Distribution.zipf(2),
  "num_starting_items": Distribution.zipf(1),
  "num_path_hints": Distribution.binomial(0.6),
  "num_barren_hints": Distribution.binomial(0.6),
  "num_location_hints": Distribution.binomial(0.4), # Min 6
}

def option_weights(randomization_mode, opt):
  if randomization_mode == "Orderly":
    return Distribution.default_weights(opt)
  elif randomization_mode == "Chaotically":
    return CHAOTIC_OPTION_DISTRIBUTIONS.get(opt, Distribution.uniform)(opt)
  else:
    raise ValueError(f"Don't know how to randomize in mode {randomization_mode}")

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
    "progression_dungeons": False,
    "race_mode": True,
  }
  settings_dict.update(prefilled_options)

  for option_name in DEFAULT_WEIGHTS:
    values, weights = option_weights(settings_dict["randomization_style"], option_name)
    
    if option_name == "starting_gear":
      # Handled in second_pass_options
      continue
    else:
      chosen_option = random.choices(values, weights=weights)[0]
    settings_dict[option_name] = chosen_option

  compute_derived_options(settings_dict)
  
  if settings_dict["target_checks"] > 0:
    settings_dict = adjust_settings_to_target(settings_dict, settings_dict["target_checks"])

  adjust_second_pass_options(settings_dict)
  # Randomize starting gear dynamically based on items which have logical implications in this seed
  settings_dict["starting_gear"] = randomize_starting_gear(settings_dict, seed=seed)

  for o in SETTINGS_RANDO_ONLY_OPTIONS:
    if o in settings_dict:
      del settings_dict[o]
  # Ensure progression flags appear first (it's what people care about)
  return dict(sorted(settings_dict.items(), key=lambda x: f"aaaa{x[0]}" if x[0].startswith("progression") else x[0]))

# This is where we can change options that depend on other options
def adjust_second_pass_options(options):
  # Clamp num_race_mode_dungeons
  compute_derived_options(options)
  options["num_race_mode_dungeons"] = max(min(options["num_race_mode_dungeons"], 6), 1)

  if not options["skip_rematch_bosses"] and options["progression_dungeons"]:
    # Cant have dungeons and trials at the same time
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

ITEM_LOCATIONS = Logic.load_and_parse_item_locations()
def get_incremental_locations_for_setting(all_options, incremental_option):
  options = all_options.copy()

  options[incremental_option] = False
  before = Logic.get_num_progression_locations_static(ITEM_LOCATIONS, options)
  options[incremental_option] = True
  after = Logic.get_num_progression_locations_static(ITEM_LOCATIONS, options)

  return after - before

def compute_weighted_locations(settings_dict):
  compute_derived_options(settings_dict)
  location_cost = lambda opt: int(settings_dict[opt]) * get_incremental_locations_for_setting(settings_dict, opt)

  # As the base case, we compute a total "cost" which is the number of checks in
  # a setting times a weight intented to convey the penibility of the setting
  total_cost = sum(
    PROGRESSION_SETTINGS_CHECK_COSTS[s] * location_cost(s)
    for s, _v in settings_dict.items() if s.startswith("progression_")
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
    # The last value is for no race mode, 
    DUNGEON_COSTS = [0, 0.20, 0.38, 0.56, 0.74, 0.92, 1.1, 1.4]
    dungeon_total_cost = location_cost("progression_dungeons") * PROGRESSION_SETTINGS_CHECK_COSTS["progression_dungeons"]
    # Remove dungeons from the initial cost calculation; we'll recompute after the multipliers
    total_cost -= dungeon_total_cost

    dungeon_total_cost *= DUNGEON_COSTS[settings_dict["num_race_mode_dungeons"]]
    if settings_dict["only_use_ganondorf_paths"]:
      dungeon_total_cost *= 1.05

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
      dungeon_total_cost *= 1 + 0.025 * settings_dict["num_race_mode_dungeons"]
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

  starting_items = settings_dict["num_starting_items"]
  # individual starting triforce shards in general don't reduce the seed cost since you need
  # to find all of them anyway, (on the contrary it reduces the number of spiky chests)
  # but starting triforce shards that cause progression items to show up on bosses count as
  # one less item to get
  if settings_dict["progression_dungeons"] and settings_dict["race_mode"]:
    non_shard_dungeons = (settings_dict["num_starting_triforce_shards"] + settings_dict["num_race_mode_dungeons"] - 8)
    if non_shard_dungeons > 0:
      starting_items += non_shard_dungeons
  if settings_dict["sword_mode"] == "Start with Hero's Sword":
    starting_items += 2 # Counts double since it's so useful

  total_cost *= pow(0.985, starting_items)


  # Figure out the ratio of hints to enabled settings, and aim for that
  # Ideally we want each hint to tell us something about one setting
  hints_target = sum(v for s,v in settings_dict.items() if s.startswith("progression_")) * 2
  total_hints = settings_dict["num_path_hints"] * 3 + settings_dict["num_location_hints"] * 0.3 + settings_dict["num_barren_hints"] * 2
  hint_distance = hints_target - total_hints

  # Stone tablet and korl hints can end up on islands we wouldn't otherwise go
  # They also happen much later, so are less useful
  if settings_dict["hint_placement"] == "stone_tablet_hints":
    if "Secret Caves" in settings_dict["randomize_entrances"]:
      # 15% of hintstones are in pawprint / cliff plat
      hint_distance += abs(hints_target)
    else:
      hint_distance += 0.5 * abs(hints_target)
  elif settings_dict["hint_placement"] == "hoho_hints":
    # Still annoying but much less, and the locations are completely fixed. But 2 of them are item locked
    hint_distance += 0.15 * abs(hints_target)

  total_cost += hint_distance # square, but same sign, with a tolerance of 1 hint in either direction

  return total_cost


class NoAcceptableSettingsException(Exception):
  pass

def orderly_settings_weights():
  first_phase = {
    # True/False toggles
    # We want the most 50/50 options to have higher chances to be toggled, and the
    # most/least likely options to have lower chances to be toggled
    opt: 100 - abs(int(weights[0][1] - weights[1][1]))
    for opt, weights in DEFAULT_WEIGHTS.items()
    if len(DEFAULT_WEIGHTS[opt]) == 2 and (weights[0][1] + weights[1][1]) == 100 and
      not any(w[1] == 100 for w in weights)
  } | {
    # Multivalued toggles. Manually weighted
    "hint_placement": 30,
    "sword_mode": 30,
    "randomize_entrances": 30,
    "num_starting_triforce_shards": 20,
    "num_race_mode_dungeons": 300, # Impacts race_mode and progression_dungeons
  }
  second_phase = {
    "num_race_mode_dungeons": 300,
    "num_starting_triforce_shards": 80,
    "num_starting_items": 100,
  }
  return first_phase, second_phase

def setting_is_guaranteed(option):
  total_weight = sum(v[1] for v in DEFAULT_WEIGHTS[option])
  return any(v[1] == total_weight for v in DEFAULT_WEIGHTS[option])

# All settings have the same likelihood of getting toggled. Weird settings ahead!
def chaotic_settings_weights():
  opts = {}
  for o,values in DEFAULT_WEIGHTS.items():
    if setting_is_guaranteed(o):
      continue

    if any(not v[0].__hash__ for v in values):
      # We need to put this in a dict later
      continue

    opts[o] = sum(1 for v in values if v[1] > 0) # More values => more likelihood of being flipped

  # Override for num_race_mode_dungeons which impacts 3 settings:
  opts["num_race_mode_dungeons"] += 4 # progression_dungeons, race_mode each 2 values
  return opts, opts.copy()

SETTINGS_WEIGHT_FUNCTIONS = {
  "Orderly": orderly_settings_weights,
  "Chaotically": chaotic_settings_weights,
}


def adjust_settings_to_target(settings_dict, target_checks):
  max_distance = round(target_checks * TARGET_CHECKS_SLACK)
  remaining_adjustable_settings, second_pass_settings = SETTINGS_WEIGHT_FUNCTIONS[settings_dict["randomization_style"]]()
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

      if math.isclose(new_cost, current_cost, rel_tol=0.05):
        # Option has no impact, will retry later
        second_pass_settings[selected] = remaining_adjustable_settings[selected]
        settings_dict[selected] = not settings_dict[selected]
      elif abs(new_cost - target_checks) >= current_distance: # This is not getting us closer, revert
        settings_dict[selected] = not settings_dict[selected]

      del remaining_adjustable_settings[selected]

    # For multivalued options, we'll try the 4 "around" the current value, to avoid too large swings.
    else:
      # Find the current option
      cur_idx = next(i for i, (v,_w) in enumerate(DEFAULT_WEIGHTS[selected]) if v == settings_dict[selected])
      # Test the one before and the one after (avoid going out of bounds)
      try_idxs = filter(lambda k: k >= 0 and k < len(DEFAULT_WEIGHTS[selected]), [cur_idx, cur_idx+1, cur_idx-1])
      # choose the best (or at random if it changes nothing)
      option_scores = {}
      try_sett = settings_dict.copy()
      for i in try_idxs:
        v, w = DEFAULT_WEIGHTS[selected][i]
        if w == 0:
          continue
        try_sett[selected] = v
        option_scores[v] = abs(compute_weighted_locations(try_sett) - target_checks)

      # Requeue in the same phase if moved, requeue in the next phase if not
      if math.isclose(min(option_scores.values()), max(option_scores.values())):
        if not second_pass:
          second_pass_settings[selected] = second_pass_settings.get(selected, 0) + 2*remaining_adjustable_settings[selected]
      else:
        # Often there are multiple minimal options, and min takes the first, so round and shuffle them first
        possible_values = list(option_scores.items())
        random.shuffle(possible_values)
        min_idx = min(enumerate(possible_values), key=lambda tup: int(tup[1][1]))[0]
        # If we only requeue when the actual value has changed, we have a strictly decreasing distance, 
        # and a finite number of possibilities to check, so this will terminate
        if not math.isclose(current_distance, possible_values[min_idx][1], rel_tol=0.05):
          # Reduce weight, since we "consumed" one option
          remaining_adjustable_settings[selected] -= math.floor(remaining_adjustable_settings[selected]/len(DEFAULT_WEIGHTS[selected]))
        else:
          # Requeue to second phase if we didn't actually change enough to matter
          second_pass_settings[selected] = second_pass_settings.get(selected, 0) + remaining_adjustable_settings[selected]

        settings_dict[selected] = possible_values[min_idx][0]

    # Reapply constraints if we toggled them
    ensure_min_max_difficulty(settings_dict, target_checks)

  return settings_dict

def ensure_min_max_difficulty(settings_dict, target_checks):
  # 140 is the cutoff for "easy" seeds. Above this, almost anything goes, but
  # under we prevent some of the most egregious settings combinations

  if target_checks < 140:
    settings_dict["skip_rematch_bosses"] = True
    if settings_dict["sword_mode"] == "Swordless":
      settings_dict["sword_mode"] = "No Starting Sword"

    # Savage is too volatile to play well with the target difficulty (either nothing, or a huge slog)
    settings_dict["progression_savage_labyrinth"] = False

    # Not really as a difficulty thing, rather this helps ensure there are enough
    # non-charts location to reduce the likelihood of having to reroll, since
    # charts are worth 100+ locations on their own, and add 40 progression
    # locations, that need to be placed somewhere
    settings_dict["progression_treasure_charts"] = False

def compute_derived_options(settings_dict):
  settings_dict["progression_dungeons"] = (settings_dict["num_race_mode_dungeons"] > 0)
  settings_dict["race_mode"] = (settings_dict["num_race_mode_dungeons"] < 7)
