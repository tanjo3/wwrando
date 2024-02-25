# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'randomizer_window.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTabWidget, QVBoxLayout, QWidget)

from wwr_ui.cosmetic_tab import CosmeticTab

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(914, 757)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMinimumSize(QSize(600, 400))
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 879, 600))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.scrollAreaWidgetContents)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_randomizer_settings = QWidget()
        self.tab_randomizer_settings.setObjectName(u"tab_randomizer_settings")
        self.verticalLayout_3 = QVBoxLayout(self.tab_randomizer_settings)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.plando_file = QLineEdit(self.tab_randomizer_settings)
        self.plando_file.setObjectName(u"plando_file")

        self.gridLayout.addWidget(self.plando_file, 2, 1, 1, 1)

        self.label_for_clean_iso_path = QLabel(self.tab_randomizer_settings)
        self.label_for_clean_iso_path.setObjectName(u"label_for_clean_iso_path")
        self.label_for_clean_iso_path.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout.addWidget(self.label_for_clean_iso_path, 0, 0, 1, 1)

        self.clean_iso_path = QLineEdit(self.tab_randomizer_settings)
        self.clean_iso_path.setObjectName(u"clean_iso_path")

        self.gridLayout.addWidget(self.clean_iso_path, 0, 1, 1, 1)

        self.label_for_output_folder = QLabel(self.tab_randomizer_settings)
        self.label_for_output_folder.setObjectName(u"label_for_output_folder")

        self.gridLayout.addWidget(self.label_for_output_folder, 1, 0, 1, 1)

        self.output_folder = QLineEdit(self.tab_randomizer_settings)
        self.output_folder.setObjectName(u"output_folder")

        self.gridLayout.addWidget(self.output_folder, 1, 1, 1, 1)

        self.output_folder_browse_button = QPushButton(self.tab_randomizer_settings)
        self.output_folder_browse_button.setObjectName(u"output_folder_browse_button")

        self.gridLayout.addWidget(self.output_folder_browse_button, 1, 2, 1, 1)

        self.label_for_plando_file = QLabel(self.tab_randomizer_settings)
        self.label_for_plando_file.setObjectName(u"label_for_plando_file")
        self.label_for_plando_file.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout.addWidget(self.label_for_plando_file, 2, 0, 1, 1)

        self.plando_file_browse_button = QPushButton(self.tab_randomizer_settings)
        self.plando_file_browse_button.setObjectName(u"plando_file_browse_button")

        self.gridLayout.addWidget(self.plando_file_browse_button, 2, 2, 1, 1)

        self.clean_iso_path_browse_button = QPushButton(self.tab_randomizer_settings)
        self.clean_iso_path_browse_button.setObjectName(u"clean_iso_path_browse_button")

        self.gridLayout.addWidget(self.clean_iso_path_browse_button, 0, 2, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.groupBox = QGroupBox(self.tab_randomizer_settings)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_4 = QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.invert_sea_compass_x_axis = QCheckBox(self.groupBox)
        self.invert_sea_compass_x_axis.setObjectName(u"invert_sea_compass_x_axis")

        self.gridLayout_4.addWidget(self.invert_sea_compass_x_axis, 0, 1, 1, 1)

        self.remove_title_and_ending_videos = QCheckBox(self.groupBox)
        self.remove_title_and_ending_videos.setObjectName(u"remove_title_and_ending_videos")
        self.remove_title_and_ending_videos.setChecked(True)

        self.gridLayout_4.addWidget(self.remove_title_and_ending_videos, 1, 0, 1, 1)

        self.switch_targeting_mode = QCheckBox(self.groupBox)
        self.switch_targeting_mode.setObjectName(u"switch_targeting_mode")

        self.gridLayout_4.addWidget(self.switch_targeting_mode, 0, 0, 1, 1)

        self.invert_camera_x_axis = QCheckBox(self.groupBox)
        self.invert_camera_x_axis.setObjectName(u"invert_camera_x_axis")

        self.gridLayout_4.addWidget(self.invert_camera_x_axis, 1, 1, 1, 1)


        self.horizontalLayout_2.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.tab_randomizer_settings)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_10 = QGridLayout(self.groupBox_2)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.randomize_enemy_palettes = QCheckBox(self.groupBox_2)
        self.randomize_enemy_palettes.setObjectName(u"randomize_enemy_palettes")

        self.gridLayout_10.addWidget(self.randomize_enemy_palettes, 0, 0, 1, 1)

        self.widget = QWidget(self.groupBox_2)
        self.widget.setObjectName(u"widget")

        self.gridLayout_10.addWidget(self.widget, 1, 0, 1, 1)


        self.horizontalLayout_2.addWidget(self.groupBox_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tab_randomizer_settings, "")
        self.tab_player_customization = CosmeticTab()
        self.tab_player_customization.setObjectName(u"tab_player_customization")
        self.tabWidget.addTab(self.tab_player_customization, "")

        self.verticalLayout_2.addWidget(self.tabWidget)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.option_description = QLabel(self.centralwidget)
        self.option_description.setObjectName(u"option_description")
        self.option_description.setMinimumSize(QSize(0, 32))
        self.option_description.setTextFormat(Qt.TextFormat.RichText)
        self.option_description.setWordWrap(True)

        self.verticalLayout.addWidget(self.option_description)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.about_button = QPushButton(self.centralwidget)
        self.about_button.setObjectName(u"about_button")

        self.horizontalLayout.addWidget(self.about_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.randomize_button = QPushButton(self.centralwidget)
        self.randomize_button.setObjectName(u"randomize_button")

        self.horizontalLayout.addWidget(self.randomize_button)


        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        QWidget.setTabOrder(self.tabWidget, self.scrollArea)
        QWidget.setTabOrder(self.scrollArea, self.clean_iso_path)
        QWidget.setTabOrder(self.clean_iso_path, self.clean_iso_path_browse_button)
        QWidget.setTabOrder(self.clean_iso_path_browse_button, self.output_folder)
        QWidget.setTabOrder(self.output_folder, self.output_folder_browse_button)
        QWidget.setTabOrder(self.output_folder_browse_button, self.plando_file)
        QWidget.setTabOrder(self.plando_file, self.plando_file_browse_button)
        QWidget.setTabOrder(self.plando_file_browse_button, self.randomize_enemy_palettes)
        QWidget.setTabOrder(self.randomize_enemy_palettes, self.switch_targeting_mode)
        QWidget.setTabOrder(self.switch_targeting_mode, self.invert_sea_compass_x_axis)
        QWidget.setTabOrder(self.invert_sea_compass_x_axis, self.remove_title_and_ending_videos)
        QWidget.setTabOrder(self.remove_title_and_ending_videos, self.invert_camera_x_axis)
        QWidget.setTabOrder(self.invert_camera_x_axis, self.about_button)
        QWidget.setTabOrder(self.about_button, self.randomize_button)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"The Wind Waker Archipelago Randomizer", None))
        self.label_for_clean_iso_path.setText(QCoreApplication.translate("MainWindow", u"Vanilla Wind Waker ISO [[?]](help)", None))
        self.label_for_output_folder.setText(QCoreApplication.translate("MainWindow", u"Randomized Output Folder", None))
        self.output_folder_browse_button.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.label_for_plando_file.setText(QCoreApplication.translate("MainWindow", u"APTWW File [[?]](help)", None))
        self.plando_file_browse_button.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.clean_iso_path_browse_button.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Convenience Tweaks", None))
        self.invert_sea_compass_x_axis.setText(QCoreApplication.translate("MainWindow", u"Invert Sea Compass X-Axis", None))
        self.remove_title_and_ending_videos.setText(QCoreApplication.translate("MainWindow", u"Remove Title and Ending Videos", None))
        self.switch_targeting_mode.setText(QCoreApplication.translate("MainWindow", u"Use 'Switch' Targeting Mode", None))
        self.invert_camera_x_axis.setText(QCoreApplication.translate("MainWindow", u"Invert Camera X-Axis", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Other Randomizers", None))
        self.randomize_enemy_palettes.setText(QCoreApplication.translate("MainWindow", u"Randomize Enemy Palettes", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_randomizer_settings), QCoreApplication.translate("MainWindow", u"Randomizer Settings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_player_customization), QCoreApplication.translate("MainWindow", u"Player Customization", None))
        self.option_description.setText("")
        self.about_button.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.randomize_button.setText(QCoreApplication.translate("MainWindow", u"Randomize", None))
    # retranslateUi

