from dataclasses import dataclass
from enum import StrEnum

from options.base_options import BaseOptions, option

from logic.tricks import ALL_TRICK_NAMES

class DungeonItemShuffleMode(StrEnum):
  VANILLA = "Vanilla"
  START_WITH = "Start With"
  OWN_DUNGEON = "Own Dungeon"
  ANY_DUNGEON = "Any Dungeon"
  OVERWORLD = "Overworld"
  ANYWHERE = "Anywhere"

class SwordMode(StrEnum):
  START_WITH_SWORD = "Start with Hero's Sword"
  NO_STARTING_SWORD = "No Starting Sword"
  SWORDLESS = "Swordless"

class EntranceMixMode(StrEnum):
  SEPARATE_DUNGEONS = "Separate Dungeons From Caves & Fountains"
  MIX_DUNGEONS = "Mix Dungeons & Caves & Fountains"

class MilaSpeedup(StrEnum):
  NONE = "None"
  SHORTENED = "Shortened"
  INSTANT = "Instant"

class SeaCompanion(StrEnum):
  NONE = "None"
  MEDLI = "Medli"
  MAKAR = "Makar"
  BOTH = "Both"
  RANDOM = "Random"

@dataclass
class Options(BaseOptions):
  def validate(self):
    super().validate()
    
    from logic.logic import Logic
    
    if self.excluded_locations:
      valid_locations = set(Logic.load_and_parse_item_locations().keys())
      self.excluded_locations = sorted(loc for loc in self.excluded_locations if loc in valid_locations)
    
    if self.enabled_tricks:
      valid_tricks = set(ALL_TRICK_NAMES)
      self.enabled_tricks = sorted(trick for trick in self.enabled_tricks if trick in valid_tricks)
    
    if self.hoho_hints and self.hoho_hint_shards:
      self.hoho_hint_shards = False
    
  #region Progress locations
  progression_dungeons: bool = option(
    default=True,
    description="This controls whether dungeons can contain progress items.<br>"
      "<u>If this is not checked, dungeons will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_tingle_chests: bool = option(
    default=True,
    description="Tingle Chests that are hidden in dungeons and must be bombed to make them appear. (2 in DRC, 1 each in FW, TotG, ET, and WT).<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_dungeon_secrets: bool = option(
    default=True,
    description="DRC, FW, TotG, ET, and WT each have 2-3 secret items within them (11 in total). This controls whether they can be progress items.<br>"
      "The items are fairly well-hidden (they aren't in chests), so don't select this option unless you're prepared to search each dungeon high and low!",
  )
  progression_puzzle_secret_caves: bool = option(
    default=True,
    description="This controls whether puzzle-focused secret caves can contain progress items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_combat_secret_caves: bool = option(
    default=True,
    description="This controls whether combat-focused secret caves (besides Savage Labyrinth) can contain progress items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_savage_labyrinth: bool = option(
    default=False,
    description="This controls whether the Savage Labyrinth can contain progress items.<br>"
      "<u>If this is not checked, it will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_great_fairies: bool = option(
    default=True,
    description="This controls whether the items given by Great Fairies can be progress items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_short_sidequests: bool = option(
    default=True,
    description="This controls whether sidequests that can be completed quickly can reward progress items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only reward optional items you don't need to beat the game.",
  )
  progression_long_sidequests: bool = option(
    default=True,
    description="This controls whether long sidequests (e.g. Lenzo's assistant, withered trees, goron trading) can reward progress items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only reward optional items you don't need to beat the game.",
  )
  progression_spoils_trading: bool = option(
    default=True,
    description="This controls whether the items you get by trading in spoils to NPCs can be progress items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only reward optional items you don't need to beat the game.",
  )
  progression_minigames: bool = option(
    default=True,
    description="This controls whether most minigames can reward progress items (auctions, mail sorting, barrel shooting, bird-man contest).<br>"
      "<u>If this is not checked, minigames will still be randomized</u>, but will only reward optional items you don't need to beat the game.",
  )
  progression_battlesquid: bool = option(
    default=False,
    description="This controls whether the Windfall battleship minigame can reward progress items.<br>"
      "<u>If this is not checked, it will still be randomized</u>, but will only reward optional items you don't need to beat the game.",
  )
  progression_free_gifts: bool = option(
    default=True,
    description="This controls whether gifts freely given by NPCs can be progress items (Tott, Salvage Corp, imprisoned Tingle).<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only be optional items you don't need to beat the game.",
  )
  progression_mail: bool = option(
    default=True,
    description="This controls whether mail can contain progress items.<br>"
      "<u>If this is not checked, mail will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_platforms_rafts: bool = option(
    default=True,
    description="This controls whether lookout platforms and rafts can contain progress items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_submarines: bool = option(
    default=True,
    description="This controls whether submarines can contain progress items.<br>"
      "<u>If this is not checked, submarines will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_eye_reef_chests: bool = option(
    default=False,
    description="This controls whether the chests that appear after clearing out the eye reefs can contain progress items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_big_octos_gunboats: bool = option(
    default=True,
    description="This controls whether the items dropped by Big Octos and Gunboats can contain progress items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_triforce_charts: bool = option(
    default=False,
    description="This controls whether the sunken treasure chests marked on Triforce Charts can contain progress items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_treasure_charts: bool = option(
    default=False,
    description="This controls whether the sunken treasure chests marked on Treasure Charts can contain progress items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_expensive_purchases: bool = option(
    default=True,
    description="This controls whether items that cost a lot of rupees can be progress items (Rock Spire shop, auctions, Tingle's letter, trading quest).<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only be optional items you don't need to beat the game.",
  )
  progression_island_puzzles: bool = option(
    default=True,
    description="This controls whether various island puzzles can contain progress items (e.g. chests hidden in unusual places).<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_misc: bool = option(
    default=True,
    description="Miscellaneous locations that don't fit into any of the above categories (outdoors chests, wind shrine, Cyclos, etc).<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  progression_rupee_dungeon: bool = option(
    default=True,
    description="This controls whether rupees inside dungeons can contain progress items. These rupees will have a sparkle effect to clearly identify them.<br>"
      "If this is not checked, the rupees will not be randomized and will not have the sparkle effect.",
  )
  progression_rupee_overworld: bool = option(
    default=True,
    description="This controls whether rupees in the overworld can contain progress items. These rupees will have a sparkle effect to clearly identify them.<br>"
      "If this is not checked, the rupees will not be randomized and will not have the sparkle effect.",
  )
  progression_blue_chu_jellies: bool = option(
    default=True,
    description="If this is checked, each Blue ChuChu will drop a randomized item instead of Blue Chu Jelly, and 23 Blue Chu Jellies will be added to the item pool.<br>"
      "If this is not checked, Blue ChuChus will drop Blue Chu Jelly as in vanilla, and Blue Chu Jellies will not be added to the item pool.",
  )
  progression_orca_minigame: bool = option(
    default=False,
    description="This controls whether the Orca mini-game can contain progression items.<br>"
      "<u>If this is not checked, they will still be randomized</u>, but will only contain optional items you don't need to beat the game.",
  )
  
  progression_locations: list[str] = option(
    default_factory=lambda: [],
    permalink=False,
    description="Randomized locations that can have progress items.",
  )
  excluded_locations: list[str] = option(
    default_factory=lambda: [
      "Angular Isles - Blue ChuChu Drop",
      "Bird's Peak Rock - Blue ChuChu Drop",
      "Boating Course - Blue ChuChu Drop",
      "Boating Course - Raft",
      "Bomb Island - Submarine",
      "Cliff Plateau Isles - Blue ChuChu Drop",
      "Cliff Plateau Isles - Lookout Platform",
      "Cliff Plateau Isles - Rupee on Platform in Lower Pool 1",
      "Cliff Plateau Isles - Rupee on Platform in Lower Pool 2",
      "Cliff Plateau Isles - Rupee on Platform in Lower Pool 3",
      "Cliff Plateau Isles - Rupee on Platform in Lower Pool 4",
      "Cliff Plateau Isles - Rupee on Platform in Middle Pool 1",
      "Cliff Plateau Isles - Rupee on Platform in Middle Pool 2",
      "Cliff Plateau Isles - Rupee on Platform in Upper Pool",
      "Crescent Moon Island - First Blue ChuChu Drop",
      "Crescent Moon Island - Second Blue ChuChu Drop",
      "Crescent Moon Island - Submarine",
      "Diamond Steppe Island - Big Octo",
      "Diamond Steppe Island - Blue ChuChu Drop",
      "Dragon Roost Cavern - Rupee in Rat Room Lower Crawlspace 1",
      "Dragon Roost Cavern - Rupee in Rat Room Lower Crawlspace 2",
      "Dragon Roost Cavern - Rupee in Rat Room Lower Crawlspace 3",
      "Dragon Roost Cavern - Rupee in Rat Room Lower Crawlspace 4",
      "Dragon Roost Cavern - Rupee in Rat Room Lower Crawlspace 5",
      "Dragon Roost Cavern - Rupee in Rat Room Upper Crawlspace 1",
      "Dragon Roost Cavern - Rupee in Rat Room Upper Crawlspace 2",
      "Dragon Roost Cavern - Rupee in Rat Room Upper Crawlspace 3",
      "Dragon Roost Cavern - Rupee in Rat Room Upper Crawlspace 4",
      "Dragon Roost Cavern - Tingle Chest in Hub Room",
      "Dragon Roost Cavern - Tingle Statue Chest",
      "Dragon Roost Island - Rito Aerie - Give Hoskit 20 Golden Feathers",
      "Dragon Roost Island - Rupee Above Bomb Flower",
      "Dragon Roost Island - Rupee in Shallow Pool 1",
      "Dragon Roost Island - Rupee in Shallow Pool 2",
      "Dragon Roost Island - Rupee in Shallow Pool 3",
      "Dragon Roost Island - Rupee in Shallow Pool 4",
      "Dragon Roost Island - Rupee in Shallow Pool 5",
      "Dragon Roost Island - Secret Cave",
      "Earth Temple - Behind Curtain Next to Hammer Button",
      "Earth Temple - Rupee Behind Curtain In Warp Pot Room",
      "Earth Temple - Rupee Behind Destructible Statue Before Third Crypt",
      "Earth Temple - Rupee Behind Destructible Wall in Shortcut 1",
      "Earth Temple - Rupee Behind Destructible Wall in Shortcut 2",
      "Earth Temple - Rupee Behind Destructible Wall in Shortcut 3",
      "Earth Temple - Rupee Behind Destructible Wall in Shortcut 4",
      "Earth Temple - Rupee Behind Destructible Wall in Shortcut 5",
      "Earth Temple - Rupee Behind Destructible Wall in Shortcut 6",
      "Earth Temple - Rupee Behind Destructible Wall in Shortcut 7",
      "Earth Temple - Rupee Behind Destructible Wall in Shortcut 8",
      "Earth Temple - Rupee Behind Destructible Wall in Shortcut 9",
      "Earth Temple - Rupee in Second Crypt",
      "Earth Temple - Rupee in Third Crypt 1",
      "Earth Temple - Tingle Statue Chest",
      "Eastern Fairy Island - Lookout Platform - Defeat the Cannons and Enemies",
      "Fire Mountain - Big Octo",
      "Fire Mountain - Lookout Platform Chest",
      "Five-Eye Reef - Lookout Platform",
      "Five-Star Isles - Lookout Platform - Destroy the Cannons",
      "Five-Star Isles - Raft",
      "Five-Star Isles - Submarine",
      "Flight Control Platform - Bird-Man Contest - First Prize",
      "Flight Control Platform - Submarine",
      "Forbidden Woods - Rupee Around Miniboss Chest 1",
      "Forbidden Woods - Rupee Around Miniboss Chest 2",
      "Forbidden Woods - Rupee Around Miniboss Chest 3",
      "Forbidden Woods - Rupee Around Miniboss Chest 4",
      "Forbidden Woods - Rupee Around Miniboss Chest 5",
      "Forbidden Woods - Rupee Around Miniboss Chest 6",
      "Forbidden Woods - Rupee Around Miniboss Chest 7",
      "Forbidden Woods - Rupee Around Miniboss Chest 8",
      "Forbidden Woods - Rupee Near Boko Baba 1",
      "Forbidden Woods - Rupee Near Boko Baba 2",
      "Forbidden Woods - Rupee Near Boko Baba 3",
      "Forbidden Woods - Rupee Near Boko Baba 4",
      "Forbidden Woods - Rupee Near Boko Baba 5",
      "Forbidden Woods - Rupee in Tree in Hub Room 1",
      "Forbidden Woods - Rupee in Tree in Hub Room 2",
      "Forbidden Woods - Rupee in Tree in Hub Room 3",
      "Forbidden Woods - Rupee in Tree in Hub Room 4",
      "Forbidden Woods - Rupee in Tree in Hub Room 5",
      "Forbidden Woods - Rupee on Lower Tree Branch 1",
      "Forbidden Woods - Rupee on Lower Tree Branch 2",
      "Forbidden Woods - Rupee on Lower Tree Branch 3",
      "Forbidden Woods - Rupee on Lower Tree Branch 4",
      "Forbidden Woods - Rupee on Upper Tree Branch 1",
      "Forbidden Woods - Rupee on Upper Tree Branch 2",
      "Forbidden Woods - Rupee on Upper Tree Branch 3",
      "Forbidden Woods - Rupee on Upper Tree Branch 4",
      "Forbidden Woods - Tingle Statue Chest",
      "Gale Isle - Rupee on East Pillars 1",
      "Gale Isle - Rupee on East Side of Summit 1",
      "Gale Isle - Rupee on East Side of Summit 2",
      "Gale Isle - Rupee on East Side of Summit 3",
      "Gale Isle - Rupee on East Side of Summit 4",
      "Gale Isle - Rupee on Summit 1",
      "Gale Isle - Rupee on Summit 2",
      "Gale Isle - Rupee on Summit 3",
      "Gale Isle - Rupee on Summit 4",
      "Gale Isle - Rupee on West Side of Summit 1",
      "Gale Isle - Rupee on West Side of Summit 2",
      "Gale Isle - Rupee on West Side of Summit 3",
      "Greatfish Isle - Rupee on Small Island 3",
      "Greatfish Isle - Rupee on Small Island 4",
      "Headstone Island - Rupee Behind Headstone 2",
      "Headstone Island - Rupee Behind Headstone 3",
      "Headstone Island - Rupee Behind Headstone 4",
      "Headstone Island - Rupee Behind Headstone 5",
      "Headstone Island - Rupee Behind Headstone 6",
      "Headstone Island - Rupee Behind Headstone 7",
      "Headstone Island - Rupee East of Headstone 1",
      "Headstone Island - Rupee East of Headstone 2",
      "Headstone Island - Rupee East of Headstone 3",
      "Headstone Island - Rupee East of Headstone 4",
      "Headstone Island - Rupee on Top of Headstone",
      "Headstone Island - Submarine",
      "Horseshoe Island - Blue ChuChu Drop",
      "Horseshoe Island - Northwestern Lookout Platform",
      "Horseshoe Island - Southeastern Lookout Platform",
      "Ice Ring Isle - Inner Cave - Chest",
      "Ice Ring Isle - Rupee on Ice Slide in Cave 1",
      "Ice Ring Isle - Rupee on Ice Slide in Cave 2",
      "Ice Ring Isle - Rupee on Iceberg",
      "Mailbox - Letter from Hoskit's Girlfriend",
      "Mailbox - Letter from Tingle",
      "Mother and Child Isles - Blue ChuChu Drop",
      "Needle Rock Isle - Golden Gunboat",
      "Northern Fairy Island - Blue ChuChu Drop",
      "Northern Fairy Island - Great Fairy",
      "Northern Fairy Island - Submarine",
      "Outset Island - Great Fairy",
      "Outset Island - Rupee Above Aryll's Lookout",
      "Outset Island - Rupee Above Path to Forest of Fairies",
      "Outset Island - Rupee Behind Mesa's Bed",
      "Outset Island - Rupee in Log in Forest of Fairies",
      "Outset Island - Rupee on Jumping Rocks 1",
      "Outset Island - Rupee on Jumping Rocks 2",
      "Outset Island - Rupee on Mesa's House Lower",
      "Outset Island - Rupee on Mesa's House Upper",
      "Outset Island - Rupee on Pillar Below Bridge to Forest of Fairies",
      "Overlook Island - Blue ChuChu Drop",
      "Overlook Island - Cave",
      "Pawprint Isle - Blue ChuChu Drop",
      "Pawprint Isle - Lookout Platform - Defeat the Enemies",
      "Pawprint Isle - Rupee Around Tree 1",
      "Pawprint Isle - Rupee Around Tree 2",
      "Pawprint Isle - Rupee Around Tree 3",
      "Pawprint Isle - Rupee Around Tree 4",
      "Pawprint Isle - Rupee Hidden On Small ChuChu Statue 1",
      "Pawprint Isle - Rupee Hidden On Small ChuChu Statue 2",
      "Pawprint Isle - Wizzrobe Cave",
      "Private Oasis - Big Octo",
      "Private Oasis - Rupee Underneath Cabana 1",
      "Private Oasis - Rupee Underneath Cabana 2",
      "Private Oasis - Rupee Underneath Cabana 3",
      "Private Oasis - Rupee Underneath Cabana 4",
      "Private Oasis - Rupee Underneath Cabana 5",
      "Private Oasis - Rupee Underneath Cabana 6",
      "Private Oasis - Rupee Underneath Cabana 7",
      "Private Oasis - Rupee Underneath Cabana 8",
      "Private Oasis - Rupee Underneath Cabana 9",
      "Private Oasis - Rupee at the Bottom of Waterfall",
      "Private Oasis - Rupee at the Top of Waterfall",
      "Private Oasis - Rupee in Pool 1",
      "Private Oasis - Rupee in Pool 2",
      "Private Oasis - Rupee in Pool 3",
      "Private Oasis - Rupee in Pool 4",
      "Private Oasis - Rupee in Pool 5",
      "Private Oasis - Rupee in Pool 6",
      "Private Oasis - Rupee in Pool 7",
      "Private Oasis - Rupee in Waterfall 1",
      "Private Oasis - Rupee in Waterfall 2",
      "Private Oasis - Rupee in Waterfall 3",
      "Private Oasis - Rupee in Waterfall 4",
      "Private Oasis - Rupee in Waterfall 5",
      "Rock Spire Isle - Beedle's Special Shop Ship - 500 Rupee Item",
      "Rock Spire Isle - Beedle's Special Shop Ship - 900 Rupee Item",
      "Rock Spire Isle - Beedle's Special Shop Ship - 950 Rupee Item",
      "Rock Spire Isle - Blue ChuChu Drop",
      "Rock Spire Isle - Cave",
      "Rock Spire Isle - Center Lookout Platform",
      "Rock Spire Isle - Eastern Lookout Platform - Destroy the Cannons",
      "Rock Spire Isle - Southeast Gunboat",
      "Rock Spire Isle - Western Lookout Platform - Destroy the Cannons",
      "Seven-Star Isles - Big Octo",
      "Seven-Star Isles - Center Lookout Platform",
      "Seven-Star Isles - Northern Lookout Platform",
      "Seven-Star Isles - Southern Lookout Platform",
      "Shark Island - Blue ChuChu Drop",
      "Shark Island - Cave",
      "Shark Island - Rupee in Trees 1",
      "Shark Island - Rupee in Trees 2",
      "Shark Island - Rupee in Trees 3",
      "Shark Island - Rupee in Trees 4",
      "Shark Island - Rupee in Trees 5",
      "Shark Island - Rupee in Trees 6",
      "Shark Island - Rupee in Trees 7",
      "Shark Island - Rupee in Trees 8",
      "Shark Island - Rupee on Upper Ledge 3",
      "Six-Eye Reef - Lookout Platform - Destroy the Cannons",
      "Southern Fairy Island - Blue ChuChu Drop",
      "Southern Fairy Island - Lookout Platform - Destroy the Northwest Cannons",
      "Southern Fairy Island - Lookout Platform - Destroy the Southeast Cannons",
      "Spectacle Island - Barrel Shooting - First Prize",
      "Spectacle Island - Barrel Shooting - Second Prize",
      "Spectacle Island - Blue ChuChu Drop",
      "Star Belt Archipelago - Lookout Platform",
      "Star Island - Blue ChuChu Drop",
      "Star Island - Cave",
      "Star Island - Lookout Platform",
      "Stone Watcher Island - Blue ChuChu Drop",
      "Stone Watcher Island - Cave",
      "The Great Sea - Goron Trading Reward",
      "The Great Sea - Withered Trees",
      "Thorned Fairy Island - Northeastern Lookout Platform - Destroy the Cannons",
      "Thorned Fairy Island - Southwestern Lookout Platform - Defeat the Enemies",
      "Tingle Island - Big Octo",
      "Tingle Island - Blue ChuChu Drop",
      "Two-Eye Reef - Lookout Platform",
      "Western Fairy Island - Blue ChuChu Drop",
      "Western Fairy Island - Great Fairy",
      "Western Fairy Island - Lookout Platform",
      "Wind Temple - Tingle Statue Chest",
      "Windfall Island - 40 Rupee Auction",
      "Windfall Island - 5 Rupee Auction",
      "Windfall Island - 60 Rupee Auction",
      "Windfall Island - 80 Rupee Auction",
      "Windfall Island - Cafe Bar - Postman",
      "Windfall Island - Chu Jelly Juice Shop - Give 15 Blue Chu Jelly",
      "Windfall Island - Chu Jelly Juice Shop - Rupee on Left Shelf",
      "Windfall Island - Chu Jelly Juice Shop - Rupee on Right Shelf",
      "Windfall Island - Dampa Pig Minigame - Deliver 1 Pig",
      "Windfall Island - Dampa Pig Minigame - Deliver 3 Pigs",
      "Windfall Island - Jail - Maze Chest",
      "Windfall Island - Jail - Rupee Underneath Bed",
      "Windfall Island - Jail - Rupee in Maze 1",
      "Windfall Island - Jail - Rupee in Maze 2",
      "Windfall Island - Jail - Rupee in Maze 3",
      "Windfall Island - Lenzo's House - Become Lenzo's Assistant",
      "Windfall Island - Lenzo's House - Bring Forest Firefly",
      "Windfall Island - Linda and Anton",
      "Windfall Island - Maggie - Delivery Reward",
      "Windfall Island - Mrs. Marie - Give 1 Joy Pendant",
      "Windfall Island - Mrs. Marie - Give 21 Joy Pendants",
      "Windfall Island - Mrs. Marie - Give 40 Joy Pendants",
      "Windfall Island - Pirate Ship",
      "Windfall Island - Rupee Behind Battlesquid Minigame 1",
      "Windfall Island - Rupee Behind Battlesquid Minigame 2",
      "Windfall Island - Rupee Behind Battlesquid Minigame 3",
      "Windfall Island - Sam - Decorate the Town",
    ],
    description="Randomized locations that cannot have progress items.",
  )
  #endregion
  
  #region Dungeon Items
  shuffle_small_keys: DungeonItemShuffleMode = option(
    default=DungeonItemShuffleMode.OWN_DUNGEON,
    description="Controls where small keys can be placed.",
    choice_descriptions={
      DungeonItemShuffleMode.VANILLA:
        "Vanilla: Small keys will be in their original locations.",
      DungeonItemShuffleMode.START_WITH:
        "Start With: You will start the game with all small keys.",
      DungeonItemShuffleMode.OWN_DUNGEON:
        "Own Dungeon: Small keys will be shuffled within their own dungeons.",
      DungeonItemShuffleMode.ANY_DUNGEON:
        "Any Dungeon: Small keys can appear in any dungeon.",
      DungeonItemShuffleMode.OVERWORLD:
        "Overworld: Small keys will only appear outside of dungeons.",
      DungeonItemShuffleMode.ANYWHERE:
        "Anywhere: Small keys can appear anywhere in the game.",
    },
  )
  shuffle_big_keys: DungeonItemShuffleMode = option(
    default=DungeonItemShuffleMode.OWN_DUNGEON,
    description="Controls where Big Keys can be placed.",
    choice_descriptions={
      DungeonItemShuffleMode.VANILLA:
        "Vanilla: Big Keys will be in their original locations.",
      DungeonItemShuffleMode.START_WITH:
        "Start With: You will start the game with all Big Keys.",
      DungeonItemShuffleMode.OWN_DUNGEON:
        "Own Dungeon: Big Keys will be shuffled within their own dungeons.",
      DungeonItemShuffleMode.ANY_DUNGEON:
        "Any Dungeon: Big Keys can appear in any dungeon.",
      DungeonItemShuffleMode.OVERWORLD:
        "Overworld: Big Keys will only appear outside of dungeons.",
      DungeonItemShuffleMode.ANYWHERE:
        "Anywhere: Big Keys can appear anywhere in the game.",
    },
  )
  shuffle_maps_and_compasses: DungeonItemShuffleMode = option(
    default=DungeonItemShuffleMode.START_WITH,
    description="Controls where dungeon maps and compasses can be placed.",
    choice_descriptions={
      DungeonItemShuffleMode.VANILLA:
        "Vanilla: Dungeon maps and compasses will be in their original locations.",
      DungeonItemShuffleMode.START_WITH:
        "Start With: You will start the game with all dungeon maps and compasses.",
      DungeonItemShuffleMode.OWN_DUNGEON:
        "Own Dungeon: Dungeon maps and compasses will be shuffled within their own dungeons.",
      DungeonItemShuffleMode.ANY_DUNGEON:
        "Any Dungeon: Dungeon maps and compasses can appear in any dungeon.",
      DungeonItemShuffleMode.OVERWORLD:
        "Overworld: Dungeon maps and compasses will only appear outside of dungeons.",
      DungeonItemShuffleMode.ANYWHERE:
        "Anywhere: Dungeon maps and compasses can appear anywhere in the game.",
    },
  )
  #endregion
  
  #region Modes
  sword_mode: SwordMode = option(
    default=SwordMode.NO_STARTING_SWORD,
    description="Controls whether you start with the Hero's Sword, the Hero's Sword is randomized, or if there are no swords in the entire game.<br>"
      "Swordless and No Starting Sword are challenge modes. (For Swordless, Phantom Ganon at FF is vulnerable to Skull Hammer.)",
    choice_descriptions={
      SwordMode.START_WITH_SWORD:
        "Start with Hero's Sword: You will start the game with the basic Hero's Sword already in your inventory (the default).",
      SwordMode.NO_STARTING_SWORD:
        "No Starting Sword: You will start the game with no sword, and have to find it somewhere in the world like other randomized items.",
      SwordMode.SWORDLESS:
        "Swordless: You will start the game with no sword, and won't be able to find it anywhere. You have to beat the entire game using other items as weapons instead of the sword.<br>"
        "(Note that Phantom Ganon in FF becomes vulnerable to Skull Hammer in this mode.)",
    },
  )
  required_bosses: bool = option(
    default=True,
    description="In this mode, you will not be allowed to beat the game until certain randomly-chosen bosses are defeated. Nothing in dungeons for other bosses will ever be required.<br>"
      "You can see which islands have the required bosses on them by opening the sea chart and checking which islands have blue quest markers.",
  )
  num_required_bosses: int = option(
    default=3,
    minimum=1,
    maximum=6,
    description="Select the number of randomly-chosen bosses that are required in Required Bosses Mode.<br>"
      "The door to Puppet Ganon will not unlock until you've defeated all of these bosses. Nothing in dungeons for other bosses will ever be required.",
  )
  prioritize_required_bosses: bool = option(
    default=False,
    description="Guarantees that each required boss's Heart Container location will contain a progress item.",
  )
  chest_type_matches_contents: bool = option(
    default=True,
    description="Changes the chest type to reflect its contents. A metal chest has a progress item, a wooden chest has a non-progress item or a consumable, and a green chest has a potentially required dungeon key.",
  )
  trap_chests: bool = option(
    default=False,
    description="Allows the randomizer to place several trapped chests across the game that do not give you items.<br>"
      "Perfect for spicing up any run!",
  )
  boss_soul_shuffle: bool = option(
    default=True,
    description="Boss souls are new randomizable progress items. Without finding a boss's soul, the boss won't spawn when entering its arena.<br>"
      "Souls exist for Gohma, Kalle Demos, Gohdan, Helmaroc King, Jalhalla, and Molgera.",
  )
  #endregion
  
  #region Difficulty
  available_tricks: list[str] = option(
    default_factory=lambda: list(ALL_TRICK_NAMES),
    permalink=False,
    description="Logic tricks that can be enabled.<br>"
      "When enabled, the randomizer may require you to perform these tricks to beat the game.",
  )
  enabled_tricks: list[str] = option(
    default_factory=lambda: [
      "Boating Course Cave with Only Hookshot",
      "DRC - Use Deku Leaf to Enter Gaping Maw",
      "DRC - Use Ice Arrows to Enter Gaping Maw",
      "FF - Trick Mounted Cannons to Blow Up Gate",
      "FF - Use Floormaster to Reach Upper Jail Cell",
      "Reflect Light Arrows with Skull Hammer",
    ],
    description="Logic tricks that are enabled.<br>"
      "When enabled, the randomizer may require you to perform these tricks to beat the game.",
  )
  
  hero_mode: bool = option(
    default=False,
    description="In Hero Mode, you take four times more damage than normal and heart refills will not drop.",
  )
  orca_one_hit_knockout: bool = option(
    default=False,
    description="This option makes Orca's minigame end immediately upon taking a hit.",
  )
  #endregion
  
  #region Entrance randomizer
  randomize_dungeon_entrances: bool = option(
    default=True,
    description="Shuffles around which dungeon entrances take you into which dungeons.<br>"
      "(No effect on Forsaken Fortress or Ganon's Tower.)",
  )
  randomize_secret_cave_entrances: bool = option(
    default=False,
    description="Shuffles around which secret cave entrances take you into which secret caves.",
  )
  randomize_miniboss_entrances: bool = option(
    default=False,
    description="Allows dungeon miniboss doors to act as entrances to be randomized.<br>"
      "If this option is enabled with random dungeon entrances, dungeons may nest within each other, forming chains of connected dungeons.",
  )
  randomize_boss_entrances: bool = option(
    default=False,
    description="Allows dungeon boss doors to act as entrances to be randomized.<br>"
      "If this option is enabled with random dungeon entrances, dungeons may nest within each other, forming chains of connected dungeons.",
  )
  randomize_secret_cave_inner_entrances: bool = option(
    default=False,
    description="Allows the pit in Ice Ring Isle's secret cave and the rear exit out of Cliff Plateau Isles' secret cave to act as entrances to be randomized.",
  )
  randomize_fairy_fountain_entrances: bool = option(
    default=False,
    description="Allows the pits that lead down into Fairy Fountains to act as entrances to be randomized.",
  )
  mix_entrances: EntranceMixMode = option(
    default=EntranceMixMode.SEPARATE_DUNGEONS,
    description="Controls whether dungeons should be separated from other randomized entrances, or if all types of randomized entrances can lead into each other.",
    choice_descriptions={
      EntranceMixMode.SEPARATE_DUNGEONS:
        "Dungeon entrances will only be randomized to lead into other dungeons.",
      EntranceMixMode.MIX_DUNGEONS:
        "Dungeon entrances may be randomized to lead into areas that are not dungeons too.",
    },
  )
  #endregion
  
  #region Other randomizers
  randomize_enemies: bool = option(
    default=False,
    hidden=True,
    unbeatable=True,
    description="Randomizes the placement of non-boss enemies.",
  )
  randomize_enemy_palettes: bool = option(
    default=False,
    permalink=True, # TODO: Has special logic to be in when enemy rando is on, but just a placeholder otherwise. How to handle this?
    description="Gives all the enemies in the game random colors.",
  )
  # randomize_music: bool = option(
  #   default=False,
  #   permalink=True, # Music duration affects gameplay (e.g. item get textbox speed).
  #   hidden=True,
  #   description="Shuffles around all the music in the game. This affects background music, combat music, fanfares, etc.",
  # ),
  randomize_starting_island: bool = option(
    default=True,
    description="Randomizes which island you start the game on.",
  )
  randomize_charts: bool = option(
    default=False,
    description="Randomizes which sector is drawn on each Triforce/Treasure Chart.",
  )
  #endregion
  
  #region Hints
  hoho_hints: bool = option(
    default=False,
    description="Places hints on Old Man Ho Ho. Old Man Ho Ho appears at 10 different islands in the game. Talk to Old Man Ho Ho to get hints.<br>"
      "This setting is mutually exclusive with having Old Man Ho Ho hint Triforce Shards.",
  )
  fishmen_hints: bool = option(
    default=False,
    description="Places hints on the fishmen. There is one fishman at each of the 49 islands of the Great Sea. Each fishman must be fed an All-Purpose Bait before he will give a hint.",
  )
  korl_hints: bool = option(
    default=True,
    description="Places hints on the King of Red Lions. Talk to the King of Red Lions to get hints.",
  )
  num_item_hints: int = option(
    default=0,
    minimum=0,
    maximum=15,
    description="The number of item hints that will be placed. Item hints tell you which area contains a particular progress item in this seed.<br>"
      "If multiple hint placement options are selected, the hint count will be split evenly among the placement options.",
  )
  num_location_hints: int = option(
    default=6,
    minimum=0,
    maximum=15,
    description="The number of location hints that will be placed. Location hints tell you what item is at a specific location in this seed.<br>"
      "If multiple hint placement options are selected, the hint count will be split evenly among the placement options.",
  )
  num_barren_hints: int = option(
    default=5,
    minimum=0,
    maximum=15,
    description="The number of barren hints that will be placed. Barren hints tell you that an area does not contain any required items in this seed.<br>"
      "If multiple hint placement options are selected, the hint count will be split evenly among the placement options.",
  )
  num_path_hints: int = option(
    default=3,
    minimum=0,
    maximum=15,
    description="The number of path hints that will be placed. Path hints tell you that an area contains an item that is required to reach a particular goal in this seed.<br>"
      "If multiple hint placement options are selected, the hint count will be split evenly among the placement options.",
  )
  cryptic_hints: bool = option(
    default=False,
    description="When this option is selected, all hints will be phrased cryptically instead of telling you the names of locations and items directly.",
  )
  prioritize_remote_hints: bool = option(
    default=True,
    description="When this option is selected, certain locations that are out of the way and time-consuming to complete will take precedence over normal location hints.",
  )
  hint_importance: bool = option(
    default=True,
    description="When this option is selected, item and location hints will also indicate if the hinted item is required, possibly required, or not required.<br>"
      "Only progress items will have these additions; non-progress items are trivially not required."
  )
  hoho_hint_shards: bool = option(
    default=False,
    description="When this option is selected, each Old Man Ho Ho will give an item hint for a random Triforce Shard. Hints are not repeated until each Shard is hinted once.<br>"
      "This setting is mutually exclusive with the Old Man Ho Ho hint placement option.",
  )
  korl_hints_swords: bool = option(
    default=False,
    description="When this option is selected, the King of Red Lions will give an item hint for each Progressive Sword if spoken to in Hyrule.",
  )
  kreeb_hints_bows: bool = option(
    default=True,
    description="When this option is selected, Kreeb will give an item hint for each Progressive Bow after Link reactivates the Windfall lighthouse.",
  )
  #endregion
  
  #region Logic Tweaks
  always_double_magic: bool = option(
    default=True,
    description="The first Progressive Magic Meter grants double magic instead of single magic. The second Progressive Magic Meter refills your magic instead of upgrading capacity.<br>"
      "Logic considers one Progressive Magic Meter as having the Magic Meter Upgrade.",
  )
  open_drc: bool = option(
    default=False,
    description="Allow DRC entrance to be accessed from the beginning of the game with no items."
  )
  #endregion
  
  #region Miscellaneous Dev Features
  rainbow_rupee_progress: bool = option(
    default=False,
    description="Place the Rainbow Rupee into the progress item pool. This means that it will be found in a progress location. If CTMC is enabled, it will be in a metal chest.<br>"
      "This setting has no effect on the logic.",
  )
  #endregion
  
  #region Tweaks
  swift_sail: bool = option(
    default=True,
    description="Sailing speed is doubled and the direction of the wind is always at your back as long as the sail is out.",
  )
  instant_text_boxes: bool = option(
    default=True,
    description="Text appears instantly.<br>"
      "Also, the B button is changed to instantly skip through text as long as you hold it down.",
  )
  reveal_full_sea_chart: bool = option(
    default=True,
    description="Start the game with the sea chart fully drawn out.",
  )
  add_shortcut_warps_between_dungeons: bool = option(
    default=True,
    description="Adds new warp pots that act as shortcuts connecting dungeons to each other directly. (DRC, FW, TotG, and separately FF, ET, WT.)<br>"
      "Each pot must be unlocked before it can be used, so you cannot use them to access dungeons you wouldn't already have access to.",
  )
  skip_rematch_bosses: bool = option(
    default=True,
    description="Removes the door in Ganon's Tower that only unlocks when you defeat the rematch versions of Gohma, Kalle Demos, Jalhalla, and Molgera.",
  )
  invert_camera_x_axis: bool = option(
    default=False,
    permalink=False,
    description="Inverts the horizontal axis of camera movement.",
  )
  invert_sea_compass_x_axis: bool = option(
    default=False,
    permalink=False,
    description="Inverts the east-west direction of the compass that shows while at sea.",
  )
  remove_title_and_ending_videos: bool = option(
    default=True,
    permalink=False,
    description="Removes the two prerendered videos that play if you wait on the title screen and after you beat the game. (This cuts the ISO's filesize in half.)<br>"
      "If you keep these videos in, they won't reflect your custom player model or colors.",
  )
  remove_music: bool = option(
    default=False,
    permalink=True, # Music duration affects gameplay (e.g. item get textbox speed).
    description="Mutes all ingame music.",
  )
  switch_targeting_mode: bool = option(
    default=False,
    permalink=False,
    description="Changes the default L-targeting mode when starting a new save file from 'Hold' to 'Switch'.",
  )
  #endregion
  
  #region Starting items
  randomized_gear: list[str] = option(
    default_factory=lambda: [
      "Bait Bag",
      "Beedle's Chart",
      "Bombs",
      "Boomerang",
      "Cabana Deed",
      "DRC Big Key",
      "DRC Compass",
      "DRC Dungeon Map",
      "DRC Small Key",
      "DRC Small Key",
      "DRC Small Key",
      "DRC Small Key",
      "Deku Leaf",
      "Delivery Bag",
      "ET Big Key",
      "ET Compass",
      "ET Dungeon Map",
      "ET Small Key",
      "ET Small Key",
      "ET Small Key",
      "Empty Bottle",
      "FF Compass",
      "FF Dungeon Map",
      "FW Big Key",
      "FW Compass",
      "FW Dungeon Map",
      "FW Small Key",
      "Farore's Pearl",
      "Fill-Up Coupon",
      "Ghost Ship Chart",
      "Goddess Tingle Statue",
      "Grappling Hook",
      "Great Fairy Chart",
      "Hero's Charm",
      "Hookshot",
      "Hurricane Spin",
      "Iron Boots",
      "Light Ring Chart",
      "Maggie's Letter",
      "Magic Armor",
      "Moblin's Letter",
      "Note to Mom",
      "Octo Chart",
      "Platform Chart",
      "Power Bracelets",
      "Progressive Bomb Bag",
      "Progressive Bomb Bag",
      "Progressive Bow",
      "Progressive Bow",
      "Progressive Bow",
      "Progressive Magic Meter",
      "Progressive Magic Meter",
      "Progressive Picto Box",
      "Progressive Picto Box",
      "Progressive Quiver",
      "Progressive Quiver",
      "Progressive Shield",
      "Progressive Shield",
      "Progressive Sword",
      "Progressive Sword",
      "Progressive Sword",
      "Progressive Wallet",
      "Progressive Wallet",
      "Secret Cave Chart",
      "Skull Hammer",
      "Soul of Gohdan",
      "Soul of Gohma",
      "Soul of Helmaroc King",
      "Soul of Jalhalla",
      "Soul of Kalle Demos",
      "Soul of Molgera",
      "Spoils Bag",
      "Submarine Chart",
      "Tingle Tuner",
      "Tingle's Chart",
      "TotG Big Key",
      "TotG Compass",
      "TotG Dungeon Map",
      "TotG Small Key",
      "TotG Small Key",
      "WT Big Key",
      "WT Compass",
      "WT Dungeon Map",
      "WT Small Key",
      "WT Small Key",
      "Wind Tingle Statue",
    ],
    description="Inventory items that will be randomized.",
  )
  starting_gear: list[str] = option(
    default_factory=lambda: [
      "Ballad of Gales",
      "Command Melody",
      "Din's Pearl",
      "Dragon Tingle Statue",
      "Earth God's Lyric",
      "Earth Tingle Statue",
      "Forbidden Tingle Statue",
      "Nayru's Pearl",
      "Song of Passing",
      "Telescope",
      "Wind God's Aria",
    ],
    description="Items that will be in your inventory at the start of a new game.",
  )
  num_starting_triforce_shards: int = option(
    default=0,
    minimum=0,
    maximum=8,
    description="Change the number of Triforce Shards you start the game with.<br>"
      "The higher you set this, the fewer you will need to find placed randomly to beat the game.",
  )
  starting_pohs: int = option(
    default=0,
    minimum=0,
    maximum=44,
    description="Amount of extra pieces of heart that you start with.",
  )
  starting_hcs: int = option(
    default=3,
    minimum=1,
    maximum=9,
    description="Amount of extra heart containers that you start with.",
  )
  starting_joy_pendant: int = option(
    default=0,
    minimum=0,
    maximum=99,
    description="Amount of Joy Pendants to start with.<br>"
      "This is a convenience setting and does not affect the logic.",
  )
  starting_skull_necklace: int = option(
    default=19,
    minimum=0,
    maximum=99,
    description="Amount of Skull Necklaces to start with.<br>"
      "This is a convenience setting and does not affect the logic.",
  )
  starting_boko_baba_seed: int = option(
    default=0,
    minimum=0,
    maximum=99,
    description="Amount of Boko Baba Seeds to start with.<br>"
      "This is a convenience setting and does not affect the logic.",
  )
  starting_golden_feather: int = option(
    default=0,
    minimum=0,
    maximum=99,
    description="Amount of Golden Feathers to start with.<br>"
      "This is a convenience setting and does not affect the logic.",
  )
  starting_knights_crest: int = option(
    default=10,
    minimum=0,
    maximum=99,
    description="Amount of Knight's Crests to start with.<br>"
      "This is a convenience setting and does not affect the logic.",
  )
  starting_red_chu_jelly: int = option(
    default=0,
    minimum=0,
    maximum=99,
    description="Amount of Red Chu Jellies to start with.<br>"
      "This is a convenience setting and does not affect the logic.",
  )
  starting_green_chu_jelly: int = option(
    default=14,
    minimum=0,
    maximum=99,
    description="Amount of Green Chu Jellies to start with.<br>"
      "This is a convenience setting and does not affect the logic.",
  )
  starting_blue_chu_jelly: int = option(
    default=0,
    minimum=0,
    maximum=99,
    description="Amount of Blue Chu Jellies to start with.<br>"
      "When Blue ChuChu shuffle is enabled, these count toward the Blue Chu Jelly progression requirement.",
  )
  num_extra_starting_items: int = option(
    default=1,
    minimum=0,
    maximum=3,
    description="Amount of extra random progression items that you start with.<br>"
      "Guaranteed to unlock at least one additional location at the start.",
  )
  #endregion

  #region Quality of Life
  mila_speedup: MilaSpeedup = option(
    default=MilaSpeedup.NONE,
    description="Speeds up Mila walk cycle when doing the Follow the Thief sidequest.",
    choice_descriptions={
      MilaSpeedup.NONE:
        "None: Vanilla behavior.",
      MilaSpeedup.SHORTENED:
        "Shortened: Mila will take a different, shorter path without stopping.",
      MilaSpeedup.INSTANT:
        "Instant: Mila will take a path straight to the safe without stopping."
    },
  )
  split_interdungeon_warps_by_required: bool = option(
    default=True,
    description="Splits warp pots into separate cycles for required and non-required dungeons.<br>"
      "Only takes effect with Required Bosses Mode, Inter-Dungeon Shortcuts, and exactly 1-3 required bosses.",
  )
  remove_ballad_of_gales_warp_in_cutscene: bool = option(
    default=False,
    description="Removes the Ballad of Gales warp landing cutscene."
  )
  always_skip_triforce_cutscene: bool = option(
    default=False,
    description="Always skip the cutscene that plays when you first board KoRL after collecting all 8 Triforce Shards."
  )
  add_drops: bool = option(
    default=False,
    description="Modifies and adds bomb, arrow, and magic drop pots/barrels on the following islands:<br>"
    "Outset, Southern Fairy, Western Fairy, Tingle, Pawprint, Stone Watcher, Dragon Roost, Needle Rock, and Forest Haven."
  )
  speedup_lenzos_assistant: bool = option(
    default=False,
    description="Speed up Lenzo's Assistant sidequest by speeding up Garrickson and Anton's movement around Windfall."
  )
  kamo_any_moon_phase: bool = option(
    default=True,
    description="Kamo will accept a picture of any moon phase, rather than just a full moon."
  )
  shorten_mail_minigame: bool = option(
    default=True,
    description="The mail sorting minigame on Dragon Roost Island is shortened to the final round with Baito."
  )
  skip_drc_plat_cs: bool = option(
    default=False,
    description="Skip the DRC cutscenes that play when riding the hanging platform and making a magma platform for the first time."
  )
  wallet_fill_behavior: bool = option(
    default=False,
    description="Fill each progressive wallet when received."
  )
  speedup_tingle_jail: bool = option(
    default=False,
    description="Speed up the cutscene that plays when Tingle is freed from jail.<br>"
      "Slightly speed up the cutscene that plays when Link approaches jailed Tingle's bars."
    )
  fix_auction: bool = option(
    default=False,
    description="Remove RNG from the auction by fixing the cycle to increasing price order.<br>"
      "The prizes for each auction will be displayed on the auction flyer inside the House of Wealth."
    )
  totg_tablet_from_start: bool = option(
    default=False,
    description="Makes the Command Melody tablet in Tower of the Gods visible from the start. Once the tablet check is obtained, the portal appears without needing to bring the statues.<br>"
      "This changes the logic for Stone Tablet and accessing the third floor in Tower of the Gods."
    )
  quick_gohma: bool = option(
    default=False,
    description="Shortens the Gohma fight to require only 1 tail grapple instead of 3 to trigger phase 2. Also skips the transition cutscene."
  )
  sunlight_arrows: bool = option(
    default=False,
    description="Light Arrows fired from Link's bow can activate all mirror-light puzzles in the game, including walls, sun switches, stone statues, and coffins.<br>"
    "This changes the logic in Earth Temple, Angular Isles, and Savage Labyrinth."
  )
  sea_companion: SeaCompanion = option(
    default=SeaCompanion.NONE,
    permalink=False,
    description="Controls which sage rides the King of Red Lions as a companion on the Great Sea.",
    choice_descriptions={
      SeaCompanion.NONE: "No companion will ride the ship.",
      SeaCompanion.MEDLI: "Medli will ride the ship.",
      SeaCompanion.MAKAR: "Makar will ride the ship.",
      SeaCompanion.BOTH: "Both Medli and Makar will ride the ship.",
      SeaCompanion.RANDOM: "Randomly selects between Medli, Makar, or Both per seed.",
    },
  )
  #endregion
  
  #region Cosmetic
  custom_player_model: str = option(
    default="Link",
    permalink=False,
    description="Replaces Link's model with a custom player model.<br>"
      "These are loaded from the /models folder.",
  )
  player_in_casual_clothes: bool = option(
    default=False,
    permalink=False,
    description="Enable this if you want to wear your casual clothes instead of the Hero's Clothes.",
  )
  disable_custom_player_voice: bool = option(
    default=False,
    permalink=False,
    description="If the chosen custom model comes with custom voice files, you can check this option to turn them off and use Link's normal voice instead.",
  )
  disable_custom_player_items: bool = option(
    default=False,
    permalink=False,
    description="If the chosen custom model comes with custom item models, you can check this option to turn them off and use Link's normal item models instead.",
  )
  custom_color_preset: str = option(
    default="Default",
    permalink=False,
    description="This allows you to select from preset color combinations chosen by the author of the selected player model.",
  )
  custom_colors: dict[str, list] = option(
    default_factory=dict,
    permalink=False,
  )
  #endregion
  
  #region Meta
  do_not_generate_spoiler_log: bool = option(
    default=True,
    description="Prevents the randomizer from generating a text file listing out the locations of all items in this seed. (Also changes where items are placed in this seed.)<br>"
      "<u>Generating a spoiler log is highly recommended even if you don't intend to use it</u>, just in case you get completely stuck.",
  )
  dry_run: bool = option(
    default=False,
    permalink=False,
    description="If this option is selected, <u>no playable ISO will be generated</u>, but the log files will still be created.<br>"
      "This can be useful if you want to generate a spoiler log on a computer where you do not have a vanilla Wind Waker ISO.",
  )
  #endregion
