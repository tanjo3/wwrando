
import os
from collections import OrderedDict
from enum import Enum

import yaml
from wwrando_paths import DATA_PATH

from logic.logic import Logic


class HintType(Enum):
  WOTH = 0
  BARREN = 1
  LOCATION = 2
  ITEM = 3
  JUNK = 100

class Hint:
  def __init__(self, type, item, location):
    self.type = type
    self.item = item
    self.location = location
  
  def __str__(self):
    return "%s <Item: %s, Location: %s>" % (str(self.type), self.item, self.location)
  
  def __hash__(self):
    return hash(str(self))
  
  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return (self.type == other.type) and (self.item == other.item) and (self.location == other.location)
    else:
      return False

class Hints:
  # When these items are placed in a seed, they are always logically required regardless of settings
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
  
  # Define constants for WotH-style distribution of hints
  TOTAL_WOTH_STYLE_HINTS = 15
  MAX_WOTH_HINTS = 5
  MAX_WOTH_DUNGEONS = 2
  MAX_BARREN_HINTS = 3
  MAX_BARREN_DUNGEONS = 1
  
  def __init__(self, rando):
    self.rando = rando
    
    with open(os.path.join(DATA_PATH, "progress_item_hints.txt"), "r") as f:
      self.progress_item_hints = yaml.safe_load(f)
    
    with open(os.path.join(DATA_PATH, "island_name_hints.txt"), "r") as f:
      self.island_name_hints = yaml.safe_load(f)
    
    with open(os.path.join(DATA_PATH, "location_hints.txt"), "r") as f:
      self.location_hints = yaml.safe_load(f)
  
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
  
  def check_location_required(self, location_to_check):
    # Optimization 1: If the item at the location is hard-required every seed, the location is trivially required
    if self.rando.logic.done_item_locations[location_to_check] in self.HARD_REQUIRED_ITEMS:
      return True
    
    # Effectively, to check whether the location is required or not, we simulate a playthrough and remove the item the
    # player would receive at that location immediately after they receive. If the player is still able to beat the game
    # despite not having this item, the location is not required.
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
        return not logic.check_requirement_met("Can Reach and Defeat Ganondorf")
      
      
      if not self.rando.options.get("keylunacy"):
        # If the player gained access to any small keys, we need to give them the keys without counting that as a new sphere.
        newly_accessible_predetermined_item_locations = [
          loc for loc in locations_in_this_sphere
          if loc in self.rando.logic.prerandomization_item_locations
        ]
        newly_accessible_small_key_locations = [
          loc for loc in newly_accessible_predetermined_item_locations
          if self.rando.logic.prerandomization_item_locations[loc].endswith(" Small Key")
        ]
        if newly_accessible_small_key_locations:
          for small_key_location_name in newly_accessible_small_key_locations:
            item_name = self.rando.logic.prerandomization_item_locations[small_key_location_name]
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
        item_name = self.rando.logic.done_item_locations[location_name]
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
    
    return not logic.check_requirement_met("Can Reach and Defeat Ganondorf")
  
  def generate_item_hints(self):
    hints = []
    unique_items_given_hint_for = []
    possible_item_locations = list(self.rando.logic.done_item_locations.keys())
    self.rando.rng.shuffle(possible_item_locations)
    num_fishman_hints = 15
    desired_num_hints = 1 + num_fishman_hints
    min_num_hints_needed = 1 + 1
    while True:
      if not possible_item_locations:
        if len(hints) >= min_num_hints_needed:
          break
        elif len(hints) >= 1:
          # Succeeded at making at least 1 hint but not enough to reach the minimum.
          # So duplicate the hint(s) we DID make to fill up the missing slots.
          unique_hints = hints.copy()
          while len(hints) < min_num_hints_needed:
            hints += unique_hints
          hints = hints[:min_num_hints_needed]
          break
        else:
          raise Exception("No valid items to give hints for")
      
      location_name = possible_item_locations.pop()
      if location_name in self.rando.race_mode_required_locations:
        # You already know which boss locations have a required item and which don't in race mode by looking at the sea chart.
        continue
      if location_name == "Two-Eye Reef - Big Octo Great Fairy":
        # We don't want this Great Fairy to hint at her own item.
        continue
      
      item_name = self.rando.logic.done_item_locations[location_name]
      if item_name not in self.rando.logic.all_progress_items:
        continue
      if self.rando.logic.is_dungeon_item(item_name) and not self.rando.options.get("keylunacy"):
        continue
      
      item_name = Hints.get_hint_item_name_static(item_name)
      if item_name == "Bait Bag":
        # Can't access fishmen hints until you already have the bait bag
        continue
      if len(hints) >= desired_num_hints:
        break
      
      zone_name, specific_location_name = self.rando.logic.split_location_name_by_zone(location_name)
      is_dungeon = "Dungeon" in self.rando.logic.item_locations[location_name]["Types"]
      is_puzzle_cave = "Puzzle Secret Cave" in self.rando.logic.item_locations[location_name]["Types"]
      is_combat_cave = "Combat Secret Cave" in self.rando.logic.item_locations[location_name]["Types"]
      is_savage = "Savage Labyrinth" in self.rando.logic.item_locations[location_name]["Types"]
      if zone_name in self.rando.dungeon_and_cave_island_locations and (is_dungeon or is_puzzle_cave or is_combat_cave or is_savage):
        # If the location is in a dungeon or cave, use the hint for whatever island the dungeon/cave is located on.
        island_name = self.rando.dungeon_and_cave_island_locations[zone_name]
      elif zone_name in self.island_name_hints:
        island_name = zone_name
      elif zone_name in self.rando.logic.DUNGEON_NAMES.values():
        continue
      else:
        continue
      
      new_item_hint = Hint(HintType.ITEM, item_name, island_name)
      if new_item_hint in unique_items_given_hint_for: # Don't give hint for same type of item in same zone
        continue
      
      hints.append(new_item_hint)
      unique_items_given_hint_for.append(new_item_hint)
    
    return hints
  
  def generate_woth_style_hints(self):
    # Determine which locations are required to beat the seed
    # Items are implicitly referred to by their location to handle duplicate item names (i.e., progressive items and
    # small keys). Basically, we remove the item from that location and see if the seed is still beatable. If not, then
    # we consider the item as required.
    required_locations = []
    progress_locations, non_progress_locations = self.rando.logic.get_progress_and_non_progress_locations()
    for location_name in progress_locations:
        # Ignore race-mode-banned locations
        if location_name in self.rando.race_mode_banned_locations:
          continue
        
        # Build a list of required locations, along with the item at that location
        item_name = self.rando.logic.done_item_locations[location_name]
        if (
            location_name not in self.rando.race_mode_required_locations                  # Ignore boss Heart Containers in race mode, even if it's required
            and (self.rando.options.get("keylunacy") or not item_name.endswith(" Key"))   # Keys are only considered in key-lunacy
            and item_name in self.rando.logic.all_progress_items                          # Required locations always contain required items (by definition)
            and self.rando.hints.check_location_required(location_name)                   # Check if this exact location is required (to account for duplicate items)
        ):
            zone_name, specific_location_name = self.rando.logic.split_location_name_by_zone(location_name)
            is_dungeon = "Dungeon" in self.rando.logic.item_locations[location_name]["Types"]
            is_puzzle_cave = "Puzzle Secret Cave" in self.rando.logic.item_locations[location_name]["Types"]
            is_combat_cave = "Combat Secret Cave" in self.rando.logic.item_locations[location_name]["Types"]
            is_savage = "Savage Labyrinth" in self.rando.logic.item_locations[location_name]["Types"]

            if zone_name in self.rando.dungeon_and_cave_island_locations and (is_dungeon or is_puzzle_cave or is_combat_cave or is_savage):
              entrance_zone = self.rando.dungeon_and_cave_island_locations[zone_name]
              # Special case: if the entrance is Tower of the Gods, call the entrance zone "Tower of the Gods Sector" to
              # differentiate between the dungeon and the entrance
              if entrance_zone == "Tower of the Gods":
                entrance_zone = "Tower of the Gods Sector"
            else:
              entrance_zone = zone_name
              # Special case: if location is Tower of the Gods - Sunken Treasure, call the entrance zone "Tower of the
              # Gods Sector" to differentiate between the dungeon and the entrance
              if zone_name == "Tower of the Gods" and specific_location_name == "Sunken Treasure":
                entrance_zone = "Tower of the Gods Sector"
              # Note that Forsaken Fortress - Sunken Treasure has a similar issue, but there are no randomized entrances
              # on Forsaken Fortress, so we won't make that distinction here
            
            required_locations.append((zone_name, entrance_zone, specific_location_name, item_name))
    
    # Generate WOTH hints
    # We select at most three zones at random to hint as WOTH. At max, `self.MAX_WOTH_HINTS` dungeons may be hinted
    # WOTH. Zones are weighted by the number of required locations at that zone. The more required locations, the more
    # likely that zone will be chosen.
    unhinted_woth_locations = required_locations.copy()
    hinted_woth_zones = []
    num_dungeons_hinted_woth = 0
    previously_hinted_locations = []
    while len(unhinted_woth_locations) > 0 and len(hinted_woth_zones) < self.MAX_WOTH_HINTS:
      zone_name, entrance_zone, specific_location_name, item_name = self.rando.rng.choice(unhinted_woth_locations)
      
      # Regardless of whether we use the location, remove that locations from being hinted
      unhinted_woth_locations.remove((zone_name, entrance_zone, specific_location_name, item_name))
      
      # Create hint for dungeon only if we have room for another dungeon hint, otherwise skip
      # Also, sunken treasure location don't count to catch for Tower of the Gods and Forsaken Fortress
      if zone_name in self.rando.logic.DUNGEON_NAMES.values() and specific_location_name != "Sunken Treasure":
          if num_dungeons_hinted_woth < self.MAX_WOTH_DUNGEONS:
            num_dungeons_hinted_woth += 1
          else:
            continue
      
      # Record hinted zone and item. If it's a dungeon, use the dungeon name. If it's a cave, use the entrance zone name.
      if zone_name in self.rando.logic.DUNGEON_NAMES.values():
        if zone_name == "Tower of the Gods" and specific_location_name == "Sunken Treasure":
          # Special case: if location is Tower of the Gods - Sunken Treasure, use "Tower of the Gods Sector" as the hint
          hinted_woth_zones.append(Hint(HintType.WOTH, None, "Tower of the Gods Sector"))
        else:
          hinted_woth_zones.append(Hint(HintType.WOTH, None, zone_name))
      else:
        hinted_woth_zones.append(Hint(HintType.WOTH, None, entrance_zone))
      previously_hinted_locations.append("%s - %s" % (zone_name, specific_location_name))
    
    # Identify zones which do not contain required items
    # We start will all zones, plus a "Tower of the Gods Sector" zone to differentiate between the dungeon and the entrance/sector
    all_world_areas = set(self.rando.logic.split_location_name_by_zone(loc)[0] for loc in progress_locations)
    all_world_areas.add("Tower of the Gods Sector")
    # For all locations, remove the entrance from being hinted barren
    barren_zones = all_world_areas - set(list(zip(*required_locations))[1])
    # For dungeon locations, also remove the dungeon itself
    dungeon_woths = list(filter(lambda x: x[0] in self.rando.logic.DUNGEON_NAMES.values(), required_locations))
    barren_zones = barren_zones - set(list(zip(*dungeon_woths))[0])
    # Remove race-mode banned dungeons from being hinted as barren
    race_mode_banned_dungeons = set(self.rando.logic.DUNGEON_NAMES.values()) - set(self.rando.race_mode_required_dungeons)
    barren_zones = barren_zones - race_mode_banned_dungeons
    
    # Generate barren hints
    # We select at most three zones at random to hint as barren. At max, `self.MAX_BARREN_HINTS` dungeons may be hinted
    # barren. All barren zones are weighted equally, regardless of how many locations are in that zone.
    unhinted_barren_zones = list(barren_zones)
    hinted_barren_zones = []
    num_dungeons_hinted_barren = 0
    while len(unhinted_barren_zones) > 0 and len(hinted_barren_zones) < self.MAX_BARREN_HINTS:
      zone_name = self.rando.rng.choice(unhinted_barren_zones)
      unhinted_barren_zones.remove(zone_name)
      if zone_name in self.rando.logic.DUNGEON_NAMES.values():
        if num_dungeons_hinted_barren < self.MAX_BARREN_DUNGEONS:
          num_dungeons_hinted_barren += 1
        else:
          continue
      hinted_barren_zones.append(Hint(HintType.BARREN, None, zone_name))
    
    # Fill in the remaining hints with location hints
    hinted_locations = []
    remaining_hints_desired = self.TOTAL_WOTH_STYLE_HINTS - len(hinted_woth_zones) - len(hinted_barren_zones)
    hintable_locations = list(filter(lambda loc: loc in self.location_hints.keys(), progress_locations))
    # Remove locations in race-mode banned dungeons
    hintable_locations = list(filter(lambda loc: self.rando.logic.split_location_name_by_zone(loc)[0] not in race_mode_banned_dungeons, hintable_locations))
    
    while len(hintable_locations) > 0 and remaining_hints_desired > 0:
      location_name = self.rando.rng.choice(hintable_locations)
      hintable_locations.remove(location_name)
      item_name = self.rando.logic.done_item_locations[location_name]
      
      # Don't hint at the same item twice
      if location_name not in previously_hinted_locations:
        hinted_locations.append(Hint(HintType.LOCATION, item_name, self.location_hints[location_name]))
        remaining_hints_desired -= 1
    
    return hinted_woth_zones + hinted_barren_zones + hinted_locations
