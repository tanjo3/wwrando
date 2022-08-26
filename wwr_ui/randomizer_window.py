from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from wwr_ui.ui_randomizer_window import Ui_MainWindow
from wwr_ui.options import OPTIONS, NON_PERMALINK_OPTIONS
from wwr_ui.update_checker import check_for_updates, LATEST_RELEASE_DOWNLOAD_PAGE_URL

import random
from collections import OrderedDict

import os
import yaml
import traceback
import string
import colorsys
import time
import zipfile
import shutil

from randomizer import Randomizer, VERSION_WITHOUT_COMMIT, TooFewProgressionLocationsError, InvalidCleanISOError
from wwrando_paths import SETTINGS_PATH, ASSETS_PATH, SEEDGEN_PATH, IS_RUNNING_FROM_SOURCE, CUSTOM_MODELS_PATH
import customizer
from randomizers.settings import randomize_settings
from logic.logic import Logic
from wwlib import texture_utils

class WWRandomizerWindow(QMainWindow):
  VALID_SEED_CHARACTERS = "-_'%%.%s%s" % (string.ascii_letters, string.digits)
  MAX_SEED_LENGTH = 42 # Limited by maximum length of game name in banner
  
  def __init__(self, cmd_line_args=OrderedDict()):
    super(WWRandomizerWindow, self).__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    
    self.randomizer_thread = None
    
    self.cmd_line_args = cmd_line_args
    self.bulk_test = ("-bulk" in cmd_line_args)
    self.bulk_test_amount = 100
    if self.bulk_test and cmd_line_args["-bulk"] is not None:
      self.bulk_test_amount = int(cmd_line_args["-bulk"])
    self.no_ui_test = ("-noui" in cmd_line_args)
    self.profiling = ("-profile" in cmd_line_args)
    self.auto_seed = ("-autoseed" in cmd_line_args)

    self.custom_color_selector_buttons = OrderedDict()
    self.custom_color_selector_hex_inputs = OrderedDict()
    self.custom_color_reset_buttons = OrderedDict()
    self.custom_colors = OrderedDict()
    self.initialize_custom_player_model_list()
    self.initialize_color_presets_list()
    
    self.preserve_default_settings()
    
    self.cached_item_locations = Logic.load_and_parse_item_locations()
    
    self.load_settings()
    
    self.ui.clean_iso_path.editingFinished.connect(self.update_settings)
    self.ui.output_folder.editingFinished.connect(self.update_settings)
    self.ui.seed.editingFinished.connect(self.update_settings)
    self.ui.clean_iso_path_browse_button.clicked.connect(self.browse_for_clean_iso)
    self.ui.output_folder_browse_button.clicked.connect(self.browse_for_output_folder)

    self.ui.install_custom_model.clicked.connect(self.install_custom_model_zip)
    self.ui.custom_player_model.currentIndexChanged.connect(self.custom_model_changed)
    self.ui.player_in_casual_clothes.toggled.connect(self.in_casual_clothes_changed)
    self.ui.randomize_all_custom_colors_together.clicked.connect(self.randomize_all_custom_colors_together)
    self.ui.randomize_all_custom_colors_separately.clicked.connect(self.randomize_all_custom_colors_separately)
    self.ui.custom_color_preset.currentIndexChanged.connect(self.color_preset_changed)
    
    for option_name in OPTIONS:
      try:
        widget = getattr(self.ui, option_name)
        if isinstance(widget, QAbstractButton):
          widget.clicked.connect(self.update_settings)
        elif isinstance(widget, QComboBox):
          widget.currentIndexChanged.connect(self.update_settings)
        elif isinstance(widget, QListView):
          pass
        elif isinstance(widget, QSpinBox):
          widget.valueChanged.connect(self.update_settings)
        else:
          raise Exception("Option widget is invalid: %s" % option_name)
      except:
        pass
    
    self.ui.generate_seed_button.clicked.connect(self.generate_seed)
    
    self.ui.randomize_button.clicked.connect(self.randomize)
    self.ui.reset_settings_to_default.clicked.connect(self.reset_settings_to_default)
    self.ui.about_button.clicked.connect(self.open_about)
    
    for option_name in OPTIONS:
      try:
        getattr(self.ui, option_name).installEventFilter(self)
        label_for_option = getattr(self.ui, "label_for_" + option_name, None)
        if label_for_option:
          label_for_option.installEventFilter(self)
      except:
        pass
    self.set_option_description(None)
    
    self.update_settings()
    
    self.setWindowTitle("WWR Random Settings %s" % VERSION_WITHOUT_COMMIT)
    
    icon_path = os.path.join(ASSETS_PATH, "icon.ico")
    self.setWindowIcon(QIcon(icon_path))
    
    if self.auto_seed:
      self.generate_seed()

    if self.no_ui_test:
      self.randomize()
      return
    
    self.show()
    
    self.ui.update_checker_label.setText("<b>This is a build specifically for random settings.</b> For updates, please join the WWR Racing Discord server. For questions and bug reports, please contact tanjo3#5077 on Discord.")
  
  def generate_seed(self):
    random.seed(None)
    
    with open(os.path.join(SEEDGEN_PATH, "adjectives.txt")) as f:
      adjectives = random.sample(f.read().splitlines(), 2)
    noun_file_to_use = random.choice(["nouns.txt", "names.txt"])
    with open(os.path.join(SEEDGEN_PATH, noun_file_to_use)) as f:
      noun = random.choice(f.read().splitlines())
    words = adjectives + [noun]
    capitalized_words = []
    for word in words:
      capitalized_word = ""
      seen_first_letter = False
      for char in word:
        if char in string.ascii_letters and not seen_first_letter:
          capitalized_word += char.capitalize()
          seen_first_letter = True
        else:
          capitalized_word += char
      capitalized_words.append(capitalized_word)
    seed = "".join(capitalized_words)
    
    seed = self.sanitize_seed(seed)
    
    self.settings["seed"] = seed
    self.ui.seed.setText(seed)
    self.update_settings()
  
  def sanitize_seed(self, seed):
    seed = str(seed)
    seed = seed.strip()
    seed = "".join(char for char in seed if char in self.VALID_SEED_CHARACTERS)
    seed = seed[:self.MAX_SEED_LENGTH]
    return seed
  
  def randomize(self):
    clean_iso_path = self.settings["clean_iso_path"].strip()
    output_folder = self.settings["output_folder"].strip()
    self.settings["clean_iso_path"] = clean_iso_path
    self.settings["output_folder"] = output_folder
    self.ui.clean_iso_path.setText(clean_iso_path)
    self.ui.output_folder.setText(output_folder)
    
    if not os.path.isfile(clean_iso_path) and not self.no_ui_test:
      QMessageBox.warning(self, "Clean ISO path not specified", "Must specify path to your clean Wind Waker ISO (USA).")
      return
    if not os.path.isdir(output_folder) and not self.no_ui_test:
      QMessageBox.warning(self, "No output folder specified", "Must specify a valid output folder for the randomized files.")
      return
    
    if self.bulk_test:
      failures_done = 0
      total_done = 0
      for i in range(self.bulk_test_amount):
        temp_seed = "RS_" + VERSION_WITHOUT_COMMIT + "_" + str(i)
        try:
          options = randomize_settings(seed=temp_seed)
          rando = Randomizer(temp_seed, str(i), clean_iso_path, output_folder, options, cmd_line_args=self.cmd_line_args)
          randomizer_generator = rando.randomize()
          while True:
            next_option_description, options_finished = next(randomizer_generator)
            if options_finished == -1:
              break
          rando.write_spoiler_log()
        except Exception as e:
          stack_trace = traceback.format_exc()
          error_message = "Error on seed " + temp_seed + ":\n" + str(e) + "\n\n" + stack_trace
          print(error_message)
          failures_done += 1
        total_done += 1
        print("%d/%d seeds failed" % (failures_done, total_done))
      return
    
    if "-seed" in self.cmd_line_args:
      seed = self.cmd_line_args["-seed"]
    else:
      seed = self.settings["seed"]
    seed = self.sanitize_seed(seed)
    
    if not seed:
      self.generate_seed()
      seed = self.settings["seed"]
    
    self.settings["seed"] = seed
    self.ui.seed.setText(seed)
    self.update_settings()
    
    original_seed = seed
    seed = "RS_" + VERSION_WITHOUT_COMMIT + "_" + seed
    
    n_attempts = 0
    max_attempts = 10
    error_message = ""
    while n_attempts < max_attempts:
      options = randomize_settings(seed=seed+str(n_attempts))
      for option_name in NON_PERMALINK_OPTIONS:
        options[option_name] = self.get_option_value(option_name)
      
      colors = OrderedDict()
      for color_name in self.get_default_custom_colors_for_current_model():
        colors[color_name] = self.get_color(color_name)
      options["custom_colors"] = colors
      
      max_progress_val = 20
      if options.get("randomize_enemy_palettes"):
        max_progress_val += 10
      if not self.no_ui_test:
        self.progress_dialog = RandomizerProgressDialog("Randomizing", "Initializing...", max_progress_val)
      
      cmd_line_args = self.cmd_line_args.copy()
      if self.no_ui_test:
        cmd_line_args["-dry"] = None
      cmd_line_args["-nologs"] = None
      
      try:
        rando = Randomizer(seed, original_seed, clean_iso_path, output_folder, options, cmd_line_args=cmd_line_args)
        break
      except (TooFewProgressionLocationsError, InvalidCleanISOError) as e:
        error_message = str(e)
        n_attempts += 1
      except Exception as e:
        stack_trace = traceback.format_exc()
        error_message = "Randomization failed with error:\n" + str(e) + "\n\n" + stack_trace
        n_attempts += 1
    else:
      self.randomization_failed(error_message)
      return
    
    if self.no_ui_test:
      randomizer_generator = rando.randomize()
      while True:
        next_option_description, options_finished = next(randomizer_generator)
        if options_finished == -1:
          break
    else:
      self.randomizer_thread = RandomizerThread(rando, profiling=self.profiling)
      self.randomizer_thread.update_progress.connect(self.update_progress_dialog)
      self.randomizer_thread.randomization_complete.connect(self.randomization_complete)
      self.randomizer_thread.randomization_failed.connect(self.randomization_failed)
      self.randomizer_thread.start()
  
  def update_progress_dialog(self, next_option_description, options_finished):
    self.progress_dialog.setLabelText(next_option_description)
    self.progress_dialog.setValue(options_finished)
  
  def randomization_complete(self):
    if not self.no_ui_test:
      self.progress_dialog.reset()
    
    self.randomizer_thread = None
    
    if self.no_ui_test:
      self.close()
      QCoreApplication.quit()
      return
    
    text = """Randomization complete.<br><br>
      If you get stuck, check the progression spoiler log in the output folder."""
    
    self.complete_dialog = QMessageBox()
    self.complete_dialog.setTextFormat(Qt.TextFormat.RichText)
    self.complete_dialog.setWindowTitle("Randomization complete")
    self.complete_dialog.setText(text)
    self.complete_dialog.setWindowIcon(self.windowIcon())
    self.complete_dialog.show()
  
  def randomization_failed(self, error_message):
    self.progress_dialog.reset()
    
    if self.randomizer_thread is not None:
      try:
        self.randomizer_thread.randomizer.write_error_log(error_message)
      except Exception as e:
        # If an error happened when writing the error log just print it and then ignore it.
        stack_trace = traceback.format_exc()
        other_error_message = "Failed to write error log:\n" + str(e) + "\n\n" + stack_trace
        print(other_error_message)
    
    self.randomizer_thread = None
    
    print(error_message)
    QMessageBox.critical(
      self, "Randomization Failed",
      error_message
    )
  
  def show_update_check_results(self, new_version):
    if not new_version:
      self.ui.update_checker_label.setText("No new updates to the randomizer are available.")
    elif new_version == "error":
      self.ui.update_checker_label.setText("There was an error checking for updates.")
    else:
      new_text = "<b>Version %s of the randomizer is available!</b>" % new_version
      new_text += " <a href=\"%s\">Click here</a> to go to the download page." % LATEST_RELEASE_DOWNLOAD_PAGE_URL
      self.ui.update_checker_label.setText(new_text)
  
  def preserve_default_settings(self):
    self.default_settings = OrderedDict()
    for option_name in OPTIONS:
      self.default_settings[option_name] = self.get_option_value(option_name)
  
  def reset_settings_to_default(self):
    any_setting_changed = False
    for option_name in OPTIONS:
      if option_name in self.default_settings:
        default_value = self.default_settings[option_name]
        current_value = self.get_option_value(option_name)
        if default_value != current_value:
          any_setting_changed = True
        self.set_option_value(option_name, default_value)
    
    any_color_changed = self.reset_color_selectors_to_model_default_colors()
    if any_color_changed:
      any_setting_changed = True
    
    self.update_settings()
    
    if not any_setting_changed:
      QMessageBox.information(self,
        "Settings already default",
        "You already have all the default randomization settings."
      )
  
  def load_settings(self):
    if os.path.isfile(SETTINGS_PATH):
      with open(SETTINGS_PATH) as f:
        self.settings = yaml.safe_load(f)
      if self.settings is None:
        self.settings = OrderedDict()
    else:
      self.settings = OrderedDict()
    
    if "clean_iso_path" in self.settings:
      self.ui.clean_iso_path.setText(self.settings["clean_iso_path"])
    if "output_folder" in self.settings:
      self.ui.output_folder.setText(self.settings["output_folder"])
    if "seed" in self.settings:
      self.ui.seed.setText(self.settings["seed"])
    
    for option_name in OPTIONS:
      if option_name in self.settings:
        if option_name == "custom_color_preset":
          # Color presets not loaded yet, handle this later
          continue
        self.set_option_value(option_name, self.settings[option_name])
    
    self.reload_custom_model(update_preview=False)
    if "custom_colors" in self.settings:
      custom_colors_from_settings = self.settings["custom_colors"]
      
      # Only read colors into the self.custom_colors dict if they are valid colors for this model.
      for color_name, default_color in self.get_default_custom_colors_for_current_model().items():
        if color_name in custom_colors_from_settings:
          self.custom_colors[color_name] = custom_colors_from_settings[color_name]
        else:
          self.custom_colors[color_name] = default_color
      
      # Update the GUI buttons to match the custom colors (or the preset colors, if a preset is selected).
      for color_name in self.get_default_custom_colors_for_current_model():
        color = self.get_color(color_name)
        option_name = "custom_color_" + color_name
        self.set_color(option_name, color, update_preview=False, save_color_as_custom=False)
    
    if "custom_color_preset" in self.settings:
      self.set_option_value("custom_color_preset", self.settings["custom_color_preset"])
      self.reload_colors()
    
    self.update_model_preview()
  
  def save_settings(self):
    with open(SETTINGS_PATH, "w") as f:
      yaml.dump(self.settings, f, default_flow_style=False, Dumper=yaml.Dumper)
  
  def update_settings(self):
    self.settings["clean_iso_path"] = self.ui.clean_iso_path.text()
    self.settings["output_folder"] = self.ui.output_folder.text()
    self.settings["seed"] = self.ui.seed.text()
    
    self.disable_invalid_cosmetic_options()
    
    for option_name in OPTIONS:
      self.settings[option_name] = self.get_option_value(option_name)
    self.settings["custom_colors"] = self.custom_colors
    
    if not self.no_ui_test:
      self.save_settings()
  
  def browse_for_clean_iso(self):
    if self.settings["clean_iso_path"] and os.path.isfile(self.settings["clean_iso_path"]):
      default_dir = os.path.dirname(self.settings["clean_iso_path"])
    else:
      default_dir = None
    
    clean_iso_path, selected_filter = QFileDialog.getOpenFileName(self, "Select clean Wind Waker ISO", default_dir, "GC ISO Files (*.iso *.gcm)")
    if not clean_iso_path:
      return
    self.ui.clean_iso_path.setText(clean_iso_path)
    self.update_settings()
  
  def browse_for_output_folder(self):
    if self.settings["output_folder"] and os.path.isdir(self.settings["output_folder"]):
      default_dir = self.settings["output_folder"]
    else:
      default_dir = None
    
    output_folder_path = QFileDialog.getExistingDirectory(self, "Select output folder", default_dir)
    if not output_folder_path:
      return
    self.ui.output_folder.setText(output_folder_path)
    self.update_settings()
  
  def eventFilter(self, target, event):
    if event.type() == QEvent.Enter:
      option_name = target.objectName()
      
      if option_name.startswith("label_for_"):
        option_name = option_name[len("label_for_"):]
      
      if option_name in OPTIONS:
        self.set_option_description(OPTIONS[option_name])
      else:
        self.set_option_description(None)
      return True
    elif event.type() == QEvent.Leave:
      self.set_option_description(None)
      return True
    
    return QMainWindow.eventFilter(self, target, event)
  
  def get_option_value(self, option_name):
    try:
      widget = getattr(self.ui, option_name)
      if isinstance(widget, QCheckBox) or isinstance(widget, QRadioButton):
        return widget.isChecked()
      elif isinstance(widget, QComboBox):
        return widget.itemText(widget.currentIndex())
      elif isinstance(widget, QSpinBox):
        return widget.value()
    except:
      return None
  
  def set_option_value(self, option_name, new_value):
    try:
      widget = getattr(self.ui, option_name)
      if isinstance(widget, QCheckBox) or isinstance(widget, QRadioButton):
        widget.setChecked(bool(new_value))
      elif isinstance(widget, QComboBox):
        index_of_value = None
        for i in range(widget.count()):
          text = widget.itemText(i)
          if text == new_value:
            index_of_value = i
            break
        
        if index_of_value is None:
          print("Cannot find value %s in combobox %s" % (new_value, option_name))
          index_of_value = 0
        
        widget.setCurrentIndex(index_of_value)
      elif isinstance(widget, QSpinBox):
        if new_value < widget.minimum() or new_value > widget.maximum():
          print("Value %s out of range for spinbox %s" % (new_value, option_name))
          new_value = self.default_settings[option_name] # reset to default in case 0 is not default or in normal range

        widget.setValue(new_value)
    except:
      pass
  
  def set_option_description(self, new_description):
    if new_description is None:
      self.ui.option_description.setText("(Hover over an option to see a description of what it does.)")
      self.ui.option_description.setStyleSheet("color: grey;")
    else:
      self.ui.option_description.setText(new_description)
      self.ui.option_description.setStyleSheet("")
  
  def initialize_custom_player_model_list(self):
    self.ui.custom_player_model.addItem("Link")
    
    custom_model_names = customizer.get_all_custom_model_names()
    for custom_model_name in custom_model_names:
      self.ui.custom_player_model.addItem(custom_model_name)
    
    if custom_model_names:
      self.ui.custom_player_model.addItem("Random")
      self.ui.custom_player_model.addItem("Random (exclude Link)")
    else:
      self.ui.custom_player_model.setEnabled(False)

  def update_custom_player_model_list(self):
    self.ui.custom_player_model.clear()
    self.initialize_custom_player_model_list()

  def initialize_color_presets_list(self):
    self.ui.custom_color_preset.addItem("Default")
    self.ui.custom_color_preset.addItem("Custom")
    
    self.update_color_presets_list(reload_colors=False)
  
  def update_color_presets_list(self, reload_colors=True):
    # Temporarily prevent the preset changing from regenerating the preview image since we'll be changing it several times in this function.
    self.ui.custom_color_preset.blockSignals(True)
    
    # Keep track of what the value of the presets dropdown was.
    prev_selected_preset_type = self.get_option_value("custom_color_preset")
    
    # Remove everything except "Default" and "Custom".
    for i in reversed(range(self.ui.custom_color_preset.count())):
      if self.ui.custom_color_preset.itemText(i) in ["Default", "Custom"]:
        continue
      self.ui.custom_color_preset.removeItem(i)
    
    # Add the presets specific to this model.
    presets = self.get_color_presets_for_current_model()
    for preset_name in presets:
      if preset_name in ["Default", "Custom"]:
        QMessageBox.warning(self, "Invalid color preset name", "The selected player model has a preset named \"%s\", which is a reserved name. This preset will be ignored." % preset_name)
        continue
      self.ui.custom_color_preset.addItem(preset_name)
    
    # If the new model has a preset with the same name as the selected preset for the previous model, set the dropdown back to that value.
    # This is so switching between hero/casual doesn't reset the preset you have selected, in cases where the same preset is specified for both hero and casual.
    # (This has the side effect of preserving the preset even across entirely different models if they happen to have presets of the same name.)
    if prev_selected_preset_type in presets:
      self.set_option_value("custom_color_preset", prev_selected_preset_type)
    else:
      # Otherwise switch to Default, since the Casual colors get cleared on model switch anyway.
      self.set_option_value("custom_color_preset", "Default")
    
    if reload_colors:
      # Because we blocked signals, we manually reload the color buttons, without generating the preview.
      self.reload_colors(update_preview=False)
    
    self.ui.custom_color_preset.blockSignals(False)
  
  def reload_custom_model(self, update_preview=True):
    self.disable_invalid_cosmetic_options()
    
    while self.ui.custom_colors_layout.count():
      item = self.ui.custom_colors_layout.takeAt(0)
      hlayout = item.layout()
      while hlayout.count():
        item = hlayout.takeAt(0)
        widget = item.widget()
        if widget:
          widget.deleteLater()
    self.custom_color_selector_buttons = OrderedDict()
    self.custom_color_selector_hex_inputs = OrderedDict()
    self.custom_color_reset_buttons = OrderedDict()
    
    custom_model_name = self.get_option_value("custom_player_model")
    metadata = customizer.get_model_metadata(custom_model_name)
    if metadata is None:
      return
    if "error_message" in metadata:
      error_message = "Syntax error when trying to read metadata.txt for custom model: %s\n\n%s" %(custom_model_name, metadata["error_message"])
      print(error_message)
      QMessageBox.critical(
        self, "Failed to load model metadata",
        error_message
      )
    
    model_author = metadata.get("author", None)
    model_comment = metadata.get("comment", None)
    comment_lines = []
    if model_author:
      comment_lines.append("Model author: %s" % model_author)
    if model_comment:
      comment_lines.append("Model author comment: %s" % model_comment)
    self.ui.custom_model_comment.setText("\n".join(comment_lines))
    if len(comment_lines) <= 0:
      self.ui.custom_model_comment.hide()
    else:
      self.ui.custom_model_comment.show()
    
    # Allow customizing the text of the Casual Clothes checkbox.
    casual_clothes_option_text = str(metadata.get("casual_clothes_option_text", "Casual Clothes"))
    if len(casual_clothes_option_text) > 28:
      # 28 character maximum length.
      casual_clothes_option_text = casual_clothes_option_text[:28]
    self.ui.player_in_casual_clothes.setText(casual_clothes_option_text)
    
    is_casual = self.get_option_value("player_in_casual_clothes")
    if is_casual:
      prefix = "casual"
    else:
      prefix = "hero"
    
    self.custom_colors = OrderedDict()
    custom_colors = metadata.get(prefix + "_custom_colors", {})
    
    for custom_color_name, default_color in custom_colors.items():
      option_name = "custom_color_" + custom_color_name
      hlayout = QHBoxLayout()
      label_for_color_selector = QLabel(self.ui.tab_player_customization)
      label_for_color_selector.setText("%s Color" % custom_color_name)
      hlayout.addWidget(label_for_color_selector)
      
      color_hex_code_input = QLineEdit(self.ui.tab_player_customization)
      color_hex_code_input.setText("")
      color_hex_code_input.setObjectName(option_name + "_hex_code_input")
      color_hex_code_input.setFixedWidth(QFontMetrics(QFont()).horizontalAdvance("CCCCCC")+5)
      color_hex_code_input.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
      hlayout.addWidget(color_hex_code_input)
      
      color_randomize_button = QPushButton(self.ui.tab_player_customization)
      color_randomize_button.setText("Random")
      color_randomize_button.setObjectName(option_name + "_randomize_color")
      color_randomize_button.setFixedWidth(QFontMetrics(QFont()).horizontalAdvance("Random")+11)
      hlayout.addWidget(color_randomize_button)
      
      color_selector_button = QPushButton(self.ui.tab_player_customization)
      color_selector_button.setText("Click to set color")
      color_selector_button.setObjectName(option_name)
      hlayout.addWidget(color_selector_button)
      
      color_reset_button = QPushButton(self.ui.tab_player_customization)
      color_reset_button.setText("X")
      color_reset_button.setObjectName(option_name + "_reset_color")
      color_reset_button.setFixedWidth(QFontMetrics(QFont()).horizontalAdvance("X")+11)
      size_policy = color_reset_button.sizePolicy()
      size_policy.setRetainSizeWhenHidden(True)
      color_reset_button.setSizePolicy(size_policy)
      color_reset_button.setVisible(False)
      hlayout.addWidget(color_reset_button)
      
      self.custom_color_selector_buttons[option_name] = color_selector_button
      color_selector_button.clicked.connect(self.open_custom_color_chooser)
      self.custom_color_selector_hex_inputs[option_name] = color_hex_code_input
      color_hex_code_input.textEdited.connect(self.custom_color_hex_code_changed)
      color_hex_code_input.editingFinished.connect(self.custom_color_hex_code_finished_editing)
      color_randomize_button.clicked.connect(self.randomize_one_custom_color)
      color_reset_button.clicked.connect(self.reset_one_custom_color)
      self.custom_color_reset_buttons[option_name] = color_reset_button
      
      self.ui.custom_colors_layout.addLayout(hlayout)
      
      self.set_color(option_name, default_color, update_preview=False, save_color_as_custom=False)
    
    if len(custom_colors) == 0:
      # Need to push the preview over to the right even when there are no colors to do it, so add a spacer.
      hlayout = QHBoxLayout()
      hspacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
      hlayout.addItem(hspacer)
      self.ui.custom_colors_layout.addLayout(hlayout)
    
    self.update_color_presets_list()
    
    if update_preview:
      self.update_model_preview()
    
    # Hide the custom voice disable option for models that don't have custom voice files.
    if custom_model_name == "Random" or custom_model_name == "Random (exclude Link)":
      self.ui.disable_custom_player_voice.show()
    else:
      custom_model_path = os.path.join(CUSTOM_MODELS_PATH, custom_model_name)
      jaiinit_aaf_path = os.path.join(custom_model_path, "sound", "JaiInit.aaf")
      voice_aw_path = os.path.join(custom_model_path, "sound", "voice_0.aw")
      if os.path.isfile(jaiinit_aaf_path) and os.path.isfile(voice_aw_path):
        self.ui.disable_custom_player_voice.show()
      else:
        self.ui.disable_custom_player_voice.hide()
    
    # Hide the custom items disable option for Link, but not any other models (since we don't know which have custom items).
    if custom_model_name == "Link":
      self.ui.disable_custom_player_items.hide()
    else:
      self.ui.disable_custom_player_items.show()
  
  def reload_colors(self, update_preview=True):
    for color_name in self.get_default_custom_colors_for_current_model():
      color = self.get_color(color_name)
      self.set_color("custom_color_" + color_name, color, update_preview=False, save_color_as_custom=False)
    
    if update_preview:
      self.update_model_preview()
  
  def custom_model_changed(self, index):
    self.reload_custom_model()
  
  def in_casual_clothes_changed(self, checked):
    self.reload_custom_model()
  
  def color_preset_changed(self, index):
    self.reload_colors()
  
  def reset_color_selectors_to_model_default_colors(self):
    default_colors = self.get_default_custom_colors_for_current_model()
    
    any_color_changed = False
    for custom_color_name, default_color in default_colors.items():
      if custom_color_name in self.custom_colors and self.custom_colors[custom_color_name] != default_color:
        any_color_changed = True
      option_name = "custom_color_" + custom_color_name
      self.set_color(option_name, default_color, update_preview=False, save_color_as_custom=False)
    
    if any_color_changed:
      self.update_model_preview()
    
    return any_color_changed
  
  def disable_invalid_cosmetic_options(self):
    custom_model_name = self.get_option_value("custom_player_model")
    metadata = customizer.get_model_metadata(custom_model_name)
    
    if metadata is None:
      self.ui.player_in_casual_clothes.setEnabled(True)
      self.set_option_value("player_in_casual_clothes", False)
    else:
      disable_casual_clothes = metadata.get("disable_casual_clothes", False)
      if disable_casual_clothes:
        self.ui.player_in_casual_clothes.setEnabled(False)
        self.ui.player_in_casual_clothes.setChecked(False)
      else:
        self.ui.player_in_casual_clothes.setEnabled(True)
  
  def get_color(self, color_name):
    preset_type = self.get_option_value("custom_color_preset")
    default_colors = self.get_default_custom_colors_for_current_model()
    if preset_type == "Default":
      return default_colors[color_name]
    elif preset_type == "Custom":
      if color_name in self.custom_colors:
        return self.custom_colors[color_name]
      else:
        return default_colors[color_name]
    else:
      color_presets = self.get_color_presets_for_current_model()
      if preset_type not in color_presets:
        print("Could not find color preset \"%s\" in the model's metadata.txt" % preset_type)
        return default_colors[color_name]
      
      preset = color_presets[preset_type]
      if color_name in preset:
        return preset[color_name]
      else:
        return default_colors[color_name]
  
  def set_color(self, 
    option_name, color, update_preview=True,
    save_color_as_custom=True, move_other_non_custom_colors_to_custom=True
  ):
    if isinstance(color, tuple):
      color = list(color)
    if not (isinstance(color, list) and len(color) == 3):
      color = [255, 255, 255]
    
    assert option_name.startswith("custom_color_")
    color_name = option_name[len("custom_color_"):]
    
    color_button = self.custom_color_selector_buttons[option_name]
    hex_input = self.custom_color_selector_hex_inputs[option_name]
    reset_button = self.custom_color_reset_buttons[option_name]
    if color is None:
      color_button.setStyleSheet("")
      hex_input.setText("")
    else:
      hex_input.setText("%02X%02X%02X" % tuple(color))
      
      r, g, b = color
      
      # Depending on the value of the background color of the button, we need to make the text color either black or white for contrast.
      h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
      if v > 0.5:
        text_color = (0, 0, 0)
      else:
        text_color = (255, 255, 255)
      
      color_button.setStyleSheet(
        "background-color: rgb(%d, %d, %d);" % (r, g, b) + \
        "color: rgb(%d, %d, %d);" % text_color,
      )
    
    default_colors = self.get_default_custom_colors_for_current_model()
    default_color = default_colors[color_name]
    if color == default_color:
      reset_button.setVisible(False)
    else:
      reset_button.setVisible(True)
    
    if save_color_as_custom:
      # First, save the color as a custom color.
      self.custom_colors[color_name] = color
      
      if self.get_option_value("custom_color_preset") != "Custom" and move_other_non_custom_colors_to_custom:
        # If the presets dropdown isn't already on Custom, we'll switch to to Custom automatically.
        
        # However, in order to prevent all the other colors besides this one from abruptly switching when we do that, we need to copy all of the currently visible default or preset colors (except this currently changing color) over to custom colors.
        for other_color_name in default_colors:
          if color_name == other_color_name:
            continue
          color = self.get_color(other_color_name)
          other_option_name = "custom_color_" + other_color_name
          self.set_color(other_option_name, color, update_preview=False, save_color_as_custom=True, move_other_non_custom_colors_to_custom=False)
        
        # Then we actually switch the presets dropdown to Custom.
        self.set_option_value("custom_color_preset", "Custom")
    
    if update_preview:
      self.update_model_preview()
  
  def open_custom_color_chooser(self):
    option_name = self.sender().objectName()
    
    assert option_name.startswith("custom_color_")
    color_name = option_name[len("custom_color_"):]
    
    r, g, b = self.get_color(color_name)
    initial_color = QColor(r, g, b, 255)
    color = QColorDialog.getColor(initial_color, self, "Select color")
    if not color.isValid():
      return
    r = color.red()
    g = color.green()
    b = color.blue()
    self.set_color(option_name, [r, g, b])
    self.update_settings()
  
  def custom_color_hex_code_changed(self):
    option_name, color_name = self.get_option_name_and_color_name_from_sender_object_name()
    
    text = self.sender().text().strip().lstrip("#").upper()
    if len(text) != 6 or any(c for c in text if c not in "0123456789ABCDEF"):
      return False
    r = int(text[0:2], 16)
    g = int(text[2:4], 16)
    b = int(text[4:6], 16)
    self.set_color(option_name, [r, g, b])
    self.update_settings()
    return True
  
  def custom_color_hex_code_finished_editing(self):
    is_valid_color = self.custom_color_hex_code_changed()
    if not is_valid_color:
      # If the hex code is invalid reset the text to the correct hex code for the current color.
      option_name, color_name = self.get_option_name_and_color_name_from_sender_object_name()
      self.set_color(option_name, self.get_color(color_name))
  
  def reset_one_custom_color(self):
    option_name, color_name = self.get_option_name_and_color_name_from_sender_object_name()
    
    default_colors = self.get_default_custom_colors_for_current_model()
    default_color = default_colors[color_name]
    
    if self.get_color(color_name) != default_color:
      self.set_color(option_name, default_color)
    
    self.update_settings()
  
  def get_random_h_and_v_shifts_for_custom_color(self, default_color):
    r, g, b = default_color
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h = int(h*360)
    s = int(s*100)
    v = int(v*100)
    
    min_v_shift = -40
    max_v_shift = 40
    if s < 10:
      # For very unsaturated colors, we want to limit the range of value randomization to exclude results that wouldn't change anything anyway.
      # This effectively stops white and black from having a 50% chance to not change at all.
      min_v_shift = max(-40, 0-v)
      max_v_shift = min(40, 100-v)
    
    h_shift = random.randint(0, 359)
    v_shift = random.randint(min_v_shift, max_v_shift)
    
    return (h_shift, v_shift)
  
  def randomize_one_custom_color(self):
    option_name, color_name = self.get_option_name_and_color_name_from_sender_object_name()
    
    default_colors = self.get_default_custom_colors_for_current_model()
    default_color = default_colors[color_name]
    h_shift, v_shift = self.get_random_h_and_v_shifts_for_custom_color(default_color)
    color = texture_utils.hsv_shift_color(default_color, h_shift, v_shift)
    
    self.set_color(option_name, color)
    
    self.update_settings()
  
  def randomize_all_custom_colors_together(self):
    default_colors = self.get_default_custom_colors_for_current_model()
    
    h_shift = random.randint(0, 359)
    v_shift = random.randint(-40, 40)
    for custom_color_name, default_color in default_colors.items():
      color = texture_utils.hsv_shift_color(default_color, h_shift, v_shift)
      
      option_name = "custom_color_" + custom_color_name
      self.set_color(option_name, color, update_preview=False)
    self.update_model_preview()
    
    self.update_settings()
  
  def randomize_all_custom_colors_separately(self):
    default_colors = self.get_default_custom_colors_for_current_model()
    
    for custom_color_name, default_color in default_colors.items():
      h_shift, v_shift = self.get_random_h_and_v_shifts_for_custom_color(default_color)
      color = texture_utils.hsv_shift_color(default_color, h_shift, v_shift)
      
      option_name = "custom_color_" + custom_color_name
      self.set_color(option_name, color, update_preview=False)
    self.update_model_preview()
    
    self.update_settings()
  
  def get_option_name_and_color_name_from_sender_object_name(self):
    object_name = self.sender().objectName()
    
    if object_name.endswith("_hex_code_input"):
      option_name = object_name[:len(object_name)-len("_hex_code_input")]
    elif object_name.endswith("_randomize_color"):
      option_name = object_name[:len(object_name)-len("_randomize_color")]
    elif object_name.endswith("_reset_color"):
      option_name = object_name[:len(object_name)-len("_reset_color")]
    else:
      raise Exception("Invalid custom color sender object name: %s" % object_name)
    
    assert option_name.startswith("custom_color_")
    color_name = option_name[len("custom_color_"):]
    
    return (option_name, color_name)
  
  def get_current_model_metadata_and_prefix(self):
    custom_model_name = self.get_option_value("custom_player_model")
    is_casual = self.get_option_value("player_in_casual_clothes")
    if is_casual:
      prefix = "casual"
    else:
      prefix = "hero"
    
    metadata = customizer.get_model_metadata(custom_model_name)
    if metadata is None:
      return ({}, prefix)
    return (metadata, prefix)
  
  def get_default_custom_colors_for_current_model(self):
    metadata, prefix = self.get_current_model_metadata_and_prefix()
    default_colors = metadata.get(prefix + "_custom_colors", {})
    return default_colors
  
  def get_color_presets_for_current_model(self):
    metadata, prefix = self.get_current_model_metadata_and_prefix()
    color_presets = metadata.get(prefix + "_color_presets", {})
    return color_presets
  
  def update_model_preview(self):
    if self.no_ui_test:
      # Preview can't be seen without a UI anyway, don't waste time generating it.
      return
    
    custom_model_name = self.get_option_value("custom_player_model")
    custom_model_metadata = customizer.get_model_metadata(custom_model_name)
    disable_casual_clothes = custom_model_metadata.get("disable_casual_clothes", False)
    if self.get_option_value("player_in_casual_clothes") and not disable_casual_clothes:
      prefix = "casual"
    else:
      prefix = "hero"
    
    colors = OrderedDict()
    for color_name in self.get_default_custom_colors_for_current_model():
      colors[color_name] = self.get_color(color_name)
    
    try:
      preview_image = customizer.get_model_preview_image(custom_model_name, prefix, colors)
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message = "Failed to load model preview image for model %s.\nError:\n" % (custom_model_name) + str(e) + "\n\n" + stack_trace
      print(error_message)
      QMessageBox.critical(
        self, "Failed to load model preview",
        error_message
      )
      return
    
    if preview_image is None:
      self.ui.custom_model_preview_label.hide()
      return
    
    self.ui.custom_model_preview_label.show()
    
    data = preview_image.tobytes('raw', 'BGRA')
    qimage = QImage(data, preview_image.width, preview_image.height, QImage.Format_ARGB32)
    scaled_pixmap = QPixmap.fromImage(qimage).scaled(225, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    self.ui.custom_model_preview_label.setPixmap(scaled_pixmap)

  def install_custom_model_zip(self):
    try:
      zip_path, selected_filter = QFileDialog.getOpenFileName(self, "Select custom model zip file", CUSTOM_MODELS_PATH, "Zip Files (*.zip)")
      if not zip_path:
        return
      zip = zipfile.ZipFile(zip_path)
      try:
        top_level_dir = zipfile.Path(zip, zip.namelist()[0])
      except IndexError:
        QMessageBox.critical(
          self, "Incorrect archive structure",
          "Archive is empty"
        )
        return
      # Verify contents
      if top_level_dir.joinpath("models").is_dir():
        model_path = top_level_dir.joinpath("models")
        model_dir_list = list(model_path.iterdir())
        is_model_pack = True
      else:
        model_dir_list = [top_level_dir]
        is_model_pack = False
      expected_files = ["Link.arc", "metadata.txt"]
      for model_dir in model_dir_list:
        for f in expected_files:
          if not model_dir.joinpath(f).exists():
            QMessageBox.critical(
              self, "Incorrect archive structure",
              "Missing file: %s" % model_dir.joinpath(f).at
            )
            return
      zip.extractall(CUSTOM_MODELS_PATH)
      if not is_model_pack:
        install_result = model_dir_list[0].name
      else:
        for model_dir in model_dir_list:
          shutil.move(os.path.join(CUSTOM_MODELS_PATH, model_dir.at), os.path.join(CUSTOM_MODELS_PATH, model_dir.name))
        shutil.rmtree(os.path.join(CUSTOM_MODELS_PATH, top_level_dir.name))
        install_result = "%s models" % len(model_dir_list)
      QMessageBox.information(
        self, "Installation complete",
        "%s installed successfully" % install_result
      )
      self.update_custom_player_model_list()
      self.set_option_value("custom_player_model", model_dir_list[0].name)
    except zipfile.BadZipfile:
      stack_trace = traceback.format_exc()
      print(stack_trace)
      QMessageBox.critical(
        self, "Failed to unpack model archive",
        stack_trace
      )

  def open_about(self):
    text = """WWR Random Settings Version %s<br><br>
      Created by LagoLunatic, Random Settings changes by tanjo3<br><br>
      Report issues here:<br><a href=\"https://github.com/tanjo3/wwrando/issues\">https://github.com/tanjo3/wwrando/issues</a><br><br>
      Source code:<br><a href=\"https://github.com/tanjo3/wwrando/tree/random-settings\">https://github.com/tanjo3/wwrando/tree/random-settings</a>""" % VERSION_WITHOUT_COMMIT
    
    self.about_dialog = QMessageBox()
    self.about_dialog.setTextFormat(Qt.TextFormat.RichText)
    self.about_dialog.setWindowTitle("WWR Random Settings")
    self.about_dialog.setText(text)
    self.about_dialog.setWindowIcon(self.windowIcon())
    self.about_dialog.show()
  
  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.close()
  
  def closeEvent(self, event):
    event.accept()

class RandomizerProgressDialog(QProgressDialog):
  def __init__(self, title, description, max_val):
    QProgressDialog.__init__(self)
    self.setWindowTitle(title)
    self.setLabelText(description)
    self.setMaximum(max_val)
    self.setWindowModality(Qt.ApplicationModal)
    self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)
    self.setFixedSize(self.size())
    self.setAutoReset(False)
    self.setCancelButton(None)
    self.show()

