class Hints:
  def __init__(self, rando):
    self.rando = rando

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
        island_hint_name = self.rando.island_name_hints[island_name]
      elif zone_name in self.rando.island_name_hints:
        island_name = zone_name
        island_hint_name = self.rando.island_name_hints[island_name]
      elif zone_name in self.rando.logic.DUNGEON_NAMES.values():
        continue
      else:
        continue
      
      if (item_name, island_name) in unique_items_given_hint_for: # Don't give hint for same type of item in same zone
        continue
      
      item_hint_name = self.rando.progress_item_hints[item_name]
      
      hints.append((item_hint_name, island_hint_name))
      
      unique_items_given_hint_for.append((item_name, island_name))
    
    return hints
