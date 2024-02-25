from dataclasses import fields
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from wwr_ui.uic.ui_randomizer_window import Ui_MainWindow
from wwr_ui.update_checker import check_for_updates, LATEST_RELEASE_DOWNLOAD_PAGE_URL
from wwr_ui.inventory import INVENTORY_ITEMS, DEFAULT_STARTING_ITEMS, DEFAULT_RANDOMIZED_ITEMS

import os
import yaml
import traceback
from enum import StrEnum
from collections import Counter
from dataclasses import fields

from options.wwrando_options import EntranceMixMode, Options, SwordMode, TrickDifficulty
from randomizer import WWRandomizer, TooFewProgressionLocationsError, InvalidCleanISOError, PermalinkWrongVersionError, PermalinkWrongCommitError
from version import VERSION
from wwrando_paths import SETTINGS_PATH, ASSETS_PATH, IS_RUNNING_FROM_SOURCE
from seedgen import seedgen
from logic.logic import Logic

from typing import TYPE_CHECKING, Type
import typing

class WWRandomizerWindow(QMainWindow):
  def __init__(self, cmd_line_args):
    super(WWRandomizerWindow, self).__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    
    # Fix text not becoming grey when a widget is disabled in newer versions of PySide6.
    self.setStyleSheet("*:disabled { color: grey; }")
    
    self.ui.tab_player_customization.initialize_from_rando_window(self)
    
    self.randomizer_thread = None
    
    self.cmd_line_args = cmd_line_args
    self.profiling = self.cmd_line_args.profile
    self.auto_seed = self.cmd_line_args.autoseed
    
    # We use an Options instance to represent the defaults instead of directly accessing each options default so that
    # default_factory works correctly.
    self.default_options = Options()
    
    self.initialize_option_widgets()
    
    # Set the default custom_colors dict after initializing the widgets just to be safe.
    # We want to be sure the selected model and preset are the default.
    self.default_options.custom_colors = self.ui.tab_player_customization.get_all_colors()
    
    self.load_settings()
    
    self.cached_item_locations = Logic.load_and_parse_item_locations()
    
    self.ui.clean_iso_path.editingFinished.connect(self.update_settings)
    self.ui.output_folder.editingFinished.connect(self.update_settings)
    self.ui.plando_file.editingFinished.connect(self.update_settings)
    self.ui.clean_iso_path_browse_button.clicked.connect(self.browse_for_clean_iso)
    self.ui.output_folder_browse_button.clicked.connect(self.browse_for_output_folder)
    self.ui.plando_file_browse_button.clicked.connect(self.browse_for_plando_file)
    
    self.ui.label_for_clean_iso_path.linkActivated.connect(self.show_clean_iso_explanation)
    
    for option in Options.all:
      if option.name == "custom_colors":
        continue
      widget = self.findChild(QWidget, option.name)
      label_for_option = self.findChild(QLabel, "label_for_" + option.name)
      
      # Connect signals to detect when the user changes each option.
      if isinstance(widget, QAbstractButton):
        widget.clicked.connect(self.update_settings)
      elif isinstance(widget, QComboBox):
        widget.currentIndexChanged.connect(self.update_settings)
        if option.choice_descriptions:
          widget.highlighted.connect(self.update_choice_highlighted_description)
      elif isinstance(widget, QListView):
        pass
      elif isinstance(widget, QSpinBox):
        widget.valueChanged.connect(self.update_settings)
    
    self.ui.randomize_button.clicked.connect(self.randomize)
    
    self.set_option_description(None)
    
    self.update_settings()
    
    self.setWindowTitle("AP The Wind Waker Randomizer Client %s" % VERSION)
    
    icon_path = os.path.join(ASSETS_PATH, "icon.ico")
    self.setWindowIcon(QIcon(icon_path))
    
    self.show()
  
  def append_row(self, model: QAbstractListModel, value):
    model.insertRow(model.rowCount())
    newrow = model.index(model.rowCount() - 1, 0)
    model.setData(newrow, value)
  
  def move_selected_rows(self, source: QListView, dest: QListView):
    selection = source.selectionModel().selectedIndexes()
    # Remove starting from the last so the previous indices remain valid
    selection.sort(reverse = True, key = lambda x: x.row())
    for item in selection:
      value = item.data()
      source.model().removeRow(item.row())
      self.append_row(dest.model(), value)
  
  def append_row(self, model: QAbstractListModel, value):
    model.insertRow(model.rowCount())
    newrow = model.index(model.rowCount() - 1, 0)
    model.setData(newrow, value)
  
  def move_selected_rows(self, source: QListView, dest: QListView):
    selection = source.selectionModel().selectedIndexes()
    # Remove starting from the last so the previous indices remain valid
    selection.sort(reverse = True, key = lambda x: x.row())
    for item in selection:
      value = item.data()
      source.model().removeRow(item.row())
      self.append_row(dest.model(), value)
  
  def randomize(self):
    clean_iso_path = self.settings["clean_iso_path"].strip()
    output_folder = self.settings["output_folder"].strip()
    plando_file = self.settings["plando_file"].strip()
    self.settings["clean_iso_path"] = clean_iso_path
    self.settings["output_folder"] = output_folder
    self.settings["plando_file"] = plando_file
    self.ui.clean_iso_path.setText(clean_iso_path)
    self.ui.output_folder.setText(output_folder)
    self.ui.plando_file.setText(plando_file)
    
    if not os.path.isfile(clean_iso_path):
      QMessageBox.warning(self, "Vanilla ISO path not specified", "Must specify path to your vanilla Wind Waker ISO (North American version).")
      return
    if not os.path.isdir(output_folder):
      QMessageBox.warning(self, "No output folder specified", "Must specify a valid output folder for the randomized files.")
      return
    if not os.path.isfile(plando_file):
      QMessageBox.warning(self, "No AP plando file specified", "Must specify a valid AP plando file.")
      return
    
    options = self.get_all_options_from_widget_values()

    seed, locations_map, entrances_map = self.read_ap_plando_file(plando_file, options)
    
    options.custom_colors = self.ui.tab_player_customization.get_all_colors()
    
    self.progress_dialog = RandomizerProgressDialog(self, "Randomizing", "Initializing...")
    
    try:
      rando = WWRandomizer(seed, clean_iso_path, output_folder, options, locations_map, entrances_map, cmd_line_args=self.cmd_line_args)
    except (TooFewProgressionLocationsError, InvalidCleanISOError) as e:
      error_message = str(e)
      self.randomization_failed(error_message)
      return
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message = "Randomization failed with error:\n" + str(e) + "\n\n" + stack_trace
      self.randomization_failed(error_message)
      return
    
    self.progress_dialog.setMaximum(rando.get_max_progress_length())
    self.randomizer_thread = RandomizerThread(rando, profiling=self.profiling)
    self.randomizer_thread.update_progress.connect(self.update_progress_dialog)
    self.randomizer_thread.randomization_complete.connect(self.randomization_complete)
    self.randomizer_thread.randomization_failed.connect(self.randomization_failed)
    self.randomizer_thread.start()
  
  def update_progress_dialog(self, next_option_description, progress_completed):
    if progress_completed > self.progress_dialog.maximum():
      # This shouldn't happen if the max estimate was correct, but if it did just snap the progress bar to the end.
      # Without this, the progress going past the max would cause the bar to get stuck at the last valid position.
      progress_completed = self.progress_dialog.maximum()
    self.progress_dialog.setLabelText(next_option_description)
    self.progress_dialog.setValue(progress_completed)
  
  def randomization_complete(self):
    self.progress_dialog.reset()
    
    text = """Randomization complete.<br><br>
      If you get stuck, check the Archipelago spoiler log for your room."""
    if self.randomizer_thread.randomizer.dry_run:
      text = """Randomization complete.<br><br>
      Note: You chose to do a dry run, meaning <u>no playable ISO was generated</u>.<br>
      To actually play the randomizer, uncheck the Dry Run checkbox in the Advanced Options tab, then click Randomize again."""
    
    self.randomizer_thread = None
    
    self.complete_dialog = QMessageBox()
    self.complete_dialog.setTextFormat(Qt.TextFormat.RichText)
    self.complete_dialog.setWindowTitle("Randomization complete")
    self.complete_dialog.setText(text)
    self.complete_dialog.setWindowIcon(self.windowIcon())
    self.complete_dialog.show()
  
  def randomization_failed(self, error_message):
    self.progress_dialog.reset()
    
    if self.randomizer_thread is not None:
      self.randomizer_thread.terminate()
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
  
  def initialize_option_widgets(self):
    for option in Options.all:
      if option.name == "custom_colors":
        continue
      widget = self.findChild(QWidget, option.name)
      if isinstance(widget, QAbstractButton):
        assert issubclass(option.type, bool)
      elif isinstance(widget, QComboBox):
        assert issubclass(option.type, str)
        if widget.objectName() not in ["custom_player_model", "custom_color_preset"]:
          assert issubclass(option.type, StrEnum)
          assert widget.count() == len(option.type)
          for i, enum_value in enumerate(option.type):
            # Make sure the text of each choice in the combobox matches the string enum value of the option.
            widget.setItemText(i, enum_value.value)
      elif isinstance(widget, QListView):
        assert issubclass(typing.get_origin(option.type) or option.type, list)
      elif isinstance(widget, QSpinBox):
        assert issubclass(option.type, int)
        widget.setMinimum(option.minimum)
        widget.setMaximum(option.maximum)
      
      # Make sure the initial values of all the GUI widgets match the defaults for the options.
      default_value = self.default_options[option.name]
      self.set_option_value(option.name, default_value)
  
  def load_settings(self):
    if os.path.isfile(SETTINGS_PATH):
      try:
        with open(SETTINGS_PATH) as f:
          self.settings = yaml.safe_load(f)
      except yaml.error.YAMLError as e:
        QMessageBox.critical(
          self, "Invalid settings.txt",
          "Failed to load settings from settings.txt.\n\n"
          "Remove the corrupted settings.txt before trying to load the randomizer again.\n"
        )
        self.close()
        return
      if self.settings is None:
        self.settings = {}
    else:
      self.settings = {}
    
    if "clean_iso_path" in self.settings:
      self.ui.clean_iso_path.setText(self.settings["clean_iso_path"])
    if "output_folder" in self.settings:
      self.ui.output_folder.setText(self.settings["output_folder"])
    if "plando_file" in self.settings:
      self.ui.plando_file.setText(self.settings["plando_file"])
    
    for option in Options.all:
      if option.name in self.settings:
        if option.name in ["custom_color_preset", "custom_colors"]:
          # Colors and color presents not loaded yet, handle this later
          continue
        self.set_option_value(option.name, self.settings[option.name])
    
    self.ui.tab_player_customization.load_custom_colors_from_settings()
  
  def save_settings(self):
    with open(SETTINGS_PATH, "w") as f:
      yaml.dump(self.settings, f, default_flow_style=False, sort_keys=False)
  
  def update_settings(self):
    self.settings["clean_iso_path"] = self.ui.clean_iso_path.text()
    self.settings["output_folder"] = self.ui.output_folder.text()
    self.settings["plando_file"] = self.ui.plando_file.text()
    
    self.ui.tab_player_customization.disable_invalid_cosmetic_options()
    
    for option in Options.all:
      self.settings[option.name] = self.get_option_value(option.name)
    
    self.save_settings()
  
  def show_clean_iso_explanation(self):
    QMessageBox.information(
      self, "Vanilla Wind Waker ISO",
      "To use the randomizer, you need to have a copy of the North American GameCube version of The Legend of Zelda: The Wind Waker.\n\n" +
      "The European and Japanese versions of Wind Waker are not supported.\nWind Waker HD is also not supported.\n\n" +
      "The ISO should ideally be a vanilla/unmodified copy of the game to guarantee the randomizer works with no " +
      "conflicts, but Wind Waker mods that do not conflict with the randomizer can also be used."
    )
  
  def browse_for_clean_iso(self):
    if self.settings["clean_iso_path"] and os.path.isfile(self.settings["clean_iso_path"]):
      default_dir = os.path.dirname(self.settings["clean_iso_path"])
    else:
      default_dir = None
    
    clean_iso_path, selected_filter = QFileDialog.getOpenFileName(self, "Select vanilla Wind Waker ISO", default_dir, "GC ISO Files (*.iso *.gcm)")
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

  def browse_for_plando_file(self):
    if self.settings["plando_file"] and os.path.isfile(self.settings["plando_file"]):
      default_dir = os.path.dirname(self.settings["plando_file"])
    else:
      default_dir = None
    
    plando_file, selected_filter = QFileDialog.getOpenFileName(self, "Select APTWW file", default_dir, "APTWW File (*.aptww)")
    if not plando_file:
      return
    self.ui.plando_file.setText(plando_file)
    self.update_settings()
  
  def get_option_from_widget(self, widget: QObject):
    option_name = widget.objectName().removeprefix("label_for_")
    if option_name in Options.by_name:
      return Options.by_name[option_name]
    else:
      return None
  
  def eventFilter(self, target: QObject, event: QEvent):
    if event.type() == QEvent.Type.Enter:
      option = self.get_option_from_widget(target)
      if option:
        self.set_option_description(option.description)
      else:
        self.set_option_description(None)
      return True
    elif event.type() == QEvent.Type.Leave:
      self.set_option_description(None)
      return True
    
    return QMainWindow.eventFilter(self, target, event)
  
  def update_choice_highlighted_description(self, index):
    option = self.get_option_from_widget(self.sender())
    assert option
    assert issubclass(option.type, StrEnum)
    enum_values = [val for val in option.type]
    highlighted_value = enum_values[index]
    
    if highlighted_value in option.choice_descriptions:
      desc = option.choice_descriptions[highlighted_value]
    else:
      desc = None
    
    self.set_option_description(desc)
  
  def get_option_value(self, option_name):
    if option_name == "custom_colors":
      return self.ui.tab_player_customization.get_all_colors()
    
    widget = self.findChild(QWidget, option_name)
    option = Options.by_name[option_name]
    if isinstance(widget, QCheckBox) or isinstance(widget, QRadioButton):
      return widget.isChecked()
    elif isinstance(widget, QComboBox):
      if issubclass(option.type, StrEnum):
        index = widget.currentIndex()
        enum_values = [val for val in option.type]
        curr_value = enum_values[index]
        return curr_value
      elif issubclass(option.type, str):
        return widget.itemText(widget.currentIndex())
      else:
        print(f"Invalid type for combobox option: {option.type}")
    elif isinstance(widget, QSpinBox):
      return widget.value()
    elif isinstance(widget, QListView):
      if widget.model() is None:
        return []
      model = widget.model()
      if isinstance(model, ModelFilterOut):
        model = model.sourceModel()
      model.sort(0)
      return [model.data(model.index(i)) for i in range(model.rowCount())]
    
    return None
  
  def set_option_value(self, option_name, new_value):
    if option_name == "custom_colors":
      print("Setting custom_colors via set_option_value not supported")
      return
    
    widget = self.findChild(QWidget, option_name)
    option = Options.by_name[option_name]
    if isinstance(widget, QCheckBox) or isinstance(widget, QRadioButton):
      widget.setChecked(bool(new_value))
    elif isinstance(widget, QComboBox):
      index_of_value = None
      if issubclass(option.type, StrEnum) and isinstance(new_value, option.type):
        enum_values = [val for val in option.type]
        index_of_value = enum_values.index(new_value)
      elif isinstance(new_value, str):
        index_of_value = None
        for i in range(widget.count()):
          text = widget.itemText(i)
          if text == new_value:
            index_of_value = i
            break
      else:
        print(f"Invalid type for combobox option: {option.type}")
      
      if index_of_value is None or index_of_value >= widget.count() or index_of_value < 0:
        print("Cannot find value %s in combobox %s" % (new_value, option_name))
        index_of_value = 0
      
      widget.setCurrentIndex(index_of_value)
    elif isinstance(widget, QSpinBox):
      new_value = int(new_value)
      if new_value < widget.minimum() or new_value > widget.maximum():
        print("Value %s out of range for spinbox %s" % (new_value, option_name))
        new_value = self.default_options[option_name] # reset to default in case 0 is not default or in normal range

      widget.setValue(new_value)
    elif isinstance(widget, QListView):
      if not isinstance(new_value, list):
        new_value = self.default_options[option_name]
      
      if widget.model() is not None:
        model = widget.model()
        if isinstance(model, QSortFilterProxyModel):
          model = model.sourceModel()
        model.setStringList(new_value)
        model.sort(0)
  
  def set_option_description(self, new_description):
    if new_description is None:
      self.ui.option_description.setText("(Hover over an option to see a description of what it does.)")
      self.ui.option_description.setStyleSheet("color: grey;")
    else:
      self.ui.option_description.setText(new_description)
      self.ui.option_description.setStyleSheet("")
  
  def get_all_options_from_widget_values(self):
    options_dict = {}
    for option in Options.all:
      options_dict[option.name] = self.get_option_value(option.name)
    options = Options(**options_dict)
    return options
  
  def read_ap_plando_file(self, plando_file, options):
    with open(os.path.join(plando_file), "r") as f:
      plando_file = yaml.safe_load(f)
    
    seed = f"{plando_file["Seed"]}AP{plando_file["Slot"]}"
    
    for field in fields(options):
      if field.name in plando_file["Options"]:
        value = plando_file["Options"][field.name]

        if field.type is int:
          setattr(options, field.name, value)
        elif field.type is bool:
          setattr(options, field.name, bool(value))
        elif field.type is SwordMode:
          match value:
            case 0: setattr(options, field.name, SwordMode.START_WITH_SWORD)
            case 1: setattr(options, field.name, SwordMode.NO_STARTING_SWORD)
            case 2: setattr(options, field.name, SwordMode.SWORDLESS)
        elif field.type is EntranceMixMode:
            match value:
              case 0: setattr(options, field.name, EntranceMixMode.SEPARATE_DUNGEONS)
              case 1: setattr(options, field.name, EntranceMixMode.MIX_DUNGEONS)
        elif field.type is TrickDifficulty:
            match value:
              case 0: setattr(options, field.name, TrickDifficulty.NONE)
              case 1: setattr(options, field.name, TrickDifficulty.NORMAL)
              case 2: setattr(options, field.name, TrickDifficulty.HARD)
              case 3: setattr(options, field.name, TrickDifficulty.VERY_HARD)
        else:
          print(f"Bad option: {field.name} = {value}")
      else:
        if field.name in ["randomized_gear", "starting_gear"]:
          setattr(options, field.name, field.default_factory())
        if getattr(options, field.name) is None:
          setattr(options, field.name, field.default)
    
    return seed, plando_file["Locations"], plando_file["Entrances"]
  
  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.close()
  
  def closeEvent(self, event):
    if self.randomizer_thread is not None:
      self.randomizer_thread.terminate()
    event.accept()
  
  if TYPE_CHECKING:
    # Fake override for type checker because PySide6 doesn't use TypeVar.
    def findChild[T](self, type: Type[T], name: str = ..., options: Qt.FindChildOption = ...) -> T: ...