class RandomizerThread(QThread):
  update_progress = Signal(str, int)
  randomization_complete = Signal()
  randomization_failed = Signal(str)
  
  def __init__(self, randomizer, profiling=False):
    QThread.__init__(self)
    
    self.randomizer = randomizer
    self.profiling = profiling
  
  def run(self):
    if self.profiling:
      import cProfile, pstats
      profiler = cProfile.Profile()
      profiler.enable()
    
    try:
      randomizer_generator = self.randomizer.randomize()
      last_update_time = time.time()
      while True:
        # Need to use a while loop to go through the generator instead of a for loop, as a for loop would silently exit if a StopIteration error ever happened for any reason.
        next_option_description, options_finished = next(randomizer_generator)
        if options_finished == -1:
          break
        if time.time()-last_update_time < 0.1:
          # Limit how frequently the signal is emitted to 10 times per second.
          # Extremely frequent updates (e.g. 1000 times per second) can cause the program to crash with no error message.
          continue
        self.update_progress.emit(next_option_description, options_finished)
        last_update_time = time.time()
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message = "Randomization failed with error:\n" + str(e) + "\n\n" + stack_trace
      self.randomization_failed.emit(error_message)
      return
    
    if self.profiling:
      profiler.disable()
      with open("profileresults.txt", "w") as f:
        ps = pstats.Stats(profiler, stream=f).sort_stats("cumulative")
        ps.print_stats()
    
    self.randomization_complete.emit()

class UpdateCheckerThread(QThread):
  finished_checking_for_updates = Signal(str)
  
  def run(self):
    new_version = check_for_updates()
    self.finished_checking_for_updates.emit(new_version)

# Allow yaml to load and dump OrderedDicts.
yaml.SafeLoader.add_constructor(
  yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
  lambda loader, node: OrderedDict(loader.construct_pairs(node))
)
yaml.Dumper.add_representer(
  OrderedDict,
  lambda dumper, data: dumper.represent_dict(data.items())
)
