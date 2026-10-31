
from wwrando import make_argparser
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
