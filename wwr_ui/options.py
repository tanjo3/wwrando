
from collections import OrderedDict

OPTIONS = OrderedDict([
  (
    "log_generation",
    "Choose which text files listing out information about the seed will be generated. (This also changes where items are placed in this seed.)<br><u>Generating a spoiler log is highly recommended even if you don't intend to use it</u>, just in case you get completely stuck."
  ),
  (
    "target_checks",
    "Select a difficulty level for random settings.<br> The number doesn't exactly mean anything per se, but would roughly correspond to the number of progression locations expected in the seed. Longer or more difficult locations count for more, close-by or easier locations for less.",
  ),
  (
    "randomization_style",
    "Choose between conservative settings (following original weights) or wilder settings (all options have an equal chance of being on or off)"
  ),
  (
    "invert_camera_x_axis",
    "Inverts the horizontal axis of camera movement.",
  ),
  (
    "invert_sea_compass_x_axis",
    "Inverts the east-west direction of the compass that shows while at sea.",
  ),
  (
    "randomize_enemy_palettes",
    "Gives all the enemies in the game random colors.",
  ),
  (
    "remove_title_and_ending_videos",
    "Removes the two prerendered videos that play if you wait on the title screen and after you beat the game. (Decreases randomized ISO's filesize by about 600MB.)\nIf you keep these videos in, they won't reflect your custom player model or colors.",
  ),
  
  
  (
    "custom_player_model",
    "Replaces Link's model with a custom player model.\nThese are loaded from the /models folder."
  ),
  (
    "player_in_casual_clothes",
    "Enable this if you want to wear your casual clothes instead of the Hero's Clothes."
  ),
  (
    "disable_custom_player_voice",
    "If the chosen custom model comes with custom voice files, you can check this option to turn them off and simply use Link's normal voice instead."
  ),
  (
    "disable_custom_player_items",
    "If the chosen custom model comes with custom item models, you can check this option to turn them off and simply use Link's normal item models instead."
  ),
  (
    "custom_color_preset",
    "This allows you to select from preset color combinations chosen by the author of the selected player model."
  ),
])

NON_PERMALINK_OPTIONS = [
  "invert_camera_x_axis",
  "invert_sea_compass_x_axis",
  "custom_player_model",
  "player_in_casual_clothes",
  "disable_custom_player_voice",
  "disable_custom_player_items",
  "custom_color_preset",
  "remove_title_and_ending_videos",
  # Note: Options that affect music must be included in the permalink because music duration affects gameplay in some cases, like not being allowed to close the item get textbox until the item get jingle has finished playing.
  # Note: randomize_enemy_palettes has special logic to be in the permalink when enemy rando is on, but otherwise just have an unused placeholder in the permalink.
]

HIDDEN_OPTIONS = [
  "randomize_music",
  "randomize_enemies",
]

POTENTIALLY_UNBEATABLE_OPTIONS = [
  "randomize_enemies",
]
