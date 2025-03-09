import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QComboBox,
)
from PyQt6.QtGui import QPixmap
from pydantic import BaseModel
from enum import Enum
from PyQt6.QtCore import Qt


class TileType(str, Enum):
    SewerPipeTile = "SewerPipeTile"
    SinglePlasmaDrillTile = "SinglePlasmaDrillTile"
    DoublePlasmaDrillTile = "DoublePlasmaDrillTile"
    CentralHousingUnitTile = "CentralHousingUnitTile"
    ModularHousingUnitTile = "ModularHousingUnitTile"
    TripleStandardStorageCompartmentTile = "TripleStandardStorageCompartmentTile"
    DoubleStandardStorageCompartmentTile = "DoubleStandardStorageCompartmentTile"
    DoubleSpecialStorageCompartmentTile = "DoubleSpecialStorageCompartmentTile"
    SingleSpecialStorageCompartmentTile = "SingleSpecialStorageCompartmentTile"
    TriplePowerCenterTile = "TriplePowerCenterTile"
    DoublePowerCenterTile = "DoublePowerCenterTile"
    SingleEngineTile = "SingleEngineTile"
    DoubleEngineTile = "DoubleEngineTile"
    PurpleLifeSupportSystemTile = "PurpleLifeSupportSystemTile"
    BrownLifeSupportSystemTile = "BrownLifeSupportSystemTile"


class ConnectorType(str, Enum):
    Smooth = "Smooth"
    OnePiped = "OnePiped"
    TwoPiped = "TwoPiped"
    Universal = "Universal"


class Tile(BaseModel):
    tile_type: TileType | None = None
    # N E S W
    connectors: list[ConnectorType | None] = [None, None, None, None]


