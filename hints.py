import os
from collections import Counter
from collections import OrderedDict
import copy
from enum import Enum
from math import sqrt

import yaml
from logic.item_types import CONSUMABLE_ITEMS, DUNGEON_PROGRESS_ITEMS, DUNGEON_NONPROGRESS_ITEMS
from wwrando_paths import DATA_PATH

from logic.logic import Logic


class HintType(Enum):
  PATH = 0
  BARREN = 1
  ITEM = 2
  LOCATION = 3


class ItemHintPriority(Enum):
  NONE = 0
  ICE_RODS = 1
  NO_DUNGEON_PATHS = 2


class Hint:
  def __init__(self, type: HintType, info1, info2=None):
    self.type = type
    self.info1 = info1
    self.info2 = info2
  
  def __str__(self):
    return "<HINT: %s, (%s, %s)>" % (str(self.type), self.info1, self.info2)
  
  def __hash__(self):
    return hash(str(self))
  
  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return (
        (self.type == other.type)
        and (self.info1 == other.info1)
        and (self.info2 == other.info2)
      )
    else:
      return False


class Hints:
  # When these items are placed in a seed, they are always logically required regardless of settings. This list is used
  # to speed up the hint generation.
  HARD_REQUIRED_ITEMS = [
    "Grappling Hook",
    "Boomerang",
    "Hookshot",
    
    "Triforce Shard 1",
    "Triforce Shard 2",
    "Triforce Shard 3",
    "Triforce Shard 4",
    "Triforce Shard 5",
    "Triforce Shard 6",
    "Triforce Shard 7",
    "Triforce Shard 8",
    
    "Progressive Sword",
    "Progressive Bow",
  ]
  
  # For hinting purposes, these item names can refer to multiple items at multiple locations
  PROGRESSIVE_ITEMS = [
    "Progressive Quiver",
    "Progressive Sword",
    "Progressive Shield",
    "Progressive Bow",
    "Progressive Wallet",
    "Progressive Picto Box",
    "Empty Bottle",
    
    "DRC Small Key",
    "FW Small Key",
    "TotG Small Key",
    "ET Small Key",
    "WT Small Key",
  ]
  
  # A dictionary mapping dungeon name to the dungeon boss. The boss name is used as the path goal in the hint text.
  DUNGEON_NAME_TO_BOSS_NAME = {
    "Dragon Roost Cavern": "Gohma",
    "Forbidden Woods": "Kalle Demos",
    "Tower of the Gods": "Gohdan",
    "Forsaken Fortress": "Helmaroc King",
    "Earth Temple": "Jalhalla",
    "Wind Temple": "Molgera",
    "Ganon's Tower": "Ganondorf",
  }
  
  # A dictionary mapping dungeon name to the requirement name. This dictionary is used when determining which items are
  # on the path to a goal.
  DUNGEON_NAME_TO_REQUIREMENT_NAME = {
    "Dragon Roost Cavern": "Can Access Other Location \"Dragon Roost Cavern - Gohma Heart Container\"",
    "Forbidden Woods": "Can Access Other Location \"Forbidden Woods - Kalle Demos Heart Container\"",
    "Tower of the Gods": "Can Access Other Location \"Tower of the Gods - Gohdan Heart Container\"",
    "Forsaken Fortress": "Can Access Other Location \"Forsaken Fortress - Helmaroc King Heart Container\"",
    "Earth Temple": "Can Access Other Location \"Earth Temple - Jalhalla Heart Container\"",
    "Wind Temple": "Can Access Other Location \"Wind Temple - Molgera Heart Container\"",
    "Ganon's Tower": "Can Reach and Defeat Ganondorf",
  }
  
  def __init__(self, rando):
    self.rando = rando
    self.logic = rando.logic
    self.options = rando.options
    
    # Define constants for hint distribution
    self.MAX_PATH_HINTS = int(self.options.get("num_path_hints", 0))
    self.MAX_BARREN_HINTS = int(self.options.get("num_barren_hints", 0))
    self.MAX_ITEM_HINTS = int(self.options.get("num_item_hints", 0))
    self.MAX_LOCATION_HINTS = int(self.options.get("num_location_hints", 0))
    self.TOTAL_NUM_HINTS = self.MAX_PATH_HINTS + self.MAX_BARREN_HINTS + self.MAX_LOCATION_HINTS + self.MAX_ITEM_HINTS
    
    self.WOTH_ONLY = self.options.get("only_use_ganondorf_paths")
    self.CLEARER_HINTS = self.options.get("clearer_hints")
    self.USE_ALWAYS_HINTS = self.options.get("use_always_hints")
    
    self.ITEM_HINT_PRIORITY = self.options.get("item_hint_priority")
    if self.ITEM_HINT_PRIORITY == "Ice Rods":
      self.ITEM_HINT_PRIORITY = ItemHintPriority.ICE_RODS
    elif self.ITEM_HINT_PRIORITY == "No D Paths":
      self.ITEM_HINT_PRIORITY = ItemHintPriority.NO_DUNGEON_PATHS
    else:
      self.ITEM_HINT_PRIORITY = ItemHintPriority.NONE
    
    # Import dictionaries used to build hints from files
    with open(os.path.join(DATA_PATH, "progress_item_hints.txt"), "r") as f:
      self.progress_item_hints = yaml.safe_load(f)
    with open(os.path.join(DATA_PATH, "island_name_hints.txt"), "r") as f:
      self.island_name_hints = yaml.safe_load(f)
    with open(os.path.join(DATA_PATH, "location_hints.txt"), "r") as f:
      self.location_hints = yaml.safe_load(f)
    
    # Define a dictionary mapping charts to their sunken treasure
    #
    # This will be used to check whether or not the chart leads to a junk item. If so, the chart itself can be
    # considered junk.
    self.chart_name_to_sunken_treasure = {}
    self.build_sunken_treasure_mapping()
    
    self.cached_required_locations_for_paths = {}
    self.cached_hinted_path_zones = []
    self.cached_hinted_path_items = []
    self.cached_hinted_barren_zones = []
    self.cached_hinted_item_locations = []
    self.cached_hinted_locations = []
  
  @staticmethod
  def get_hint_item_name_static(item_name):
    if item_name.startswith("Triforce Chart"):
      return "Triforce Chart"
    if item_name.startswith("Treasure Chart"):
      return "Treasure Chart"
    if item_name.endswith("Small Key"):
      return "Small Key"
    if item_name.endswith("Big Key"):
      return "Big Key"
    return item_name
  
  @staticmethod
  def get_formatted_hint_text_static(hint, prefix="They say that ", suffix=".", delay=30):
    if hint.type == HintType.PATH:
      hint_string = (
        "%san item found at \\{1A 06 FF 00 00 05}%s\\{1A 06 FF 00 00 00} is on the path to \\{1A 06 FF 00 00 01}%s\\{1A 06 FF 00 00 00}%s"
        % (prefix, hint.info1, hint.info2, suffix)
      )
    elif hint.type == HintType.BARREN:
      hint_string = (
        "%svisiting \\{1A 06 FF 00 00 03}%s\\{1A 06 FF 00 00 00} is a foolish choice%s"
        % (prefix, hint.info1, suffix)
      )
    elif hint.type == HintType.LOCATION:
      hint_string = (
        "%s\\{1A 06 FF 00 00 01}%s\\{1A 06 FF 00 00 00} rewards \\{1A 06 FF 00 00 01}%s\\{1A 06 FF 00 00 00}%s"
        % (prefix, hint.info1, hint.info2, suffix)
      )
    elif hint.type == HintType.ITEM:
      hint_string = (
        "%s\\{1A 06 FF 00 00 01}%s\\{1A 06 FF 00 00 00} is located in \\{1A 06 FF 00 00 01}%s\\{1A 06 FF 00 00 00}%s"
        % (prefix, hint.info1, hint.info2, suffix)
      )
    else:
      hint_string = ""
    
    # Cap delay to "FF"
    delay = min(delay, 255)
    
    # Add a wait command (delay) to prevent the player from skipping over the hint accidentally.
    if delay > 0:
      hint_string += "\\{1A 07 00 00 07 00 %02X}" % delay
    
    return hint_string
  
  
  def get_entrance_zone(self, location_name):
    # Helper function to return the entrance zone name for the location.
    #
    # For non-dungeon and non-cave locations, the entrance zone name is simply the zone name. However, when entrances
    # are randomized, the entrance zone name may not be the same as the zone name for dungeons and caves.
    # As a special case, if the entrance zone is Tower of the Gods or the location name is "Tower of the Gods - Sunken
    # Treasure", the entrance zone name is "Tower of the Gods Sector" to differentiate between the dungeon and the
    # entrance.
    
    zone_name, specific_location_name = self.logic.split_location_name_by_zone(location_name)
    
    # Distinguish between the two Pawprint Isle entrances
    if self.options.get("randomize_entrances") not in ["Disabled", "Dungeons", None] and location_name == "Pawprint Isle - Wizzrobe Cave":
      zone_name = "Pawprint Isle Side Isle"
    
    if zone_name in self.rando.dungeon_and_cave_island_locations and self.logic.is_dungeon_or_cave(location_name):
      # For dungeons and caves, look up the island where the entrance is
      entrance_zone = self.rando.dungeon_and_cave_island_locations[zone_name]
      if entrance_zone == "Tower of the Gods":
        entrance_zone = "Tower of the Gods Sector"
    else:
      # Otherwise, for non-interior locations, just use the island (zone) name
      entrance_zone = zone_name
      if location_name == "Tower of the Gods - Sunken Treasure":
        entrance_zone = "Tower of the Gods Sector"
      # Note that Forsaken Fortress - Sunken Treasure has a similar issue, but there are no randomized entrances on
      # Forsaken Fortress, so we won't make that distinction here
    return entrance_zone
  
  def build_sunken_treasure_mapping(self):
    # Helper function to create a mapping of treasure charts to their respective sunken treasure.
    
    self.chart_name_to_sunken_treasure = {}
    chart_name_to_island_number = {}
    for island_number in range(1, 49+1):
      chart_name = self.logic.macros["Chart for Island %d" % island_number][0]
      chart_name_to_island_number[chart_name] = island_number
    for chart_number in range(1, 49+1):
      if chart_number <= 8:
        chart_name = "Triforce Chart %d" % chart_number
      else:
        chart_name = "Treasure Chart %d" % (chart_number-8)
      island_number = chart_name_to_island_number[chart_name]
      island_name = self.rando.island_number_to_name[island_number]
      self.chart_name_to_sunken_treasure[chart_name] = "%s - Sunken Treasure" % island_name
  
  def check_location_required_for_paths(self, location_to_check, paths_to_check):
    # If the item is not a progress item, there's no way it's required
    item_name = self.logic.done_item_locations[location_to_check]
    if item_name not in self.logic.all_progress_items:
      return False
    
    # Effectively, to check whether the location is required or not, we simulate a playthrough and remove the item the
    # player would receive at that location immediately after they receive it. If the player can still fulfill the
    # requirement despite not having this item, the location is not required.
    logic = Logic(self.rando)
    previously_accessible_locations = []
    
    while logic.unplaced_progress_items:
      progress_items_in_this_sphere = OrderedDict()
      
      accessible_locations = logic.get_accessible_remaining_locations()
      locations_in_this_sphere = [
        loc for loc in accessible_locations
        if loc not in previously_accessible_locations
      ]
      if not locations_in_this_sphere:
        return {path_name: not logic.check_requirement_met(self.DUNGEON_NAME_TO_REQUIREMENT_NAME[path_name]) for path_name in paths_to_check}
      
      
      if not self.options.get("keylunacy"):
        # If the player gained access to any small keys, we need to give them the keys without counting that as a new sphere.
        newly_accessible_predetermined_item_locations = [
          loc for loc in locations_in_this_sphere
          if loc in self.logic.prerandomization_item_locations
        ]
        newly_accessible_small_key_locations = [
          loc for loc in newly_accessible_predetermined_item_locations
          if self.logic.prerandomization_item_locations[loc].endswith(" Small Key")
        ]
        if newly_accessible_small_key_locations:
          for small_key_location_name in newly_accessible_small_key_locations:
            item_name = self.logic.prerandomization_item_locations[small_key_location_name]
            assert item_name.endswith(" Small Key")
            
            logic.add_owned_item(item_name)
            # Remove small key from owned items if it was from the location we want to check
            if small_key_location_name == location_to_check:
              logic.currently_owned_items.remove(logic.clean_item_name(item_name))
          
          previously_accessible_locations += newly_accessible_small_key_locations
          continue # Redo this loop iteration with the small key locations no longer being considered 'remaining'.
      
      
      # Hide duplicated progression items (e.g. Empty Bottles) when they are placed in non-progression locations to avoid confusion and inconsistency.
      locations_in_this_sphere = logic.filter_locations_for_progression(locations_in_this_sphere)
      
      for location_name in locations_in_this_sphere:
        item_name = self.logic.done_item_locations[location_name]
        if item_name in logic.all_progress_items:
          progress_items_in_this_sphere[location_name] = item_name
      
      for location_name, item_name in progress_items_in_this_sphere.items():
        logic.add_owned_item(item_name)
        # Remove item from owned items if it was from the location we want to check
        if location_name == location_to_check:
          logic.currently_owned_items.remove(logic.clean_item_name(item_name))
      for group_name, item_names in logic.progress_item_groups.items():
        entire_group_is_owned = all(item_name in logic.currently_owned_items for item_name in item_names)
        if entire_group_is_owned and group_name in logic.unplaced_progress_items:
          logic.unplaced_progress_items.remove(group_name)
      
      previously_accessible_locations = accessible_locations
    
    return {path_name: not logic.check_requirement_met(self.DUNGEON_NAME_TO_REQUIREMENT_NAME[path_name]) for path_name in paths_to_check}
  
  def get_required_locations_for_paths(self):
    # If `self.WOTH_ONLY` is True, then the only path in the game is for Ganon's Tower. Otherwise, add all race-mode
    # dungeons as paths, in addition to Ganon's Tower.
    if self.WOTH_ONLY:
      dungeon_paths = []
      required_locations_for_paths = {"Ganon's Tower": []}
    else:
      dungeon_paths = self.rando.race_mode_required_dungeons.copy()
      required_locations_for_paths = {goal: [] for goal in ["Ganon's Tower"] + dungeon_paths}
    
    # Determine which locations are required to beat the seed.
    # 
    # Items are implicitly referred to by their location to handle duplicate item names (i.e., progressive items and
    # small keys). Basically, we remove the item from that location and see if the seed is still beatable. If not, then
    # we consider the item as required.
    progress_locations, non_progress_locations = self.logic.get_progress_and_non_progress_locations()
    for location_name in progress_locations:
      # Ignore race-mode-banned locations
      if location_name in self.rando.race_mode_banned_locations:
        continue
      
      # Build a list of required locations, along with the item at that location
      item_name = self.logic.done_item_locations[location_name]
      if (
        location_name not in self.rando.race_mode_required_locations            # Ignore boss Heart Containers in race mode, even if it's required
        and (self.options.get("keylunacy") or not item_name.endswith(" Key"))   # Keys are only considered in key-lunacy
        and item_name in self.logic.all_progress_items                          # Required locations always contain progress items (by definition)
      ):
        required_for_non_ganondorf_paths = False
        
        # Determine the item name for the given location
        zone_name, specific_location_name = self.logic.split_location_name_by_zone(location_name)
        entrance_zone = self.get_entrance_zone(location_name)
        item_tuple = (zone_name, entrance_zone, specific_location_name, item_name)
        
        # Check and record if the location is required for the dungeon paths
        requirements_met = self.check_location_required_for_paths(location_name, dungeon_paths)
        for dungeon_name, requirement_met in requirements_met.items():
          if requirement_met:
            required_for_non_ganondorf_paths = True
            required_locations_for_paths[dungeon_name].append(item_tuple)
        
        # Check and record if the location is required to beat the game
        if item_tuple not in required_locations_for_paths["Ganon's Tower"]:
          required_for_ganondorf = self.check_location_required_for_paths(location_name, ["Ganon's Tower"])["Ganon's Tower"]
          if required_for_non_ganondorf_paths or required_for_ganondorf:
            required_locations_for_paths["Ganon's Tower"].append((zone_name, entrance_zone, specific_location_name, item_name))
    
    return required_locations_for_paths
  
  def get_path_hint(self, unhinted_locations, hinted_locations, path_name):
    valid_path_hint = False
    while not valid_path_hint:
      # If there are no hintable locations, return `None`
      if len(unhinted_locations) == 0:
        return None, None
      
      # Pick a location uniformly at random from the list of hintable locations
      zone_name, entrance_zone, specific_location_name, item_name = self.rando.rng.choice(unhinted_locations)
      hinted_location = "%s - %s" % (zone_name, specific_location_name)
      
      # Regardless of whether we use the location, remove that location from being hinted
      unhinted_locations.remove((zone_name, entrance_zone, specific_location_name, item_name))
      
      # The location is a valid hint if it has not already been hinted at
      if hinted_location not in hinted_locations:
        valid_path_hint = True
      
    # Record hinted zone, item, and path goal.
    # If it's a dungeon, use the dungeon name. If it's a cave, use the entrance zone name.
    if zone_name in self.logic.DUNGEON_NAMES.values():
      if zone_name == "Tower of the Gods" and specific_location_name == "Sunken Treasure":
        # Special case: if location is Tower of the Gods - Sunken Treasure, use "Tower of the Gods Sector" as the hint
        return Hint(HintType.PATH, "Tower of the Gods Sector", self.DUNGEON_NAME_TO_BOSS_NAME[path_name]), hinted_location
      else:
        return Hint(HintType.PATH, zone_name, self.DUNGEON_NAME_TO_BOSS_NAME[path_name]), hinted_location
    else:
      return Hint(HintType.PATH, entrance_zone, self.DUNGEON_NAME_TO_BOSS_NAME[path_name]), hinted_location
  
  
  def determine_junk_items(self):
    # Helper method which returns a set of guaranteed unrequired items in the seed
    
    junk_items = set(self.logic.all_nonprogress_items)      # Start with all non-progress items in the seed
    junk_items |= set(CONSUMABLE_ITEMS)                     # Add consumables like Heart Containers and Rupees
    junk_items |= set(DUNGEON_NONPROGRESS_ITEMS)            # Add dungeon items (Dungeon Maps and Compasses)
    if not self.options.get("keylunacy"):
      junk_items |= set(DUNGEON_PROGRESS_ITEMS)             # Consider Small and Big Keys junk when key-lunacy is off
    
    # Consider Empty Bottles junk only if none are logical
    if "Empty Bottle" in self.rando.logic.all_progress_items and "Empty Bottle" in junk_items:
      junk_items.remove("Empty Bottle")
    # Consider Progressive Quiver junk only if none are logical
    if "Progressive Quiver" in self.rando.logic.all_progress_items and "Progressive Quiver" in junk_items:
      junk_items.remove("Progressive Quiver")
    # Consider Progressive Wallet junk only if none are logical
    if "Progressive Wallet" in self.rando.logic.all_progress_items and "Progressive Wallet" in junk_items:
      junk_items.remove("Progressive Wallet")
    
    # Consider Small and Big Keys for non-required race mode dungeons as junk when key-lunacy is on
    if self.options.get("race_mode") and self.options.get("keylunacy"):
      race_mode_banned_dungeons = set(self.logic.DUNGEON_NAMES.values()) - set(self.rando.race_mode_required_dungeons)

      if "Dragon Roost Cavern" in race_mode_banned_dungeons:
        junk_items.add("DRC Small Key")
        junk_items.add("DRC Big Key")
      if "Forbidden Woods" in race_mode_banned_dungeons:
        junk_items.add("FW Small Key")
        junk_items.add("FW Big Key")
      if "Tower of the Gods" in race_mode_banned_dungeons:
        junk_items.add("TotG Small Key")
        junk_items.add("TotG Big Key")
      if "Earth Temple" in race_mode_banned_dungeons:
        junk_items.add("ET Small Key")
        junk_items.add("ET Big Key")
      if "Wind Temple" in race_mode_banned_dungeons:
        junk_items.add("WT Small Key")
        junk_items.add("WT Big Key")
    
    # Special cases: loop here until the list of junk items stops changing
    junk_items_changed = True
    while junk_items_changed:
      junk_items_changed = False
      
      # Loop through charts when sunken treasure on and consider any charts that lead to immediately to junk as junk
      if self.options.get("progression_triforce_charts") or self.options.get("progression_treasure_charts"):
        for chart_name, sunken_treasure in self.chart_name_to_sunken_treasure.items():
          if chart_name not in junk_items:
            item_name = self.logic.done_item_locations[sunken_treasure]
            if item_name in junk_items:
              junk_items.add(chart_name)
              junk_items_changed = True
      
      # Check Maggie's and Moblin's Letters and if they lead to junk, consider them junk as well
      if self.options.get("progression_short_sidequests"):
        item_name = self.logic.done_item_locations["Windfall Island - Cafe Bar - Postman"]
        if "Maggie's Letter" not in junk_items and item_name in junk_items:
          junk_items.add("Maggie's Letter")
          junk_items_changed = True
        item_name = self.logic.done_item_locations["Windfall Island - Maggie - Delivery Reward"]
        if "Moblin's Letter" not in junk_items and item_name in junk_items:
          junk_items.add("Moblin's Letter")
          junk_items_changed = True
      
      # Check the two 12-eye octos and if both lead to junk, consider both quivers as junk
      if self.options.get("progression_big_octos_gunboats"):
        octo1_item_name = self.logic.done_item_locations["Tingle Island - Big Octo"]
        octo2_item_name = self.logic.done_item_locations["Seven-Star Isles - Big Octo"]
        if "Progressive Quiver" not in junk_items and octo1_item_name in junk_items and octo2_item_name in junk_items:
          junk_items.add("Progressive Quiver")
          junk_items_changed = True
      
      if self.options.get("progression_misc"):
        # Check Tingle statues
        item_name = self.logic.done_item_locations["Tingle Island - Ankle - Reward for All Tingle Statues"]
        if "Dragon Tingle Statue" not in junk_items and item_name in junk_items:
          junk_items.add("Dragon Tingle Statue")
          junk_items.add("Forbidden Tingle Statue")
          junk_items.add("Goddess Tingle Statue")
          junk_items.add("Earth Tingle Statue")
          junk_items.add("Wind Tingle Statue")
          junk_items_changed = True
        
        # Check Ghost Ship Chart
        if self.options.get("progression_misc"):
          item_name = self.logic.done_item_locations["The Great Sea - Ghost Ship"]
          if "Ghost Ship Chart" not in junk_items and item_name in junk_items:
            junk_items.add("Ghost Ship Chart")
            junk_items_changed = True
        
    return junk_items
  
  def get_barren_zones(self, progress_locations):
    # Helper function to build a list of barren zones in this seed.
    # The list includes only zones which are allowed to be hinted at as barren.
    
    # To determine a list of candidate barren zones, we first construct a list of guaranteed junk items. The remaining
    # set of items may or may not be required, so the zones that contain them won't be hinted barren. We do this because
    # the player may have multiple paths to beat the seed. So if we only used non-path locations, we may hint at all
    # paths as barren (since one particular path is not strictly required).
    # Technically, this is an overestimate (a superset) of actual barren locations, but it should suffice.
    junk_items = self.determine_junk_items()
    
    # We don't want to have barren/always hints overlap if hints are on.
    # For instance, consider a Ganon's Tower always hint. If you get that hint and a barren hint for Ganon's Tower, it's
    # effectively the same hint. However, if there's a Blue Chu Jelly hint, a Windfall barren hint would still be
    # helpful since Green Chu Jelly is at least another check on Windfall.
    always_hint_locations = []
    if self.USE_ALWAYS_HINTS:
      always_hint_locations = list(filter(
        lambda location_name: location_name in self.location_hints
        and self.location_hints[location_name]["Type"] == "Always",
        progress_locations,
      ))
    
    # Initialize possibly-required zones to all logical zones in this seed
    # `possibly_required_zones` contains a mapping of zones -> possibly-required items
    # `possibly_required_zones_no_always` contains a mapping of zones with always locations ignored -> possibly-required items
    possibly_required_zones = {}
    possibly_required_zones_no_always = {}
    for location_name in progress_locations:
      zone_name, specific_location_name = self.logic.split_location_name_by_zone(location_name)
      
      # Consider dungeons as a separate zone
      key_name = ""
      if zone_name in self.logic.DUNGEON_NAMES.values():
        if location_name == "Tower of the Gods - Sunken Treasure":
          key_name = "Tower of the Gods Sector"
        else:
          key_name = zone_name
      else:
        entrance_zone = self.get_entrance_zone(location_name)
        key_name = entrance_zone
      
      possibly_required_zones[key_name] = set()
      if location_name not in always_hint_locations:
        possibly_required_zones_no_always[key_name] = set()
    
    # Loop through all progress locations, recording only possibly-required items in our dictionary
    for location_name in progress_locations:
      item_name = self.logic.done_item_locations[location_name]
      if location_name not in self.rando.race_mode_required_locations and item_name not in junk_items:
        zone_name, specific_location_name = self.logic.split_location_name_by_zone(location_name)
        
        # Consider dungeons as a separate zone
        if zone_name in self.logic.DUNGEON_NAMES.values():
          if location_name == "Tower of the Gods - Sunken Treasure":
            possibly_required_zones["Tower of the Gods Sector"].add(item_name)
          else:
            possibly_required_zones[zone_name].add(item_name)
        else:
          entrance_zone = self.get_entrance_zone(location_name)
          possibly_required_zones[entrance_zone].add(item_name)
        
        # Include dungeon-related mail with its dungeon, in addition to Mailbox
        if location_name == "Mailbox - Letter from Baito":
          possibly_required_zones["Earth Temple"].add(item_name)
          entrance_zone = self.get_entrance_zone("Earth Temple - Jalhalla Heart Container")
          if entrance_zone in possibly_required_zones:
            possibly_required_zones[entrance_zone].add(item_name)
        if location_name == "Mailbox - Letter from Orca":
          possibly_required_zones["Forbidden Woods"].add(item_name)
          entrance_zone = self.get_entrance_zone("Forbidden Woods - Kalle Demos Heart Container")
          if entrance_zone in possibly_required_zones:
            possibly_required_zones[entrance_zone].add(item_name)
        if location_name == "Mailbox - Letter from Aryll" or location_name == "Mailbox - Letter from Tingle":
          possibly_required_zones["Forsaken Fortress"].add(item_name)
    
    # The zones with zero possibly-required items makes up our initial set of barren zones.
    # We also check whether there are any non-always hinted locations there. If not, then don't hint at that zone since
    # it'd be covered already by the always hint(s).
    barren_zones = list(filter(
      lambda x: x[0] in possibly_required_zones_no_always and len(x[1]) == 0,
      possibly_required_zones.items()
    ))
    barren_zones = set(zone_name for zone_name, empty_set in barren_zones)
    
    # Prevent the entrances of possibly-required dungeons from being hinted at as barren
    possibly_required_dungeons = list(filter(
      lambda x: len(x[1]) != 0
      and x[0] in self.logic.DUNGEON_NAMES.values(),
      possibly_required_zones.items(),
    ))
    for dungeon_name, items_set in possibly_required_dungeons:
      if dungeon_name == "Dragon Roost Cavern":
        entrance_zone = self.get_entrance_zone("Dragon Roost Cavern - Gohma Heart Container")
        barren_zones.discard(entrance_zone)
      if dungeon_name == "Forbidden Woods":
        entrance_zone = self.get_entrance_zone("Forbidden Woods - Kalle Demos Heart Container")
        barren_zones.discard(entrance_zone)
      if dungeon_name == "Tower of the Gods":
        entrance_zone = self.get_entrance_zone("Tower of the Gods - Gohdan Heart Container")
        barren_zones.discard(entrance_zone)
      if dungeon_name == "Earth Temple":
        entrance_zone = self.get_entrance_zone("Earth Temple - Jalhalla Heart Container")
        barren_zones.discard(entrance_zone)
      if dungeon_name == "Wind Temple":
        entrance_zone = self.get_entrance_zone("Wind Temple - Molgera Heart Container")
        barren_zones.discard(entrance_zone)
    
    # Remove race-mode banned dungeons from being hinted at as barren
    if self.options.get("race_mode"):
      race_mode_banned_dungeons = set(self.logic.DUNGEON_NAMES.values()) - set(self.rando.race_mode_required_dungeons)
      barren_zones = barren_zones - race_mode_banned_dungeons
    
    # Return the list of barren zones sorted to maintain consistent ordering
    return list(sorted(barren_zones))
  
  def get_barren_hint(self, unhinted_zones, zone_weights):
    # If there are no hintable locations, return `None`
    if len(unhinted_zones) == 0:
      return None
    
    # Remove a barren zone at random from the list, using the weights provided
    zone_name = self.rando.rng.choices(unhinted_zones, weights=zone_weights)[0]
    unhinted_zones.remove(zone_name)
    
    return Hint(HintType.BARREN, zone_name)
  
  
  def filter_legal_item_hint(self, location_name, progress_locations, previously_hinted_locations):
    # Some location like the Great Sea or dungeons are invalid for item hints
    entrance_zone = self.get_entrance_zone(location_name)
    if entrance_zone == "Tower of the Gods Sector":
      entrance_zone = "Tower of the Gods"
    
    return (
      # Don't hint at non-progress items
      self.logic.done_item_locations[location_name] in self.logic.all_progress_items and
      
      # Don't hint at item in non-progress locations
      location_name in progress_locations and
      
      # Don't hint at dungeon maps and compasses, and don't hint at dungeon keys when key-lunacy is not enabled
      (self.options.get("keylunacy") or not self.logic.is_dungeon_item(self.logic.done_item_locations[location_name])) and
      
      # You already know which boss locations have a required item and which don't in race mode by looking at the sea chart.
      location_name not in self.rando.race_mode_required_locations and
      
      # Only create hints for locations that are hintable (not Great Sea, Mailbox, or Hyrule)
      entrance_zone in self.island_name_hints and
      
      # Remove locations that are included in always hints
      not (location_name in self.location_hints and self.location_hints[location_name]["Type"] == "Always") and
      
      # Remove locations in race-mode banned dungeons
      location_name not in self.rando.race_mode_banned_locations and
      
      # Remove locations for items that were previously hinted
      location_name not in previously_hinted_locations
    )
  
  def get_legal_item_hints(self, progress_locations, hinted_barren_zones, previously_hinted_locations):
    # Helper function to build a list of locations which may be hinted as item hints in this seed.
    
    # Filter out locations which are invalid to be hinted at for item hints
    hintable_locations = list(filter(lambda location_name: self.filter_legal_item_hint(
      location_name, progress_locations, previously_hinted_locations), self.logic.done_item_locations.keys()))
    
    # Remove locations in hinted barren areas
    new_hintable_locations = []
    barrens = [hint.info1 for hint in hinted_barren_zones]
    for location_name in hintable_locations:
      # Catch Mailbox cases
      if (
          (location_name == "Mailbox - Letter from Baito" and "Earth Temple" in barrens)
          or (location_name == "Mailbox - Letter from Orca" and "Forbidden Woods" in barrens)
          or (location_name == "Mailbox - Letter from Aryll" and "Forsaken Fortress" in barrens)
          or (location_name == "Mailbox - Letter from Tingle" and "Forsaken Fortress" in barrens)
      ):
        continue
      
      # Catch locations which are hinted at in barren dungeons
      zone_name, specific_location_name = self.logic.split_location_name_by_zone(location_name)
      if zone_name in self.logic.DUNGEON_NAMES.values() and zone_name in barrens:
        continue
      
      # Catch locations which are hinted at in barren zones
      entrance_zone = self.get_entrance_zone(location_name)
      if entrance_zone not in barrens:
        new_hintable_locations.append(location_name)
    
    return new_hintable_locations
  
  def get_item_hint(self, hintable_locations, priority=[]):
    # If there are no hintable locations, return `None`
    if len(hintable_locations) == 0 and len(priority) == 0:
      return None
    
    # Pick a location at which to hint at random
    if len(priority) > 0:
      location_name = self.rando.rng.choice(priority)
      priority.remove(location_name)
    else:
      location_name = self.rando.rng.choice(hintable_locations)
      hintable_locations.remove(location_name)
    
    item_name = self.logic.done_item_locations[location_name]
    entrance_zone = self.get_entrance_zone(location_name)
    
    # Simplify entrance zone name
    if entrance_zone == "Tower of the Gods Sector":
      entrance_zone = "Tower of the Gods"
    
    return Hint(HintType.ITEM, item_name, entrance_zone), location_name
  
  
  def get_legal_location_hints(self, progress_locations, hinted_barren_zones, previously_hinted_locations):
    # Helper function to build a list of locations which may be hinted as location hints in this seed.
    
    hintable_locations = list(filter(lambda loc: loc in self.location_hints.keys(), progress_locations))
    
    # Identify valid always hints for this seed
    always_hintable_locations = list(filter(lambda loc: self.location_hints[loc]["Type"] == "Always", hintable_locations))
    # The remaining locations are potential sometimes hints
    hintable_locations = list(filter(lambda loc: self.location_hints[loc]["Type"] == "Sometimes", hintable_locations))
    
    # If we're not using always hints, consider them as sometimes hints instead
    if not self.USE_ALWAYS_HINTS:
      hintable_locations += always_hintable_locations
      always_hintable_locations = []
    
    # Remove locations in race-mode banned dungeons
    hintable_locations = list(filter(lambda location_name: location_name not in self.rando.race_mode_banned_locations, hintable_locations))
    
    # Remove locations for items that were previously hinted
    hintable_locations = list(filter(lambda loc: loc not in previously_hinted_locations, hintable_locations))
    
    # Remove locations in hinted barren areas
    sometimes_hintable_locations = []
    barrens = [hint.info1 for hint in hinted_barren_zones]
    for location_name in hintable_locations:
      # Catch Mailbox cases
      if (
          (location_name == "Mailbox - Letter from Baito" and "Earth Temple" in barrens)
          or (location_name == "Mailbox - Letter from Orca" and "Forbidden Woods" in barrens)
          or (location_name == "Mailbox - Letter from Aryll" and "Forsaken Fortress" in barrens)
          or (location_name == "Mailbox - Letter from Tingle" and "Forsaken Fortress" in barrens)
      ):
        continue
      
      # Catch locations which are hinted at in barren dungeons
      zone_name, specific_location_name = self.logic.split_location_name_by_zone(location_name)
      if zone_name in self.logic.DUNGEON_NAMES.values() and zone_name in barrens:
        continue
      
      # Catch locations which are hinted at in barren zones
      entrance_zone = self.get_entrance_zone(location_name)
      if entrance_zone not in barrens:
        sometimes_hintable_locations.append(location_name)
    
    return always_hintable_locations, sometimes_hintable_locations
  
  def get_location_hint(self, hintable_locations):
    # If there are no hintable locations, return `None`
    if len(hintable_locations) == 0:
      return None
    
    # Pick a location at which to hint at random
    location_name = self.rando.rng.choice(hintable_locations)
    hintable_locations.remove(location_name)
    
    # Apply cryptic text to the location name, if the option is selected
    item_name = self.logic.done_item_locations[location_name]
    if not self.CLEARER_HINTS:
      location_name = self.location_hints[location_name]["Text"]
    
    return Hint(HintType.LOCATION, location_name, item_name)
  
  
  def generate_octo_fairy_hint(self):
    # Get an item hint for a random progress item
    # Note that this hint is completely independant of all other hints
    hintable_locations = self.get_legal_item_hints(self.logic.done_item_locations, [], [])
    
    if len(hintable_locations) == 0:
      raise Exception("No valid items to give hints for")
    
    item_hint, location_name = self.get_item_hint(hintable_locations)
    # We don't want this Great Fairy to hint at her own item.
    if location_name == "Two-Eye Reef - Big Octo Great Fairy":
      item_hint, location_name = self.get_item_hint(hintable_locations)
    
    # Always use cryptic text for the octo fairy hint
    item_hint.info1 = self.progress_item_hints[Hints.get_hint_item_name_static(item_hint.info1)]
    item_hint.info2 = self.island_name_hints[item_hint.info2]
    
    return item_hint
  
  def generate_savage_labyrinth_hints(self):
    # Get an item hint for the two checks in Savage Labyrinth
    floor_30_item_name = self.logic.done_item_locations["Outset Island - Savage Labyrinth - Floor 30"]
    floor_50_item_name = self.logic.done_item_locations["Outset Island - Savage Labyrinth - Floor 50"]
  
    floor_30_is_progress = (floor_30_item_name in self.logic.all_progress_items)
    floor_50_is_progress = (floor_50_item_name in self.logic.all_progress_items)
    
    floor_30_item_name = Hints.get_hint_item_name_static(floor_30_item_name)
    floor_50_item_name = Hints.get_hint_item_name_static(floor_50_item_name)
    
    if floor_30_is_progress and not floor_30_item_name in self.progress_item_hints:
      raise Exception("Could not find progress item hint for item: %s" % floor_30_item_name)
    if floor_50_is_progress and not floor_50_item_name in self.progress_item_hints:
      raise Exception("Could not find progress item hint for item: %s" % floor_50_item_name)
    
    floor_30_hint = None
    if floor_30_is_progress:
      floor_30_hint = Hint(HintType.ITEM, self.progress_item_hints[floor_30_item_name], None)
    floor_50_hint = None
    if floor_50_is_progress:
      floor_50_hint = Hint(HintType.ITEM, self.progress_item_hints[floor_50_item_name], None)
    
    return floor_30_hint, floor_50_hint
  
  def generate_hints(self):
    # Reset cached lists
    self.cached_required_locations_for_paths = {}
    self.cached_hinted_path_zones = []
    self.cached_hinted_path_items = []
    self.cached_hinted_barren_zones = []
    self.cached_hinted_item_locations = []
    self.cached_hinted_locations = []
    
    # Create a mapping for chart name -> sunken treasure
    self.build_sunken_treasure_mapping()
    
    # Build of list of progress locations for this seed
    progress_locations, non_progress_locations = self.logic.get_progress_and_non_progress_locations()
    
    # Ignore sunken treasure for now
    progress_locations = list(filter(lambda location_name: not location_name.endswith(" - Sunken Treasure"), progress_locations))
    
    # Remove user-excluded locations from consideration
    excluded_locations = []
    for location_name in self.options.get("excluded_locations"):
      # Leave locations that have dungeon keys in, so we can possibly hint at them for location hints
      item_name = self.logic.done_item_locations[location_name]
      if self.options.get("keylunacy") or not item_name.endswith(" Key"):
        excluded_locations.append(location_name)
    progress_locations = list(filter(lambda location_name: location_name not in excluded_locations, progress_locations))
    
    # Add back sunken treasure for charts that are in logic
    if self.options.get("progression_triforce_charts"):
      for chart_number in range(1, 1+self.rando.options.get("num_triforce_charts_in_logic", 0)):
        progress_locations.append(self.chart_name_to_sunken_treasure["Triforce Chart %d" % chart_number])
    if self.options.get("progression_treasure_charts"):
      for chart_number in range(1, 1+self.rando.options.get("num_treasure_charts_in_logic", 0)):
        progress_locations.append(self.chart_name_to_sunken_treasure["Treasure Chart %d" % chart_number])
    
    # Get all entrance zones for progress locations in this seed
    all_world_areas = []
    for location_name in progress_locations:
      if self.logic.is_dungeon_location(location_name):
        zone_name, specific_location_name = self.logic.split_location_name_by_zone(location_name)
        all_world_areas.append(zone_name)
      else:
        all_world_areas.append(self.get_entrance_zone(location_name))
    
    # Get a counter for the number of locations associated with each zone, used for weighing
    location_counter = Counter(all_world_areas)
    
    # Determine which locations are required for each path goal
    # Items are implicitly referred to by their location to handle duplicate item names (i.e., progressive items and
    # small keys). Basically, we remove the item from that location and see if the path goal is still achievable. If
    # not, then we consider the item as required.
    required_locations_for_paths = []
    if self.MAX_PATH_HINTS > 0:
      required_locations_for_paths = self.get_required_locations_for_paths()
      self.cached_required_locations_for_paths = copy.deepcopy(required_locations_for_paths)
    
    # Generate path hints
    # We hint at max `self.MAX_PATH_HINTS` zones at random. We start by hinted each of the race mode dungeons once.
    # After that, we repeatedly select a path goal at random and use that to form another hint. Zones are weighted by
    # the number of required locations at that zone. The more required locations, the more likely that zone will be
    # chosen.
    dungeon_paths = self.rando.race_mode_required_dungeons.copy()
    self.rando.rng.shuffle(dungeon_paths)
    
    hinted_path_zones = []
    previously_hinted_locations = []
    
    # Generate a path hint for each race-mode dungeon. If `self.WOTH_ONLY` is True, skip this step
    if not self.WOTH_ONLY:
      for dungeon_name in dungeon_paths:
        # If there are no hintable locations for path hints, skip to barren hints
        if len(required_locations_for_paths) == 0:
          break
        
        if len(hinted_path_zones) < self.MAX_PATH_HINTS:
          path_hint, location_name = self.get_path_hint(required_locations_for_paths[dungeon_name], previously_hinted_locations, dungeon_name)
          
          # Unable to generate a path hint for the dungeon, so remove path goal and move on to the next
          if path_hint is None:
            del required_locations_for_paths[dungeon_name]
            continue
          
          # Remove locations that are hinted in always hints from being hinted path
          if not self.USE_ALWAYS_HINTS or (location_name not in self.location_hints or self.location_hints[location_name]["Type"] != "Always"):
            hinted_path_zones.append(path_hint)
            previously_hinted_locations.append(location_name)
            self.cached_hinted_path_items.append((self.logic.done_item_locations[location_name], location_name))
    
    while len(required_locations_for_paths) > 0 and len(hinted_path_zones) < self.MAX_PATH_HINTS:
      path_name = self.rando.rng.choice(list(required_locations_for_paths.keys()))
      path_hint, location_name = self.get_path_hint(required_locations_for_paths[path_name], previously_hinted_locations, path_name)
      
      # Unable to generate a path hint for the dungeon, so remove path goal
      if path_hint is None:
        del required_locations_for_paths[path_name]
      else:
        # Remove locations that are hinted in always hints from being hinted path
        if not self.USE_ALWAYS_HINTS or (location_name not in self.location_hints or self.location_hints[location_name]["Type"] != "Always"):
          hinted_path_zones.append(path_hint)
          previously_hinted_locations.append(location_name)
          self.cached_hinted_path_items.append((self.logic.done_item_locations[location_name], location_name))
    
    self.cached_hinted_path_zones = copy.deepcopy(hinted_path_zones)
    
    # Generate barren hints
    # We select at most `self.MAX_BARREN_HINTS` zones at random to hint as barren. Barren zones are weighted by the
    # square root of the number of locations at that zone.
    unhinted_barren_zones = self.get_barren_zones(progress_locations)
    hinted_barren_zones = []
    while len(unhinted_barren_zones) > 0 and len(hinted_barren_zones) < self.MAX_BARREN_HINTS:
      # Weigh each barren zone by the square root of the number of locations there
      zone_weights = [sqrt(location_counter[zone]) for zone in unhinted_barren_zones]
      
      barren_hint = self.get_barren_hint(unhinted_barren_zones, zone_weights)
      if barren_hint is not None:
        hinted_barren_zones.append(barren_hint)
    
    self.cached_hinted_barren_zones = copy.deepcopy(hinted_barren_zones)
    
    # Generate item hints
    # We select at most `self.MAX_ITEM_HINTS` items at random to hint at. We do not want to hint at items already
    # covered by the path hints, nor do we want to hint at items in barren-hinted locations.
    hintable_locations = self.get_legal_item_hints(progress_locations, hinted_barren_zones, previously_hinted_locations)
    
    # For `NO_DUNGEON_PATHS` hint priority, generate a set of items that are on dungeon paths
    items_on_dungeon_paths = set()
    if self.ITEM_HINT_PRIORITY == ItemHintPriority.NO_DUNGEON_PATHS:
      for path_name, path_locations in required_locations_for_paths.items():
        if path_name == "Ganon's Tower":
          continue
        for zone_name, entrance_zone, specific_location_name, item_name in path_locations:
          items_on_dungeon_paths.add((item_name, "%s - %s" % (zone_name, specific_location_name)))
    
    # Determine which locations are prioritized when generating item hints
    prioritized_hintable_locations = []
    remaining_hintable_locations = []
    if self.ITEM_HINT_PRIORITY == ItemHintPriority.NONE:
      remaining_hintable_locations = hintable_locations
    else:
      for location_name in hintable_locations:
        item_name = self.logic.done_item_locations[location_name]
        
        if self.ITEM_HINT_PRIORITY == ItemHintPriority.ICE_RODS:
          if item_name == "Progressive Sword" or item_name.startswith("Triforce Shard "):
            prioritized_hintable_locations.append(location_name)
          else:
            remaining_hintable_locations.append(location_name)
        if self.ITEM_HINT_PRIORITY == ItemHintPriority.NO_DUNGEON_PATHS:
          if (item_name, location_name) in items_on_dungeon_paths:
            remaining_hintable_locations.append(location_name)
          else:
            prioritized_hintable_locations.append(location_name)
    
    hinted_item_locations = []
    while len(hintable_locations) > 0 and len(hinted_item_locations) < self.MAX_ITEM_HINTS:
      item_hint, location_name = self.get_item_hint(remaining_hintable_locations, priority=prioritized_hintable_locations)
      
      # Apply cryptic text, if the option is selected
      if not self.CLEARER_HINTS:
        item_hint.info1 = self.progress_item_hints[Hints.get_hint_item_name_static(item_hint.info1)]
        item_hint.info2 = self.island_name_hints[item_hint.info2]
      
      hinted_item_locations.append(item_hint)
      previously_hinted_locations.append(location_name)
    
    self.cached_hinted_item_locations = copy.deepcopy(hinted_item_locations)
    
    # Generate location hints
    # We try to generate location hints until we get to `self.TOTAL_NUM_HINTS` total hints, but if there are not enough
    # valid hintable locations, then we have no choice but to return less than the desired amount of hints.
    always_hintable_locations, sometimes_hintable_locations = self.get_legal_location_hints(progress_locations, hinted_barren_zones, previously_hinted_locations)
    hinted_locations = []
    remaining_hints_desired = self.TOTAL_NUM_HINTS - len(hinted_path_zones) - len(hinted_barren_zones) - len(hinted_item_locations)
    
    # Start by exhausting the list of always hints
    while len(always_hintable_locations) > 0 and remaining_hints_desired > 0:
      remaining_hints_desired -= 1
      location_hint = self.get_location_hint(always_hintable_locations)
      hinted_locations.append(location_hint)
    
    # Fill out the remaining hint slots with sometimes hints
    while len(sometimes_hintable_locations) > 0 and remaining_hints_desired > 0:
      remaining_hints_desired -= 1
      location_hint = self.get_location_hint(sometimes_hintable_locations)
      hinted_locations.append(location_hint)
    
    self.cached_hinted_locations = copy.deepcopy(hinted_locations)
    
    return hinted_path_zones + hinted_barren_zones + hinted_item_locations + hinted_locations
