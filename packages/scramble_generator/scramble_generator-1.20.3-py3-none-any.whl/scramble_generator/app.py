"""
Python app for generating scrambles for twisty puzzles.
"""

import sys

from PySide6.QtCore import Qt, QTimer, QTime
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QComboBox,
    QSpinBox,
    QGridLayout,
)

from .scramble_generator import ScrambleGenerator as SG
from .yaml_file_handler import YamlFileHandler

config_file = YamlFileHandler("resources/configs/config.yaml")
config = config_file.load_yaml_file()

themes_file = YamlFileHandler("resources/configs/themes.yaml")
themes = themes_file.load_yaml_file()


class ScrambleGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.show()

        # * Set window default settings
        self.setWindowTitle("Scramble Generator")
        self.setFixedSize(
            config["window_size"]["width"], config["window_size"]["height"]
        )

        # * Define normal variables
        self.is_running = False
        self.elapsed_time = QTime(0, 0)
        self.puzzle_type_list = [puzzle for puzzle in config["puzzle_type_list"]]

        # * Create end user widgets and apply settings to them
        self.scramble_button = QPushButton("Generate Scramble")

        self.puzzle_type = QComboBox()
        self.puzzle_type.addItems(self.puzzle_type_list)
        self.puzzle_type.setCurrentText(config["defaults"]["puzzle_type"])

        self.num_moves = QSpinBox()
        self.num_moves.setRange(
            config["num_moves_range"]["min"], config["num_moves_range"]["max"]
        )
        self.num_moves.setValue(config["defaults"]["num_moves"])

        self.theme_toggle = QPushButton(config["defaults"]["theme"])

        self.scramble = QLabel(
            " ", alignment=Qt.AlignmentFlag.AlignCenter, wordWrap=True
        )
        self.scramble.setFixedWidth(config["scramble_widget_width"])

        self.timer_button = QPushButton("Start Timer")

        self.timer_output = QLabel(
            "00:00.0", alignment=Qt.AlignmentFlag.AlignCenter, maximumHeight=22
        )

        self.timer = QTimer()
        self.timer.interval = 10  # * Milliseconds

        # * Define button connections and/or actions
        self.scramble_button.pressed.connect(self.get_moves)
        self.puzzle_type.currentTextChanged.connect(self.set_default_num_moves)
        self.theme_toggle.pressed.connect(self.toggle_theme)
        self.timer_button.pressed.connect(self.toggle_timer)
        self.timer.timeout.connect(self.update_time)

        # * Create layouts
        page = QGridLayout()
        left_side = QGridLayout()
        left_side.setVerticalSpacing(5)
        right_side = QGridLayout()

        # * Add widgets to layouts
        left_side.addWidget(self.scramble_button, 0, 0, 1, 2)
        left_side.addWidget(self.puzzle_type, 1, 0, 1, 1)
        left_side.addWidget(self.num_moves, 1, 1, 1, 1)
        left_side.addWidget(self.timer_button, 2, 0, 1, 2)
        left_side.addWidget(self.timer_output, 3, 0, 1, 2)
        left_side.addWidget(self.theme_toggle, 4, 0, 1, 2)

        right_side.addWidget(self.scramble, 0, 0, 1, 2)

        # * Setup overall page layout and set default window theme
        page.addLayout(left_side, 0, 0)
        page.addLayout(right_side, 0, 1)

        gui = QWidget()
        gui.setLayout(page)

        self.setCentralWidget(gui)

        self.apply_theme(self.theme_toggle.text().lower())

    def toggle_theme(self):
        if self.theme_toggle.text() == "Dark":
            self.theme_toggle.setText("Light")
            theme = self.theme_toggle.text()
        else:
            self.theme_toggle.setText("Dark")
            theme = self.theme_toggle.text()

        self.apply_theme(theme.lower())

    def apply_theme(self, theme):
        self.main_stylesheet = f"""
            background-color: {themes[theme]["background-color"]};
            color: {themes[theme]["color"]};
            border: {themes[theme]["border"]};
            border-radius: {themes["general"]["border-radius"]};
            padding: {themes["general"]["padding"]};
            """
        self.widget_stylesheet = f"""
            background-color: {themes[theme]["widget-background-color"]};
            """
        self.setStyleSheet(self.main_stylesheet)
        self.scramble_button.setStyleSheet(self.widget_stylesheet)
        self.puzzle_type.setStyleSheet(self.widget_stylesheet)
        self.num_moves.setStyleSheet(self.widget_stylesheet)
        self.theme_toggle.setStyleSheet(self.widget_stylesheet)
        self.scramble.setStyleSheet(self.widget_stylesheet)
        self.timer_button.setStyleSheet(self.widget_stylesheet)
        self.timer_output.setStyleSheet(self.widget_stylesheet)

        (
            self.theme_toggle.setText("Dark")
            if theme == "dark"
            else self.theme_toggle.setText("Light")
        )

    def get_moves(self):
        scramble = SG()
        self.scramble.setText(
            scramble.generate_scramble(
                self.puzzle_type.currentText().lower(), self.num_moves.value()
            )
        )

    def set_default_num_moves(self):
        self.num_moves.setValue(
            config["puzzle_default_moves"][self.puzzle_type.currentText().lower()]
        )

    def toggle_timer(self):
        if not self.is_running:
            self.timer.start(100)  # * Update display every 100 milliseconds
            self.timer_button.setText("Stop Timer")
            self.is_running = True
        else:
            self.timer.stop()
            self.timer_button.setText("Start Timer")
            self.is_running = False
            self.update_time()

    def update_time(self):
        self.elapsed_time = self.elapsed_time.addMSecs(
            100
        )  # * Increment time by 100 milliseconds
        self.timer_output.setText(self.elapsed_time.toString("mm:ss.z"))

        if not self.is_running:
            self.elapsed_time = QTime(0, 0)


def main():
    app = QApplication(sys.argv)
    main_window = ScrambleGenerator()  # noqa: F841
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
