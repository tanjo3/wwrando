# Note that chest storage is never considered since there's a possibly of softlocking if no chests are available to be stored
LOGICAL_TRICKS = [
  "Early Jabun's Cave",
  "Lenzo Door Cancel",
  "Hammerless Cabana",
  "Needle Rock Chest With Fire Arrows",
  "Early Islet of Steel",
  "Grapple Clip Into Bird's Peak Rock",
  "Sidle Behind Left Boulder In Pawprint",
  "Leafless Horseshoe",
  
  "Leaf Pumps In Submarines",
  
  "Shoot Down Hanging DRC Platform",
  "Jumpslash From Hanging DRC Platform To 2F",
  
  "Grappleless Forest Haven",
  "Grappleless FW Hub Room",
  "FW Basement Without Boomerang",
  "FW BK Chest With Hookshot",
  
  "TotG F1 SK Skip",
  "Skip Command Melody In TotG",
  "Skip Deku Leaf At North Servant In TotG",
  
  "Enter FF Without Bombs",
  
  "Early ET Left Side",
  
  "Gale Isle Entry Without Iron Boots",
  "Skip Wind God's Aria In WT Basement",
  
  "Puppet Ganon Without Boomerang",
  "Grapple Skip in Ganon's Tower",
]
TRICK_NAME_TO_SORTED_INDEX = {trick_name: index for index, trick_name in enumerate(LOGICAL_TRICKS)}

DEFAULT_TRICKS_IN_LOGIC = []

DEFAULT_TRICKS_NOT_IN_LOGIC = LOGICAL_TRICKS.copy()
for trick_name in DEFAULT_TRICKS_IN_LOGIC:
    DEFAULT_TRICKS_NOT_IN_LOGIC.remove(trick_name)
