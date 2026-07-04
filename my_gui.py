import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QScrollArea, QHBoxLayout,
    QVBoxLayout, QCheckBox, QLabel, QFrame
)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QSize

import house_handler_config as hh

IMAGE_DIR = "./images"       # Folder where your PNGs are located
IMAGE_SIZE = 50       # Images will be forced to a 100x100 square
MARGIN_SIZE = 15      # Inter-space between image edge and the border line
BORDER_RADIUS = 12    # Rounded corner intensity

class HouseCard(QFrame):
    """A minimal, layout-clean interactive card that toggles selection 

    directly upon clicking the target asset image.
    """
    def __init__(self, house_name, data, parent=None):
        super().__init__(parent)
        self.house_name = house_name
        self.is_checked = False
        
        # Human-readable label for tooltips (e.g., "stone_castle" -> "Stone Castle")
        self.display_name = house_name.replace("_", " ").title()

        self.card_layout = QVBoxLayout(self)
        self.card_layout.setAlignment(Qt.AlignCenter)
        self.card_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Image Container Core setup
        self.image_container = QLabel(self)
        self.image_container.setAlignment(Qt.AlignCenter)
        
        # Calculate dynamic size box for padding around standard image dimensions
        container_dimensions = IMAGE_SIZE + (MARGIN_SIZE * 2) + 6
        self.image_container.setFixedSize(container_dimensions, container_dimensions)
        
        # Apply hover tooltip native tracking to the container asset box
        self.image_container.setToolTip(self.display_name)
        
        self.pixmap = self.load_image()
        self.image_container.setPixmap(self.pixmap)
        
        # Custom display drawing hook replacements
        self.image_container.paintEvent = self.custom_paint_event
        
        self.card_layout.addWidget(self.image_container)

    def load_image(self):
        img_path = os.path.join(IMAGE_DIR, f"{self.house_name}.png")
        pix = QPixmap(img_path)
        
        if pix.isNull():
            pix = QPixmap(IMAGE_SIZE, IMAGE_SIZE)
            pix.fill(QColor(80, 80, 80))
        else:
            pix = pix.scaled(IMAGE_SIZE, IMAGE_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
        return pix

    def custom_paint_event(self, event):
        """Paints image container background base layers and conditional vector highlights."""
        QLabel.paintEvent(self.image_container, event)
        
        if self.is_checked:
            painter = QPainter(self.image_container)
            painter.setRenderHint(QPainter.Antialiasing)
            
            pen = QPen(QColor(255, 255, 255), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            offset = 3
            w = self.image_container.width() - (offset * 2)
            h = self.image_container.height() - (offset * 2)
            
            painter.drawRoundedRect(offset, offset, w, h, BORDER_RADIUS, BORDER_RADIUS)
            painter.end()

    def mousePressEvent(self, event):
        """Intercept clicks directly targeting the image card component."""
        if event.button() == Qt.LeftButton:
            # Invert active flag status
            self.is_checked = not self.is_checked
            self.image_container.update()  # Refresh canvas presentation layer
            
            # Pipe status tracking updates up directly to standard master framework wrapper
            window = self.window()
            if hasattr(window, 'update_global_selection'):
                window.update_global_selection(self.house_name, self.is_checked)


class HouseViewerWindow(QWidget):
    def __init__(self, data):
        super().__init__()
        self.houses_data = data
        self.selected_houses = set()
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyQt5 House Grid Minimal")
        self.setFixedSize(1200, 800)
        self.setStyleSheet("background-color: #1e1e1e;") 

        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(15, 15, 15, 15)
        master_layout.setSpacing(15)

        exclude_keys = {"empty", "visa", "road", "tree"}

        # Initialize size column tracks
        columns = {1: QVBoxLayout(), 2: QVBoxLayout(), 3: QVBoxLayout()}
        
        for col_layout in columns.values():
            col_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            col_layout.setSpacing(15)

        # Sort asset cards across targeted data lanes
        for house_name, data in self.houses_data.items():
            if house_name.lower() in exclude_keys:
                continue
                
            house_size = data.get("size", 1)
            if house_size in columns:
                card = HouseCard(house_name, data)
                columns[house_size].addWidget(card)

        # Construct scroll panels for each categorized size lane
        for size_num in sorted(columns.keys()):
            col_wrapper = QVBoxLayout()
            
            header = QLabel(f"SIZE {size_num}")
            header.setStyleSheet("color: #00ffcc; font-weight: bold; font-size: 14px; margin-bottom: 5px;")
            header.setAlignment(Qt.AlignCenter)
            col_wrapper.addWidget(header)
            
            scroll = QScrollArea(self)
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("""
                QScrollArea { border: 1px solid #333333; background-color: #252525; border-radius: 6px; }
                QScrollBar:vertical { width: 8px; background: #252525; }
                QScrollBar::handle:vertical { background: #555555; border-radius: 4px; }
            """)
            
            inner_widget = QWidget()
            inner_widget.setStyleSheet("background-color: #252525;")
            inner_widget.setLayout(columns[size_num])
            
            scroll.setWidget(inner_widget)
            col_wrapper.addWidget(scroll)
            
            master_layout.addLayout(col_wrapper)

    def update_global_selection(self, name, select_status):
        if select_status:
            self.selected_houses.add(name)
        else:
            self.selected_houses.discard(name)
            
        print(f"Active Selections: {list(self.selected_houses)}")

class HouseViewerWindow(QWidget):
    def __init__(self, data):
        super().__init__()
        self.houses_data = data
        self.selected_houses = set()
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyQt5 House Grid (Filtered by Size)")
        # Force strict 1200x800 canvas dimensions
        self.setFixedSize(1200, 800)
        self.setStyleSheet("background-color: #1e1e1e;") 

        # Horizontal master layout splitting into columns
        master_layout = QHBoxLayout(self)
        master_layout.setContentsMargins(15, 15, 15, 15)
        master_layout.setSpacing(15)

        # Exclusion list definition
        exclude_keys = {"empty", "visa", "road", "tree"}

        # Generate structural column channels for Sizes 1, 2, and 3
        columns = {1: QVBoxLayout(), 2: QVBoxLayout(), 3: QVBoxLayout()}
        
        # Format alignment flags inside target columns
        for col_layout in columns.values():
            col_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            col_layout.setSpacing(10)

        # Sort elements into their respective column layouts based on "size"
        for house_name, data in self.houses_data.items():
            if house_name.lower() in exclude_keys:
                continue  # Skip filtered assets
                
            house_size = data.get("size", 1)
            if house_size in columns:
                card = HouseCard(house_name, data)
                columns[house_size].addWidget(card)

        # Package columns into clean scroll frames to prevent overflowing
        for size_num in sorted(columns.keys()):
            # Wrapper container
            col_wrapper = QVBoxLayout()
            
            # Header Label
            header = QLabel(f"HOUSE SIZE {size_num}")
            header.setStyleSheet("color: #00ffcc; font-weight: bold; font-size: 14px; margin-bottom: 5px;")
            header.setAlignment(Qt.AlignCenter)
            col_wrapper.addWidget(header)
            
            # Scroll Area infrastructure
            scroll = QScrollArea(self)
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("""
                QScrollArea { border: 1px solid #333333; background-color: #252525; border-radius: 6px; }
                QScrollBar:vertical { width: 8px; background: #252525; }
                QScrollBar::handle:vertical { background: #555555; border-radius: 4px; }
            """)
            
            inner_widget = QWidget()
            inner_widget.setStyleSheet("background-color: #252525;")
            inner_widget.setLayout(columns[size_num])
            
            scroll.setWidget(inner_widget)
            col_wrapper.addWidget(scroll)
            
            # Mount onto master track layout
            master_layout.addLayout(col_wrapper)

    def update_global_selection(self, name, select_status):
        if select_status:
            self.selected_houses.add(name)
        else:
            self.selected_houses.discard(name)
            
        print(f"Active Selections: {list(self.selected_houses)}")

if __name__ == "__main__":

    loaded_houses = hh.load_houses(hh.FILE_NAME)

    app = QApplication(sys.argv)
    viewer = HouseViewerWindow(loaded_houses)
    viewer.show()
    sys.exit(app.exec_())