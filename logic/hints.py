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
    return "%s <Item: %s, Location: %s>" % (
      str(self.type),
      self.item,
      self.location,
    )
  
  def __hash__(self):
    return hash(str(self))
  
  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return (
        (self.type == other.type)
        and (self.item == other.item)
        and (self.location == other.location)
      )
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
    
    self.chart_name_to_sunken_treasure = {}
  
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
    if hint.type == HintType.WOTH:
      hint_string = (
        "%s\\{1A 06 FF 00 00 05}%s\\{1A 06 FF 00 00 00} is on the way of the hero%s"
        % (prefix, hint.location, suffix)
      )
    elif hint.type == HintType.BARREN:
      hint_string = (
        "%splundering \\{1A 06 FF 00 00 03}%s\\{1A 06 FF 00 00 00} is a foolish choice%s"
        % (prefix, hint.location, suffix)
      )
    elif hint.type == HintType.LOCATION:
      hint_string = (
        "%s\\{1A 06 FF 00 00 01}%s\\{1A 06 FF 00 00 00} rewards \\{1A 06 FF 00 00 01}%s\\{1A 06 FF 00 00 00}%s"
        % (prefix, hint.location, hint.item, suffix)
      )
    elif hint.type == HintType.ITEM:
      hint_string = (
        "%s\\{1A 06 FF 00 00 01}%s\\{1A 06 FF 00 00 00} is located in \\{1A 06 FF 00 00 01}%s\\{1A 06 FF 00 00 00}%s"
        % (prefix, hint.item, hint.location, suffix)
      )
    else:
      hint_string = ""
    
    # Cap delay to "FF"
    delay = min(delay, 255)
    
    # Add a wait command (delay) to prevent the player from skipping over the hint accidentally.
    if delay > 0:
      hint_string += "\\{1A 07 00 00 07 00 %X}" % delay
    
    return hint_string
  
  @staticmethod
  def get_formatted_hint_group_text_static(hints, hint_type, prefix="They say that ", suffix=".", delay=30):
    if hint_type == HintType.WOTH:
      woth_hints = ["\\{1A 06 FF 00 00 05}%s\\{1A 06 FF 00 00 00}" % hint.location for hint in hints]
      hint_string = (
        "%s%s are on the way of the hero%s"
        % (prefix, ", ".join(woth_hints[:-1]) + ", and " + woth_hints[-1], suffix)
      )
    elif hint_type == HintType.BARREN:
      barren_hints = ["\\{1A 06 FF 00 00 03}%s\\{1A 06 FF 00 00 00}" % hint.location for hint in hints]
      hint_string = (
        "%splundering %s is foolish%s"
        % (prefix, ", ".join(barren_hints[:-1]) + ", and " + barren_hints[-1], suffix)
      )
    elif hint_type == HintType.LOCATION:
      # Not implemented because grouped location hints would likely overflow textbox
      hint_string = ""
    elif hint_type == HintType.ITEM:
      # Not implemented because grouped item hints would likely overflow textbox
      hint_string = ""
    else:
      hint_string = ""
    
    # Cap delay to "FF"
    delay = min(delay, 255)
    
    # Add a wait command (delay) to prevent the player from skipping over the hint accidentally.
    if delay > 0:
      hint_string += "\\{1A 07 00 00 07 00 %X}" % delay
    
    return hint_string
  
  def get_entrance_zone(self, location_name):
    # Helper function to return the entrance zone name for the location.
    # For non-dungeon and non-cave locations, the entrance zone name is simply the zone name. When entrances are
    # randomized, the entrance zone name may not be the same as the zone name for dungeons and cave.
    #
    # As a special case, if the entrance zone is Tower of the Gods or if the location name is "Tower of the Gods -
    # Sunken Treasure", the entrance zone name is "Tower of the Gods Sector" to differentiate between the dungeon and
    # the entrance.
    
    zone_name, specific_location_name = self.rando.logic.split_location_name_by_zone(location_name)
    
    # Distinguish between the two Pawprint Isle entrances
    if location_name == "Pawprint Isle - Wizzrobe Cave":
      zone_name = "Pawprint Isle Side Isle"
    
    if zone_name in self.rando.dungeon_and_cave_island_locations and self.rando.logic.is_dungeon_or_cave(location_name):
      entrance_zone = self.rando.dungeon_and_cave_island_locations[zone_name]
      if entrance_zone == "Tower of the Gods":
        entrance_zone = "Tower of the Gods Sector"
    else:
      entrance_zone = zone_name
      if location_name == "Tower of the Gods - Sunken Treasure":
        entrance_zone = "Tower of the Gods Sector"
      # Note that Forsaken Fortress - Sunken Treasure has a similar issue, but there are no randomized entrances
      # on Forsaken Fortress, so we won't make that distinction here
    return entrance_zone
  
  def check_location_required(self, location_to_check, cached_required_items, cached_nonrequired_items):
    # Check if the item is in the cached set of required or nonrequired locations
    item_name = self.rando.logic.done_item_locations[location_to_check]
    if item_name in cached_required_items:
      return True
    if item_name in cached_nonrequired_items:
      return False
    
    # If the item is not a progress item, there's no way it's required
    if item_name not in self.rando.logic.all_progress_items:
      return False
    
    # If the item is a treasure/Triforce chart, only need to check if it's sunken treasure is required
    if item_name.startswith("Treasure Chart ") or item_name.startswith("Triforce Chart "):
      sunken_treasure_name = self.chart_name_to_sunken_treasure[item_name]
      sunken_treasure_item = self.rando.logic.done_item_locations[sunken_treasure_name]
      if self.check_location_required(sunken_treasure_name, cached_required_items, cached_nonrequired_items):
        cached_required_items.add(sunken_treasure_item) # If sunken treasure is required, may as well cache this
        return True
      else:
        return False
    
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
  
  def get_required_locations(self):
    cached_required_items = set()
    cached_nonrequired_items = set()
    
    # Add hard-required items  to cached list of required items
    cached_required_items.update(self.HARD_REQUIRED_ITEMS)
    
    # Check Tingle statues: if one is required, all of them are; if one is not required, none of them are
    items_dict = {item_name: location_name for location_name, item_name in self.rando.logic.done_item_locations.items()}
    if "Dragon Tingle Statue" in items_dict:
      location_name = items_dict["Dragon Tingle Statue"]
      if self.rando.hints.check_location_required(location_name, cached_required_items, cached_nonrequired_items):
        cached_required_items.update(("Dragon Tingle Statue", "Forbidden Tingle Statue", "Goddess Tingle Statue", "Earth Tingle Statue", "Wind Tingle Statue"))
      else:
        cached_nonrequired_items.update(("Dragon Tingle Statue", "Forbidden Tingle Statue", "Goddess Tingle Statue", "Earth Tingle Statue", "Wind Tingle Statue"))
    
    # Check mail dependencies
    if "Delivery Bag" in items_dict:
      location_name = items_dict["Delivery Bag"]
      if not self.rando.hints.check_location_required(location_name, cached_required_items, cached_nonrequired_items):
        cached_nonrequired_items.update(("Delivery Bag", "Maggie's Letter", "Moblin's Letter", "Note to Mom", "Cabana Deed"))
      else:
        cached_required_items.add("Delivery Bag")
    
    # Dungeons can mark off a lot of required items if the boss is required since that means that the BK and all SKs are
    # required (with the exceptions of FW SK and FF as a dungeon). Additionally, it means that all the items required to
    # reach and fight the boss are also required. Note that if a dungeon is not required, those items may or may not be
    # required
    if self.rando.hints.check_location_required("Dragon Roost Cavern - Gohma Heart Container", cached_required_items, cached_nonrequired_items):
      cached_required_items.update(("DRC Small Key", "DRC Big Key"))
    else:
      cached_nonrequired_items.update(("DRC Small Key", "DRC Big Key"))
    if (
      self.rando.hints.check_location_required("Forbidden Woods - Kalle Demos Heart Container", cached_required_items, cached_nonrequired_items)
      or self.rando.hints.check_location_required("Mailbox - Letter from Orca", cached_required_items, cached_nonrequired_items)
    ):
      cached_required_items.update(("FW Big Key", "Deku Leaf"))
    else:
      cached_nonrequired_items.add("FW Big Key")
    if self.rando.hints.check_location_required("Tower of the Gods - Gohdan Heart Container", cached_required_items, cached_nonrequired_items):
      cached_required_items.update(("TotG Small Key", "TotG Big Key", "Bombs", "Command Melody", "Deku Leaf"))
    else:
      cached_nonrequired_items.update(("TotG Small Key", "TotG Big Key"))
    if (
      self.rando.hints.check_location_required("Earth Temple - Jalhalla Heart Container", cached_required_items, cached_nonrequired_items)
      or self.rando.hints.check_location_required("Mailbox - Letter from Baito", cached_required_items, cached_nonrequired_items)
    ):
      cached_required_items.update(("ET Small Key", "ET Big Key", "Progressive Shield", "Power Bracelets", "Command Melody", "Earth God's Lyric", "Skull Hammer"))
    else:
      cached_nonrequired_items.update(("ET Small Key", "ET Big Key"))
    if self.rando.hints.check_location_required("Wind Temple - Molgera Heart Container", cached_required_items, cached_nonrequired_items):
      cached_required_items.update(("WT Small Key", "WT Big Key", "Iron Boots", "Skull Hammer", "Command Melody", "Deku Leaf", "Wind God's Aria"))
    else:
      cached_nonrequired_items.update(("WT Small Key", "WT Big Key"))
    
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
        location_name
        not in self.rando.race_mode_required_locations                                # Ignore boss Heart Containers in race mode, even if it's required
        and (self.rando.options.get("keylunacy") or not item_name.endswith(" Key"))   # Keys are only considered in key-lunacy
        and item_name in self.rando.logic.all_progress_items                          # Required locations always contain required items (by definition)
      ):
        if self.rando.hints.check_location_required(location_name, cached_required_items, cached_nonrequired_items):
          zone_name, specific_location_name = self.rando.logic.split_location_name_by_zone(location_name)
          entrance_zone = self.get_entrance_zone(location_name)
          required_locations.append((zone_name, entrance_zone, specific_location_name, item_name))
          cached_required_items.add(item_name)
        else:
          cached_nonrequired_items.add(item_name)
    
    return required_locations
  
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
      if item_name == "Bait Bag" and self.rando.options.get("hint_placement") == "Fishmen":
        # Can't access fishmen hints until you already have the bait bag
        continue
      if len(hints) >= desired_num_hints:
        break
      
      zone_name, specific_location_name = self.rando.logic.split_location_name_by_zone(location_name)
      # Distinguish between the two Pawprint Isle entrances
      if location_name == "Pawprint Isle - Wizzrobe Cave":
        zone_name = "Pawprint Isle Side Isle"
      if zone_name in self.rando.dungeon_and_cave_island_locations and self.rando.logic.is_dungeon_or_cave(location_name):
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
    # Create a mapping for chart name -> sunken treasure
    self.chart_name_to_sunken_treasure = {}
    chart_name_to_island_number = {}
    for island_number in range(1, 49+1):
      chart_name = self.rando.logic.macros["Chart for Island %d" % island_number][0]
      chart_name_to_island_number[chart_name] = island_number
    for chart_number in range(1, 49+1):
      if chart_number <= 8:
        chart_name = "Triforce Chart %d" % chart_number
      else:
        chart_name = "Treasure Chart %d" % (chart_number-8)
      island_number = chart_name_to_island_number[chart_name]
      island_name = self.rando.island_number_to_name[island_number]
      self.chart_name_to_sunken_treasure[chart_name] = "%s - Sunken Treasure" % island_name
    
    # Determine which locations are required to beat the seed
    # Items are implicitly referred to by their location to handle duplicate item names (i.e., progressive items and
    # small keys). Basically, we remove the item from that location and see if the seed is still beatable. If not, then
    # we consider the item as required.
    required_locations = self.get_required_locations()
    
    # Generate WOTH hints
    # We select at most `self.MAX_WOTH_HINTS` zones at random to hint as WOTH. At max, `self.MAX_WOTH_DUNGEONS` dungeons
    # may be hinted WOTH. Zones are weighted by the number of required locations at that zone. The more required
    # locations, the more likely that zone will be chosen.
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
          hinted_woth_zones.append(Hint(HintType.WOTH, item_name, "Tower of the Gods Sector"))
        else:
          hinted_woth_zones.append(Hint(HintType.WOTH, item_name, zone_name))
      else:
        hinted_woth_zones.append(Hint(HintType.WOTH, item_name, entrance_zone))
      previously_hinted_locations.append("%s - %s" % (zone_name, specific_location_name))
    
    # Identify zones which do not contain required items
    # For starters, get all entrance zones for progress locations in this seed
    progress_locations, non_progress_locations = self.rando.logic.get_progress_and_non_progress_locations()
    all_world_areas = set(self.get_entrance_zone(location_name) for location_name in progress_locations)
    # Special case: if entrances are not randomized and Tower of the Gods - Sunken Treasure is not in logic, "Tower of
    # the Gods Sector" can only refer to the dungeon, so is redundant. Remove it.
    if (
      "Tower of the Gods Sector" in all_world_areas
      and self.rando.options.get("randomize_entrances") in ["Disabled", None]
      and "Tower of the Gods - Sunken Treasure" not in progress_locations
    ):
      all_world_areas.remove("Tower of the Gods Sector")
    # For all required locations, remove the entrance from being hinted barren
    barren_zones = all_world_areas - set(list(zip(*required_locations))[1])
    # For dungeon locations, also remove the dungeon itself
    dungeon_woths = list(filter(lambda x: x[0] in self.rando.logic.DUNGEON_NAMES.values(), required_locations))
    if len(dungeon_woths) > 0:
      barren_zones = barren_zones - set(list(zip(*dungeon_woths))[0])
    
    # Generate barren hints
    # We select at most `self.MAX_BARREN_HINTS` zones at random to hint as barren. At max, `self.MAX_BARREN_DUNGEONS`
    # dungeons may be hinted barren. All barren zones are weighted equally, regardless of how many locations are in that
    # zone.
    unhinted_barren_zones = list(sorted(barren_zones))
    hinted_barren_zones = []
    num_dungeons_hinted_barren = 0
    while len(unhinted_barren_zones) > 0 and len(hinted_barren_zones) < self.MAX_BARREN_HINTS:
      # Remove a barren zone at random from the list
      zone_name = self.rando.rng.choice(unhinted_barren_zones)
      unhinted_barren_zones.remove(zone_name)
      
      # If the zone is a dungeon, ensure we still have room to hint at barren dungeon
      if zone_name in self.rando.logic.DUNGEON_NAMES.values():
        if num_dungeons_hinted_barren < self.MAX_BARREN_DUNGEONS:
          num_dungeons_hinted_barren += 1
        else:
          continue
      hinted_barren_zones.append(Hint(HintType.BARREN, None, zone_name))
    
    # Fill in the remaining hints with location hints
    hinted_locations = []
    hintable_locations = list(filter(lambda loc: loc in self.location_hints.keys(), progress_locations))
    # Remove locations in race-mode banned dungeons
    race_mode_banned_dungeons = set(self.rando.logic.DUNGEON_NAMES.values()) - set(self.rando.race_mode_required_dungeons)
    hintable_locations = list(filter(lambda loc: self.rando.logic.split_location_name_by_zone(loc)[0] not in race_mode_banned_dungeons, hintable_locations))
    # Remove locations for items that were previously hinted
    hintable_locations = list(filter(lambda loc: loc not in previously_hinted_locations, hintable_locations))
    # Remove locations in hinted barren areas
    new_hintable_locations = []
    barrens = [hint.location for hint in hinted_barren_zones]
    for location_name in hintable_locations:
      # Catch Mailbox cases
      if (
          (location_name == "Mailbox - Letter from Baito" and "Earth Temple" in barrens)
          or (location_name == "Mailbox - Letter from Orca" and "Forbidden Woods" in barrens)
          or (location_name == "Mailbox - Letter from Aryll" and "Forsaken Fortress" in barrens)
          or (location_name == "Mailbox - Letter from Tingle" and "Forsaken Fortress" in barrens)
      ):
        continue
      # Catch locations which are hinted in barren zones
      entrance_zone = self.get_entrance_zone(location_name)
      if entrance_zone not in barrens:
        new_hintable_locations.append(location_name)
    hintable_locations = new_hintable_locations.copy()
    
    # Generate location hints
    # Shuffle the list of valid location hints and then create them one by one until we have enough
    self.rando.rng.shuffle(hintable_locations)
    remaining_hints_desired = self.TOTAL_WOTH_STYLE_HINTS - len(hinted_woth_zones) - len(hinted_barren_zones)
    for location_name in hintable_locations:
      remaining_hints_desired -= 1
      item_name = self.rando.logic.done_item_locations[location_name]
      hinted_locations.append(Hint(HintType.LOCATION, item_name, self.location_hints[location_name]))
      if remaining_hints_desired == 0:
        break
    
    return hinted_woth_zones + hinted_barren_zones + hinted_locations