class ImageGallery(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Card Mapping Tool")
        self.setGeometry(100, 100, 400, 500)

        self.image_folder = "./tiles/"
        self.image_files = sorted([f for f in os.listdir(self.image_folder) if f.endswith(".jpg")])
        self.current_index = 0

        self.tiles_file = "tiles.json"
        self.tiles_data = self.load_or_create_tiles_data()

        self.initUI()

    def load_or_create_tiles_data(self):
        if os.path.exists(self.tiles_file):
            with open(self.tiles_file, "r") as file:
                tiles_data = json.load(file)
        else:
            tiles_data = {f: {"tile_type": None, "connectors": [None, None, None, None]} for f in self.image_files}
            with open(self.tiles_file, "w") as file:
                json.dump(tiles_data, file, indent=4)

        # Deserialize tiles_data into Tile objects
        return {k: Tile(**v) for k, v in tiles_data.items()}

    def save_tiles_data(self):
        tiles_data = {k: v.model_dump() for k, v in self.tiles_data.items()}
        with open(self.tiles_file, "w") as file:
            json.dump(tiles_data, file, indent=4)

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.connector_dropdowns = {}

        # Create dropdowns for N, E, S, W
        for direction in ["N", "E", "S", "W"]:
            self.connector_dropdowns[direction] = self.create_dropdown(ConnectorType, self.update_connector_type)

        # N dropdown
        self.layout.addWidget(self.connector_dropdowns["N"])

        # Image and W/E dropdowns
        self.image_and_side_layout = QHBoxLayout()
        self.layout.addLayout(self.image_and_side_layout)

        # W dropdown
        self.image_and_side_layout.addWidget(self.connector_dropdowns["W"])

        # Image
        self.image_label = QLabel()
        self.image_and_side_layout.addWidget(self.image_label)

        # E dropdown
        self.image_and_side_layout.addWidget(self.connector_dropdowns["E"])

        # S dropdown
        self.layout.addWidget(self.connector_dropdowns["S"])

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.prev_button = QPushButton("<")
        self.prev_button.clicked.connect(self.show_prev_image)
        self.button_layout.addWidget(self.prev_button)

        self.tile_type_dropdown = self.create_dropdown(TileType, self.update_tile_type)
        self.layout.addWidget(self.tile_type_dropdown)
        self.button_layout.addWidget(self.tile_type_dropdown)

        self.next_button = QPushButton(">")
        self.next_button.clicked.connect(self.show_next_image)
        self.button_layout.addWidget(self.next_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_tiles_data)
        self.layout.addWidget(self.save_button)

        self.show_image()

    def create_dropdown(self, enum_class, callback):
        dropdown = QComboBox()
        dropdown.addItem("?")
        dropdown.addItems([item.value for item in enum_class])
        dropdown.currentIndexChanged.connect(callback)
        dropdown.currentIndexChanged.connect(lambda: self.update_dropdown_color(dropdown))
        self.update_dropdown_color(dropdown)  # Initial color update
        return dropdown

    def update_dropdown_color(self, dropdown):
        if dropdown.currentText() == "?":
            dropdown.setStyleSheet("QComboBox { background-color: red; }")
        else:
            dropdown.setStyleSheet("QComboBox { background-color: green; }")

    def show_image(self):
        if self.image_files:
            image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size()))

            # Update window title with current filename
            self.setWindowTitle(f"Card Mapping Tool ({self.image_files[self.current_index]})")

            # Get the Tile object for the current image
            image_file = self.image_files[self.current_index]
            tile = self.tiles_data.get(image_file)
            print(f"Loaded tile data for {image_file}: {tile}")

            # Update the dropdown to reflect the current tile type
            self.update_dropdown(self.tile_type_dropdown, tile.tile_type)

            # Update the connector dropdowns to reflect the current connectors
            for direction, connector_dropdown in self.connector_dropdowns.items():
                connector_type = tile.connectors[["N", "E", "S", "W"].index(direction)]
                print(f"Updating dropdown for {direction} to {connector_type}")
                self.update_dropdown(connector_dropdown, connector_type)

    def update_dropdown(self, dropdown, value):
        if value:
            index = dropdown.findText(value.value)
        else:
            index = dropdown.findText("?")
        if index >= 0:
            dropdown.blockSignals(True)
            dropdown.setCurrentIndex(index)
            self.update_dropdown_color(dropdown)
            dropdown.blockSignals(False)
        else:
            raise ValueError(f"Value {value} not found in dropdown {dropdown}")

    def update_tile_type(self):
        if self.image_files:
            image_file = self.image_files[self.current_index]
            tile = self.tiles_data.get(image_file)
            if tile:
                selected_text = self.tile_type_dropdown.currentText()
                tile.tile_type = TileType(selected_text) if selected_text != "?" else None
                print(f"Updated tile type for {image_file} to {tile.tile_type}")

    def update_connector_type(self):
        if self.image_files:
            image_file = self.image_files[self.current_index]
            tile = self.tiles_data.get(image_file)
            if tile:
                for direction, connector_dropdown in self.connector_dropdowns.items():
                    selected_text = connector_dropdown.currentText()
                    tile.connectors[["N", "E", "S", "W"].index(direction)] = (
                        ConnectorType(selected_text) if selected_text != "?" else None
                    )
                print(f"Updated connectors for {image_file} to {tile.connectors}")

    def show_prev_image(self):
        if self.image_files:
            self.save_tiles_data()  # Autosave before changing the image
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.show_image()

    def show_next_image(self):
        if self.image_files:
            self.save_tiles_data()  # Autosave before changing the image
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.show_image()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.show_prev_image()
        elif event.key() == Qt.Key.Key_Right:
            self.show_next_image()
        elif event.key() == Qt.Key.Key_W:
            self.connector_dropdowns["N"].showPopup()
        elif event.key() == Qt.Key.Key_D:
            self.connector_dropdowns["E"].showPopup()
        elif event.key() == Qt.Key.Key_S:
            self.connector_dropdowns["S"].showPopup()
        elif event.key() == Qt.Key.Key_A:
            self.connector_dropdowns["W"].showPopup()
        elif event.key() == Qt.Key.Key_E:
            self.tile_type_dropdown.showPopup()

    def closeEvent(self, event):
        self.save_tiles_data()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gallery = ImageGallery()
    gallery.show()
    sys.exit(app.exec())
