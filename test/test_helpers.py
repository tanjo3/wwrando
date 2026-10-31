from options.wwrando_options import Options, SwordMode, EntranceMixMode, TrickDifficulty, KeyLunacyMode
from logic.logic import Logic
from randomizer import Plando
from randomizers.entrances import (
  DUNGEON_ENTRANCES, MINIBOSS_ENTRANCES, BOSS_ENTRANCES, SECRET_CAVE_ENTRANCES, SECRET_CAVE_INNER_ENTRANCES, FAIRY_FOUNTAIN_ENTRANCES,
  DUNGEON_EXITS, MINIBOSS_EXITS, BOSS_EXITS, SECRET_CAVE_EXITS, SECRET_CAVE_INNER_EXITS, FAIRY_FOUNTAIN_EXITS,
)

def own_item(name: str, classification: str = "progression") -> dict:
  return {"player": 1, "name": name, "game": "The Wind Waker", "classification": classification}

def foreign_item(name: str = "Lantern", classification: str = "progression") -> dict:
  return {"player": 2, "name": name, "game": "Other Game", "classification": classification}

def nothing_item() -> dict:
  return {"name": "Nothing", "game": "The Wind Waker", "classification": "filler"}

def make_filler_plando(options: Options) -> Plando:
  plando = make_test_plando(options)
  for location_name in plando.locations:
    plando.locations[location_name] = own_item("Green Rupee", "filler")
  return plando

def make_test_plando(options: Options) -> Plando:
  item_locations = Logic.load_and_parse_item_locations()
  location_names = Logic.filter_locations_for_progression_static(
    list(item_locations), item_locations, options,
    filter_sunken_treasure=not (options.progression_triforce_charts and options.progression_treasure_charts),
  )
  locations = {
    location_name: own_item("Green Rupee", "filler")
    for location_name in location_names
  }
  
  own_progression = {
    "Dragon Roost Cavern - First Room": "Deku Leaf",
    "Dragon Roost Cavern - Alcove With Water Jugs": "DRC Small Key",
    "Dragon Roost Cavern - Boarded Up Chest": "DRC Big Key",
  }
  for location_name, item_name in own_progression.items():
    if location_name in locations:
      locations[location_name] = own_item(item_name)
  for location_name in ["Dragon Roost Cavern - Rat Room", "Outset Island - Savage Labyrinth - Floor 30"]:
    if location_name in locations:
      locations[location_name] = foreign_item()
  
  required_bosses = []
  if options.required_bosses:
    boss_locations = [name for name, location in item_locations.items() if "Boss" in location["Types"]]
    required_bosses = boss_locations[:options.num_required_bosses]
  
  zone_entrances = DUNGEON_ENTRANCES + MINIBOSS_ENTRANCES + BOSS_ENTRANCES + SECRET_CAVE_ENTRANCES + SECRET_CAVE_INNER_ENTRANCES + FAIRY_FOUNTAIN_ENTRANCES
  zone_exits = DUNGEON_EXITS + MINIBOSS_EXITS + BOSS_EXITS + SECRET_CAVE_EXITS + SECRET_CAVE_INNER_EXITS + FAIRY_FOUNTAIN_EXITS
  entrances = {zone_entrance.entrance_name: zone_exit.unique_name for zone_entrance, zone_exit in zip(zone_entrances, zone_exits)}
  
  return Plando("pytestseed", 1, "Player1", required_bosses, locations, entrances, list(range(1, 49+1)))

def enable_all_progression_location_options(options: Options):
  options.progression_dungeons = True
  options.progression_great_fairies = True
  options.progression_puzzle_secret_caves = True
  options.progression_combat_secret_caves = True
  options.progression_short_sidequests = True
  options.progression_long_sidequests = True
  options.progression_spoils_trading = True
  options.progression_minigames = True
  options.progression_free_gifts = True
  options.progression_mail = True
  options.progression_platforms_rafts = True
  options.progression_submarines = True
  options.progression_eye_reef_chests = True
  options.progression_big_octos_gunboats = True
  options.progression_triforce_charts = True
  options.progression_treasure_charts = True
  options.progression_expensive_purchases = True
  options.progression_misc = True
  options.progression_tingle_chests = True
  options.progression_battlesquid = True
  options.progression_savage_labyrinth = True
  options.progression_island_puzzles = True
  options.progression_dungeon_secrets = True

def disable_all_progression_location_options(options: Options):
  options.progression_dungeons = False
  options.progression_great_fairies = False
  options.progression_puzzle_secret_caves = False
  options.progression_combat_secret_caves = False
  options.progression_short_sidequests = False
  options.progression_long_sidequests = False
  options.progression_spoils_trading = False
  options.progression_minigames = False
  options.progression_free_gifts = False
  options.progression_mail = False
  options.progression_platforms_rafts = False
  options.progression_submarines = False
  options.progression_eye_reef_chests = False
  options.progression_big_octos_gunboats = False
  options.progression_triforce_charts = False
  options.progression_treasure_charts = False
  options.progression_expensive_purchases = False
  options.progression_misc = False
  options.progression_tingle_chests = False
  options.progression_battlesquid = False
  options.progression_savage_labyrinth = False
  options.progression_island_puzzles = False
  options.progression_dungeon_secrets = False

def enable_all_options(options: Options):
  enable_all_progression_location_options(options)
  
  options.sword_mode = SwordMode.SWORDLESS
  options.randomize_mapcompass = KeyLunacyMode.KEYLUNACY
  options.randomize_smallkeys = KeyLunacyMode.KEYLUNACY
  options.randomize_bigkeys = KeyLunacyMode.KEYLUNACY
  
  options.mix_entrances = EntranceMixMode.MIX_DUNGEONS
  options.randomize_dungeon_entrances = True
  options.randomize_secret_cave_entrances = True
  options.randomize_miniboss_entrances = True
  options.randomize_boss_entrances = True
  options.randomize_secret_cave_inner_entrances = True
  options.randomize_fairy_fountain_entrances = True
  
  options.randomize_enemy_palettes = True
  
  options.randomize_enemies = True
  
  options.randomize_charts = True
  
  options.randomize_starting_island = True
  
  options.required_bosses = True
  options.num_required_bosses = 4
  
  options.chest_type_matches_contents = True
  
  options.trap_chests = True
  
  options.fishmen_hints = True
  options.hoho_hints = True
  options.korl_hints = True
  options.num_path_hints = 15
  options.num_barren_hints = 15
  options.num_location_hints = 15
  options.num_item_hints = 15
  options.cryptic_hints = True
  options.prioritize_remote_hints = True
  options.hint_importance = True
  
  options.do_not_generate_spoiler_log = False
  
  options.swift_sail = True
  options.instant_text_boxes = True
  options.reveal_full_sea_chart = True
  options.add_shortcut_warps_between_dungeons = True
  options.skip_rematch_bosses = True
  options.invert_camera_x_axis = True
  options.invert_sea_compass_x_axis = True
  options.remove_title_and_ending_videos = True
  options.remove_music = True
  options.switch_targeting_mode = True
  
  # options.custom_player_model
  # options.player_in_casual_clothes
  # options.disable_custom_player_voice
  # options.disable_custom_player_items
  # options.custom_color_preset
  # options.custom_colors
  
  options.num_starting_triforce_shards = 4
  # options.randomized_gear
  # options.starting_gear
  options.starting_pohs = 3
  options.starting_hcs = 2
  options.num_extra_starting_items = 3
  
  # options.dry_run
  
  options.logic_obscurity = TrickDifficulty.VERY_HARD
  options.logic_precision = TrickDifficulty.VERY_HARD
  options.hero_mode = True
