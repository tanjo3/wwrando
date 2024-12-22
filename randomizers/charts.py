
import copy

from randomizers.base_randomizer import BaseRandomizer
from wwlib.dzx import DZx, SCOB

class ChartRandomizer(BaseRandomizer):
  """Shuffles around which chart points to each sector."""
  
  def __init__(self, rando):
    super().__init__(rando)
  
  def is_enabled(self) -> bool:
    return self.options.randomize_charts
  
  def _randomize(self):
    # Chart randomization is done by the AP generator.
    return
    original_item_names = list(self.rando.plando.charts.values())
    
    # Shuffles the list of island numbers.
    # The shuffled island numbers determine which sector each chart points to.
    shuffled_island_numbers = list(self.rando.plando.charts.keys())
    self.rng.shuffle(shuffled_island_numbers)
    
    for original_item_name in original_item_names:
      shuffled_island_number = shuffled_island_numbers.pop()
      self.rando.plando.charts[shuffled_island_number] = original_item_name
    
    self.logic.update_chart_macros()
  
  def _save(self):
    randomizable_charts = [chart for chart in self.rando.chart_list.charts if chart.type in [0, 1, 2, 6]]
    original_charts = copy.deepcopy(randomizable_charts)
    
    for island_number, original_item_name in self.rando.plando.charts.items():
      # Finds the corresponding charts for the shuffled island number and original item name.
      chart_to_copy_from = next(chart for chart in original_charts if chart.island_number == island_number)
      chart = next(chart for chart in randomizable_charts if chart.item_name == original_item_name)
      
      chart.texture_id = chart_to_copy_from.texture_id
      chart.sector_x = chart_to_copy_from.sector_x
      chart.sector_y = chart_to_copy_from.sector_y
      
      for random_pos_index in range(4):
        possible_pos = chart.possible_random_positions[random_pos_index]
        possible_pos_to_copy_from = chart_to_copy_from.possible_random_positions[random_pos_index]
        
        possible_pos.chart_texture_x_offset = possible_pos_to_copy_from.chart_texture_x_offset
        possible_pos.chart_texture_y_offset = possible_pos_to_copy_from.chart_texture_y_offset
        possible_pos.salvage_x_pos = possible_pos_to_copy_from.salvage_x_pos
        possible_pos.salvage_y_pos = possible_pos_to_copy_from.salvage_y_pos
      
      chart.save_changes()
      
      # Then update the salvage object on the sea so it knows what chart corresponds to it now.
      dzx = self.rando.get_arc(f"files/res/Stage/sea/Room{chart.island_number}.arc").get_file("room.dzr", DZx)
      for scob in dzx.entries_by_type(SCOB):
        if scob.actor_class_name == "d_a_salvage" and scob.salvage_type == 0:
          scob.chart_index_plus_1 = chart.owned_chart_index_plus_1
          scob.save_changes()
  
  def write_to_spoiler_log(self):
    spoiler_log = "Charts:\n"
    
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
      spoiler_log += "  %-18s %s\n" % (chart_name+":", island_name)
    
    spoiler_log += "\n\n\n"
    
    return spoiler_log
  
  
  def build_chart_to_sunken_treasure_location_mapping(self):
    # Helper function to create a mapping of treasure charts to their respective sunken treasure.
    
    chart_name_to_island_number = {}
    for island_number in range(1, 49+1):
      chart_name = self.logic.macros["Chart for Island %d" % island_number][0]
      chart_name_to_island_number[chart_name] = island_number
    
    chart_name_to_sunken_treasure = {}
    for chart_number in range(1, 49+1):
      if chart_number <= 8:
        chart_name = "Triforce Chart %d" % chart_number
      else:
        chart_name = "Treasure Chart %d" % (chart_number-8)
      island_number = chart_name_to_island_number[chart_name]
      island_name = self.rando.island_number_to_name[island_number]
      chart_name_to_sunken_treasure[chart_name] = "%s - Sunken Treasure" % island_name
    
    return chart_name_to_sunken_treasure