class ModelFilterOut(QSortFilterProxyModel):
  def __init__(self):
    super(ModelFilterOut, self).__init__()
    self.filter_strings = []
  
  def setFilterStrings(self, fstr):
    self.filter_strings = fstr
    self.invalidateFilter()
  
  def filterAcceptsRow(self, sourceRow, sourceParent):
    index0 = self.sourceModel().index(sourceRow, 0, sourceParent)
    data = self.sourceModel().data(index0)
    num_occurrences = self.filter_strings.count(data)
    for i in range(sourceRow):
      cur_index = self.sourceModel().index(i, 0, sourceParent)
      cur_data = self.sourceModel().data(cur_index)
      if cur_data == data:
        num_occurrences -= 1
    return num_occurrences <= 0

class RandomizerProgressDialog(QProgressDialog):
  def __init__(self, rando_window: WWRandomizerWindow, title, description):
    QProgressDialog.__init__(self)
    self.rando_window = rando_window
    self.setWindowTitle(title)
    self.setLabelText(description)
    self.setWindowModality(Qt.ApplicationModal)
    self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)
    self.setFixedSize(self.size())
    self.setAutoReset(False)
    self.setCancelButton(None) # Disable cancellation via cancel button.
    self.show()
  
  def keyPressEvent(self, e: QKeyEvent):
    # Disable cancellation via escape key.
    if e.key() == Qt.Key.Key_Escape:
      e.ignore()
  
  def closeEvent(self, e: QCloseEvent):
    # Although we could disable cancellation via Alt+F4, this would not be good design as it would
    # prevent the user from escaping from a randomization that got stuck in a loop somehow.
    # Instead, we reroute the Alt+F4 press to close the entire randomizer window instead of just the
    # progress bar. The window will forcibly kill the randomization attempt before it closes.
    self.rando_window.close()

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
      for next_option_description, progress_completed in self.randomizer.randomize():
        self.update_progress.emit(next_option_description, progress_completed)
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

# Allows PyYAML to dump StrEnums as strings.
yaml.Dumper.add_multi_representer(
  StrEnum,
  lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', str(data.value))
)
