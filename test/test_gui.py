
import threading
from types import SimpleNamespace

import pytest

from wwrando import make_argparser
from wwr_ui import randomizer_window
from wwr_ui.randomizer_window import WWRandomizerWindow
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMessageBox

def make_rando_window() -> WWRandomizerWindow:
  args = make_argparser().parse_args(args=[])
  window = WWRandomizerWindow(cmd_line_args=args)
  return window

def test_gui_launches(qtbot):
  window = make_rando_window()
  window.save_settings()

def test_cosmetic_tab(qtbot):
  window = make_rando_window()
  cosmetic_tab = window.ui.tab_player_customization
  cosmetic_tab.ui.custom_player_model.setCurrentIndex(cosmetic_tab.ui.custom_player_model.findText("Link"))
  cosmetic_tab.ui.randomize_all_custom_colors_separately.click()
  cosmetic_tab.ui.randomize_all_custom_colors_together.click()
  cosmetic_tab.ui.custom_color_preset.setCurrentIndex(cosmetic_tab.ui.custom_color_preset.findText("Dark Link"))

def test_invalid_aptww_file_is_reported_as_rich_text(qtbot, tmp_path, monkeypatch):
  window = make_rando_window()
  qtbot.addWidget(window)
  clean_iso = tmp_path / "clean.iso"
  clean_iso.write_bytes(b"")
  plando_file = tmp_path / "file.aptww"
  plando_file.write_bytes(b"not an aptww file")
  window.settings["clean_iso_path"] = str(clean_iso)
  window.settings["output_folder"] = str(tmp_path)
  window.settings["plando_file"] = str(plando_file)
  
  shown_dialogs = []  
  monkeypatch.setattr(QMessageBox, "exec_", lambda dialog: shown_dialogs.append((dialog.textFormat(), dialog.text())))
  
  # The plain text dialog would otherwise wait forever for someone to close it.
  monkeypatch.setattr(QMessageBox, "critical", lambda parent, title, text: shown_dialogs.append((Qt.TextFormat.PlainText, text)))
  
  window.randomize()
  assert len(shown_dialogs) == 1
  text_format, message = shown_dialogs[0]
  assert text_format == Qt.TextFormat.RichText
  assert "modified or corrupted" in message

def make_released_window(qtbot, monkeypatch, update_check_result) -> WWRandomizerWindow:
  monkeypatch.setattr(randomizer_window, "IS_RUNNING_FROM_SOURCE", False)
  monkeypatch.setattr(randomizer_window, "check_for_updates", lambda: update_check_result)
  window = make_rando_window()
  qtbot.addWidget(window)
  label = window.ui.update_checker_label
  qtbot.waitUntil(lambda: label.text() != "Checking for updates to the randomizer...")
  window.update_checker_thread.wait()
  return window

@pytest.mark.parametrize("update_check_result, expected_text", [
  (None, "No new updates to the randomizer are available."),
  ("error", "There was an error checking for updates."),
], ids=["up to date", "error"])
def test_released_build_reports_the_update_check(qtbot, monkeypatch, update_check_result, expected_text):
  window = make_released_window(qtbot, monkeypatch, update_check_result)
  assert window.ui.update_checker_label.text() == expected_text

def test_released_build_links_to_a_new_version(qtbot, monkeypatch):
  window = make_released_window(qtbot, monkeypatch, "2.7.0")
  label = window.ui.update_checker_label
  assert "Version 2.7.0" in label.text()
  assert 'href="https://github.com/tanjo3/wwrando/releases?q=tag%3Aap_2"' in label.text()
  assert "APWorld" in label.text()
  assert label.openExternalLinks()

def test_released_build_waits_for_a_running_update_check_before_closing(qtbot, monkeypatch):
  check_may_finish = threading.Event()
  monkeypatch.setattr(randomizer_window, "IS_RUNNING_FROM_SOURCE", False)
  monkeypatch.setattr(randomizer_window, "check_for_updates", lambda: check_may_finish.wait(10) and None)
  window = make_rando_window()
  qtbot.addWidget(window)
  thread = window.update_checker_thread
  assert thread.isRunning()
  
  threading.Timer(0.2, check_may_finish.set).start()
  closed = window.close()
  finished_when_closed = thread.isFinished()
  
  thread.wait()
  assert closed
  assert finished_when_closed

def test_source_build_skips_the_update_check(qtbot, monkeypatch):
  monkeypatch.setattr(randomizer_window, "IS_RUNNING_FROM_SOURCE", True)
  window = make_rando_window()
  qtbot.addWidget(window)
  assert not hasattr(window, "update_checker_thread")
  assert "skipping" in window.ui.update_checker_label.text()
  assert window.close()

def fail_randomization_in_thread(window: WWRandomizerWindow, monkeypatch, write_error_log) -> list:
  shown_errors = []
  monkeypatch.setattr(QMessageBox, "critical", lambda parent, title, text: shown_errors.append(text))
  window.progress_dialog = SimpleNamespace(reset=lambda: None)
  window.randomizer_thread = SimpleNamespace(terminate=lambda: None, randomizer=SimpleNamespace(write_error_log=write_error_log))
  window.randomization_failed("Some error")
  return shown_errors

def test_failed_randomization_writes_an_error_log(qtbot, monkeypatch):
  window = make_rando_window()
  qtbot.addWidget(window)
  logged_errors = []
  shown_errors = fail_randomization_in_thread(window, monkeypatch, logged_errors.append)
  assert logged_errors == ["Some error"]
  assert shown_errors == ["Some error"]

def test_error_is_still_shown_when_the_error_log_cannot_be_written(qtbot, monkeypatch):
  def fail_to_write(error_message):
    raise OSError("disk full")
  
  window = make_rando_window()
  qtbot.addWidget(window)
  assert fail_randomization_in_thread(window, monkeypatch, fail_to_write) == ["Some error"]

def test_about_dialog_links_to_the_setup_guide_and_shows_the_version(qtbot, monkeypatch):
  window = make_rando_window()
  qtbot.addWidget(window)
  monkeypatch.setattr(QMessageBox, "show", lambda dialog: None)
  window.open_about()
  text = window.about_dialog.text()
  assert 'href="https://archipelago.gg/tutorial/The%20Wind%20Waker/setup_en"' in text
  assert randomizer_window.VERSION in text
