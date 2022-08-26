# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'randomizer_window.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QTabWidget, QTextBrowser,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(950, 700)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 932, 590))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tabWidget = QTabWidget(self.scrollAreaWidgetContents)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.tab_randomizer_settings = QWidget()
        self.tab_randomizer_settings.setObjectName(u"tab_randomizer_settings")
        self.verticalLayout_3 = QVBoxLayout(self.tab_randomizer_settings)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.random_settings_explanation = QTextBrowser(self.tab_randomizer_settings)
        self.random_settings_explanation.setObjectName(u"random_settings_explanation")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.random_settings_explanation.sizePolicy().hasHeightForWidth())
        self.random_settings_explanation.setSizePolicy(sizePolicy)
        self.random_settings_explanation.setFrameShape(QFrame.NoFrame)
        self.random_settings_explanation.setOpenExternalLinks(True)

        self.verticalLayout_3.addWidget(self.random_settings_explanation)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.seed = QLineEdit(self.tab_randomizer_settings)
        self.seed.setObjectName(u"seed")

        self.gridLayout_5.addWidget(self.seed, 2, 1, 1, 1)

        self.label_for_output_folder = QLabel(self.tab_randomizer_settings)
        self.label_for_output_folder.setObjectName(u"label_for_output_folder")

        self.gridLayout_5.addWidget(self.label_for_output_folder, 1, 0, 1, 1)

        self.label_for_seed = QLabel(self.tab_randomizer_settings)
        self.label_for_seed.setObjectName(u"label_for_seed")

        self.gridLayout_5.addWidget(self.label_for_seed, 2, 0, 1, 1)

        self.generate_seed_button = QPushButton(self.tab_randomizer_settings)
        self.generate_seed_button.setObjectName(u"generate_seed_button")

        self.gridLayout_5.addWidget(self.generate_seed_button, 2, 2, 1, 1)

        self.output_folder_browse_button = QPushButton(self.tab_randomizer_settings)
        self.output_folder_browse_button.setObjectName(u"output_folder_browse_button")

        self.gridLayout_5.addWidget(self.output_folder_browse_button, 1, 2, 1, 1)

        self.clean_iso_path = QLineEdit(self.tab_randomizer_settings)
        self.clean_iso_path.setObjectName(u"clean_iso_path")

        self.gridLayout_5.addWidget(self.clean_iso_path, 0, 1, 1, 1)

        self.output_folder = QLineEdit(self.tab_randomizer_settings)
        self.output_folder.setObjectName(u"output_folder")

        self.gridLayout_5.addWidget(self.output_folder, 1, 1, 1, 1)

        self.clean_iso_path_browse_button = QPushButton(self.tab_randomizer_settings)
        self.clean_iso_path_browse_button.setObjectName(u"clean_iso_path_browse_button")

        self.gridLayout_5.addWidget(self.clean_iso_path_browse_button, 0, 2, 1, 1)

        self.label_for_clean_iso_path = QLabel(self.tab_randomizer_settings)
        self.label_for_clean_iso_path.setObjectName(u"label_for_clean_iso_path")

        self.gridLayout_5.addWidget(self.label_for_clean_iso_path, 0, 0, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_5)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.groupBox = QGroupBox(self.tab_randomizer_settings)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_6 = QGridLayout(self.groupBox)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.invert_sea_compass_x_axis = QCheckBox(self.groupBox)
        self.invert_sea_compass_x_axis.setObjectName(u"invert_sea_compass_x_axis")

        self.gridLayout_6.addWidget(self.invert_sea_compass_x_axis, 1, 1, 1, 1)

        self.remove_title_and_ending_videos = QCheckBox(self.groupBox)
        self.remove_title_and_ending_videos.setObjectName(u"remove_title_and_ending_videos")
        self.remove_title_and_ending_videos.setChecked(True)

        self.gridLayout_6.addWidget(self.remove_title_and_ending_videos, 1, 2, 1, 1)

        self.randomize_enemy_palettes = QCheckBox(self.groupBox)
        self.randomize_enemy_palettes.setObjectName(u"randomize_enemy_palettes")

        self.gridLayout_6.addWidget(self.randomize_enemy_palettes, 1, 3, 1, 1)

        self.invert_camera_x_axis = QCheckBox(self.groupBox)
        self.invert_camera_x_axis.setObjectName(u"invert_camera_x_axis")

        self.gridLayout_6.addWidget(self.invert_camera_x_axis, 1, 0, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.tab_randomizer_settings, "")
        self.tab_player_customization = QWidget()
        self.tab_player_customization.setObjectName(u"tab_player_customization")
        self.verticalLayout_4 = QVBoxLayout(self.tab_player_customization)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_for_custom_color_preset = QLabel(self.tab_player_customization)
        self.label_for_custom_color_preset.setObjectName(u"label_for_custom_color_preset")

        self.horizontalLayout.addWidget(self.label_for_custom_color_preset)

        self.custom_color_preset = QComboBox(self.tab_player_customization)
        self.custom_color_preset.setObjectName(u"custom_color_preset")

        self.horizontalLayout.addWidget(self.custom_color_preset)


        self.gridLayout_8.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.randomize_all_custom_colors_together = QPushButton(self.tab_player_customization)
        self.randomize_all_custom_colors_together.setObjectName(u"randomize_all_custom_colors_together")

        self.horizontalLayout_2.addWidget(self.randomize_all_custom_colors_together)

        self.randomize_all_custom_colors_separately = QPushButton(self.tab_player_customization)
        self.randomize_all_custom_colors_separately.setObjectName(u"randomize_all_custom_colors_separately")

        self.horizontalLayout_2.addWidget(self.randomize_all_custom_colors_separately)


        self.gridLayout_8.addLayout(self.horizontalLayout_2, 2, 1, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_for_custom_player_model = QLabel(self.tab_player_customization)
        self.label_for_custom_player_model.setObjectName(u"label_for_custom_player_model")

        self.horizontalLayout_3.addWidget(self.label_for_custom_player_model)

        self.custom_player_model = QComboBox(self.tab_player_customization)
        self.custom_player_model.setObjectName(u"custom_player_model")

        self.horizontalLayout_3.addWidget(self.custom_player_model)


        self.gridLayout_8.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.player_in_casual_clothes = QCheckBox(self.tab_player_customization)
        self.player_in_casual_clothes.setObjectName(u"player_in_casual_clothes")

        self.horizontalLayout_4.addWidget(self.player_in_casual_clothes)

        self.disable_custom_player_voice = QCheckBox(self.tab_player_customization)
        self.disable_custom_player_voice.setObjectName(u"disable_custom_player_voice")

        self.horizontalLayout_4.addWidget(self.disable_custom_player_voice)

        self.disable_custom_player_items = QCheckBox(self.tab_player_customization)
        self.disable_custom_player_items.setObjectName(u"disable_custom_player_items")

        self.horizontalLayout_4.addWidget(self.disable_custom_player_items)


        self.gridLayout_8.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)

        self.install_custom_model = QPushButton(self.tab_player_customization)
        self.install_custom_model.setObjectName(u"install_custom_model")

        self.gridLayout_8.addWidget(self.install_custom_model, 0, 0, 1, 2)


        self.verticalLayout_4.addLayout(self.gridLayout_8)

        self.custom_model_comment = QLabel(self.tab_player_customization)
        self.custom_model_comment.setObjectName(u"custom_model_comment")
        self.custom_model_comment.setMaximumSize(QSize(810, 16777215))
        self.custom_model_comment.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.custom_model_comment)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.custom_colors_layout = QVBoxLayout()
        self.custom_colors_layout.setObjectName(u"custom_colors_layout")

        self.verticalLayout_5.addLayout(self.custom_colors_layout)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_4)


        self.horizontalLayout_5.addLayout(self.verticalLayout_5)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.custom_model_preview_label = QLabel(self.tab_player_customization)
        self.custom_model_preview_label.setObjectName(u"custom_model_preview_label")

        self.verticalLayout_6.addWidget(self.custom_model_preview_label)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_5)


        self.horizontalLayout_5.addLayout(self.verticalLayout_6)


        self.verticalLayout_4.addLayout(self.horizontalLayout_5)

        self.tabWidget.addTab(self.tab_player_customization, "")

        self.verticalLayout_2.addWidget(self.tabWidget)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.option_description = QLabel(self.centralwidget)
        self.option_description.setObjectName(u"option_description")
        self.option_description.setMinimumSize(QSize(0, 32))
        self.option_description.setWordWrap(True)

        self.verticalLayout.addWidget(self.option_description)

        self.update_checker_label = QLabel(self.centralwidget)
        self.update_checker_label.setObjectName(u"update_checker_label")
        self.update_checker_label.setOpenExternalLinks(True)

        self.verticalLayout.addWidget(self.update_checker_label)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.about_button = QPushButton(self.centralwidget)
        self.about_button.setObjectName(u"about_button")

        self.horizontalLayout_6.addWidget(self.about_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer)

        self.reset_settings_to_default = QPushButton(self.centralwidget)
        self.reset_settings_to_default.setObjectName(u"reset_settings_to_default")
        self.reset_settings_to_default.setMinimumSize(QSize(180, 0))

        self.horizontalLayout_6.addWidget(self.reset_settings_to_default)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_2)

        self.randomize_button = QPushButton(self.centralwidget)
        self.randomize_button.setObjectName(u"randomize_button")

        self.horizontalLayout_6.addWidget(self.randomize_button)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Wind Waker Randomizer", None))
        self.random_settings_explanation.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:xx-large; font-weight:700;\">Random Settings</span> </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This special client specifically generates Wind Waker Randomizer seeds with randomized settings. The client randomizes the settings according to a set of predefined weights. C"
                        "hest Type Matches Contents (CTMC) and path hints will <span style=\" font-weight:700;\">always</span> be on. You need to deduce which settings are enabled in your seed.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">First, set up your clean WW ISO path, output folder, and seed. Additionally, ensure the additional options and your custom player model are all set. Once ready, hit Randomize to randomize the seed and generate an ISO. Note that the randomizer will not create a spoiler or a non-spoiler log.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text"
                        "-indent:0px;\">The settings are randomly determined using the seed. If there's no seed, then a random seed will be used. If you wish to share/race a seed, the seed name is all that needs to be shared.  In rare cases, certain combinations of settings will fail to generate. Often, this is because not enough progress locations end up being selected. For races, it is recommended to ensure that a seed results in a successful generation before sharing it.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The random setting weights can be found here: <a href=\"https://github.com/tanjo3/wwrando/blob/random-settings/randomizers/random_settings.md\"><span style=\" text-decoration: underline; color:#0000ff;\">https://github.com/tanjo3/wwrando/blob/random-settings/randomizers/random_set"
                        "tings.md</span></a></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; text-decoration: underline; color:#0000ff;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Random Settings Tracker by Colfra: <a href=\"https://jaysc.github.io/tww-rando-tracker-rs/\"><span style=\" text-decoration: underline; color:#0000ff;\">https://jaysc.github.io/tww-rando-tracker-rs/</span></a></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Helpful Random Settings reference by Alex: <a href=\"http://bombch.us/DVy8\"><span style=\" text-decoration: underline; color:#0000ff;\">http://bombch.us/DVy8</span></a></p></body></html>", None))
        self.label_for_output_folder.setText(QCoreApplication.translate("MainWindow", u"Output Folder", None))
        self.label_for_seed.setText(QCoreApplication.translate("MainWindow", u"Seed", None))
        self.generate_seed_button.setText(QCoreApplication.translate("MainWindow", u"New seed", None))
        self.output_folder_browse_button.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.clean_iso_path_browse_button.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.label_for_clean_iso_path.setText(QCoreApplication.translate("MainWindow", u"Clean WW ISO", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Additional Options (Does Not Affect Seed Randomization)", None))
        self.invert_sea_compass_x_axis.setText(QCoreApplication.translate("MainWindow", u"Invert Sea Compass X-Axis", None))
        self.remove_title_and_ending_videos.setText(QCoreApplication.translate("MainWindow", u"Remove Title and Ending Videos", None))
        self.randomize_enemy_palettes.setText(QCoreApplication.translate("MainWindow", u"Randomize Enemy Palettes", None))
        self.invert_camera_x_axis.setText(QCoreApplication.translate("MainWindow", u"Invert Camera X-Axis", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_randomizer_settings), QCoreApplication.translate("MainWindow", u"Randomizer Settings", None))
        self.label_for_custom_color_preset.setText(QCoreApplication.translate("MainWindow", u"Color Preset", None))
        self.randomize_all_custom_colors_together.setText(QCoreApplication.translate("MainWindow", u"Randomize Colors Orderly", None))
        self.randomize_all_custom_colors_separately.setText(QCoreApplication.translate("MainWindow", u"Randomize Colors Chaotically", None))
        self.label_for_custom_player_model.setText(QCoreApplication.translate("MainWindow", u"Player Model", None))
        self.player_in_casual_clothes.setText(QCoreApplication.translate("MainWindow", u"Casual Clothes", None))
        self.disable_custom_player_voice.setText(QCoreApplication.translate("MainWindow", u"Disable Custom Voice", None))
        self.disable_custom_player_items.setText(QCoreApplication.translate("MainWindow", u"Disable Custom Items", None))
        self.install_custom_model.setText(QCoreApplication.translate("MainWindow", u"Install a Custom Model or Model Pack", None))
        self.custom_model_comment.setText("")
        self.custom_model_preview_label.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_player_customization), QCoreApplication.translate("MainWindow", u"Player Customization", None))
        self.option_description.setText("")
        self.update_checker_label.setText(QCoreApplication.translate("MainWindow", u"Checking for updates to the randomizer...", None))
        self.about_button.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.reset_settings_to_default.setText(QCoreApplication.translate("MainWindow", u"Reset All Settings to Default", None))
        self.randomize_button.setText(QCoreApplication.translate("MainWindow", u"Randomize", None))
    # retranslateUi

