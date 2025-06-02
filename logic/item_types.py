
PROGRESS_ITEMS = [
  "Tingle Tuner",
  "Wind Waker",
  "Spoils Bag",
  "Grappling Hook",
  "Power Bracelets",
  "Iron Boots",
  "Bait Bag",
  "Boomerang",
  "Hookshot",
  "Delivery Bag",
  "Bombs",
  "Skull Hammer",
  "Deku Leaf",
  
  "Triforce Shard 1",
  "Triforce Shard 2",
  "Triforce Shard 3",
  "Triforce Shard 4",
  "Triforce Shard 5",
  "Triforce Shard 6",
  "Triforce Shard 7",
  "Triforce Shard 8",
  
  "Nayru's Pearl",
  "Din's Pearl",
  "Farore's Pearl",
  
  "Wind's Requiem",
  "Ballad of Gales",
  "Command Melody",
  "Earth God's Lyric",
  "Wind God's Aria",
  "Song of Passing",
  
  "Boat's Sail",
  
  "Note to Mom",
  "Maggie's Letter",
  "Moblin's Letter",
  "Cabana Deed",
  
  "Dragon Tingle Statue",
  "Forbidden Tingle Statue",
  "Goddess Tingle Statue",
  "Earth Tingle Statue",
  "Wind Tingle Statue",
  
  "Bomb Bag Capacity Upgrade",
  "Bomb Bag Capacity Upgrade",
  "Quiver Capacity Upgrade",
  "Quiver Capacity Upgrade",
  
  "Ghost Ship Chart",
  "Magic Armor",
] + \
  ["Progressive Sword"]*4 + \
  ["Progressive Shield"]*2 + \
  ["Progressive Bow"]*3 + \
  ["Wallet Capacity Upgrade"]*2 + \
  ["Progressive Picto Box"]*2 + \
  ["Progressive Magic Meter"]*2 + \
  ["Empty Bottle"]*4

NONPROGRESS_ITEMS = [
  "Telescope",
  "Hero's Charm",
  
  # Complimentary ID is not placed in the randomizer to avoid the player getting an overly full delivery bag.
  # If you got a progress item for your delivery bag when the bag was already full, the new item would simply never enter your inventory.
  #"Complimentary ID",
  "Fill-Up Coupon",
  
  "Hurricane Spin",
  
  "Submarine Chart",
  "Beedle's Chart",
  "Platform Chart",
  "Light Ring Chart",
  "Secret Cave Chart",
  "Great Fairy Chart",
  "Octo Chart",
  "Tingle's Chart",
  
  # These three charts are inaccurate in the randomizer so they're not placed.
  # If a way to update them is found they should be placed.
  #"Sea Hearts Chart",
  #"Island Hearts Chart",
  #"IN-credible Chart",
] + \
  ["Piece of Heart"]*44 + \
  ["Heart Container"]*9

CONSUMABLE_ITEMS = \
   1 * ["Green Rupee"] + \
   2 * ["Blue Rupee"] + \
   3 * ["Yellow Rupee"] + \
   5 * ["Red Rupee"] + \
  10 * ["Purple Rupee"] + \
  15 * ["Orange Rupee"] + \
  15 * ["Silver Rupee"] + \
   1 * ["Rainbow Rupee"] + \
  \
   9 * ["Joy Pendant"] + \
   9 * ["Skull Necklace"] + \
   1 * ["Boko Baba Seed"] + \
   9 * ["Golden Feather"] + \
   3 * ["Knight's Crest"] + \
   1 * ["Red Chu Jelly"] + \
   1 * ["Green Chu Jelly"] + \
  \
   1 * ["All-Purpose Bait"] + \
   4 * ["Hyoi Pear"]
# (Note: Blue Chu Jelly is not included as it is specially coded and would cause issues if randomly placed as a field item.)

# Once all the items that have a fixed number per seed are used up, this list is used.
# Unlike the other lists, this one does not have items removed from it as they are placed.
# The number of each item in this list is instead its weighting relative to the other items in the list.
DUPLICATABLE_CONSUMABLE_ITEMS = \
   3 * ["Yellow Rupee"] + \
   7 * ["Red Rupee"] + \
  10 * ["Purple Rupee"] + \
  15 * ["Orange Rupee"] + \
  \
   3 * ["Joy Pendant"]

DUNGEON_PROGRESS_ITEMS = \
  ["DRC Big Key"] *1 + ["DRC Small Key"] *4 + \
  ["FW Big Key"]  *1 + ["FW Small Key"]  *1 + \
  ["TotG Big Key"]*1 + ["TotG Small Key"]*2 + \
  ["FF Big Key"]  *0 + ["FF Small Key"]  *0 + \
  ["ET Big Key"]  *1 + ["ET Small Key"]  *3 + \
  ["WT Big Key"]  *1 + ["WT Small Key"]  *2

DUNGEON_NONPROGRESS_ITEMS = \
  ["DRC Dungeon Map", "DRC Compass"] + \
  ["FW Dungeon Map", "FW Compass"] + \
  ["TotG Dungeon Map", "TotG Compass"] + \
  ["FF Dungeon Map", "FF Compass"] + \
  ["ET Dungeon Map", "ET Compass"] + \
  ["WT Dungeon Map", "WT Compass"]
