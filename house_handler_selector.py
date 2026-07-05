import os
from PyQt5.QtWidgets import QWidget, QScrollArea, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt

import house_handler_config as hhc

IMAGE_SIZE = 40                                         # Images will be forced to a 50x50 square
MARGIN_SIZE = 10                                        # Inter-space between image edge and the border line
BORDER_RADIUS = 10                                      # Rounded corner intensity

class HouseCard(QFrame):
    def __init__(self, house_name, size, on_toggle_callback, parent=None):
        super().__init__(parent)
        self.house_name = house_name
        self.is_checked = True
        self.on_toggle_callback = on_toggle_callback
        
        # Human-readable label for tooltips (e.g., "stone_castle" -> "Stone Castle")
        self.display_name = house_name.replace("_", " ").title()

        self.card_layout = QVBoxLayout(self)
        self.card_layout.setAlignment(Qt.AlignCenter)
        self.card_layout.setContentsMargins(0, 0, 0, 0)

        self.image_container = QLabel(self)
        self.image_container.setAlignment(Qt.AlignCenter)
        
        container_dimensions = (size*IMAGE_SIZE) + (MARGIN_SIZE * 2) + 6
        self.image_container.setFixedSize(container_dimensions, container_dimensions)
        
        self.image_container.setToolTip(self.display_name)
        
        self.pixmap = self.load_image(size)
        self.image_container.setPixmap(self.pixmap)
        
        self.image_container.paintEvent = self.custom_paint_event
        
        self.card_layout.addWidget(self.image_container)

        self.on_toggle_callback(self.house_name, True)

    def load_image(self, size):
        img_path = os.path.join(hhc.resource_path(hhc.IMAGE_DIR), f"{self.house_name}.png")
        pix = QPixmap(img_path)
        
        if pix.isNull():
            pix = QPixmap(size*IMAGE_SIZE, size*IMAGE_SIZE)
            pix.fill(QColor(80, 80, 80))
        else:
            pix = pix.scaled(size*IMAGE_SIZE, size*IMAGE_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
        return pix

    def custom_paint_event(self, event):
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

    def set_selected(self, checked_state):
        if self.is_checked != checked_state:
            self.is_checked = checked_state
            self.image_container.update()
            self.on_toggle_callback(self.house_name, checked_state)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.set_selected(not self.is_checked)


class HouseSelectorScreen(QWidget):
    def __init__(self, data, submit_callback, toggle_callback):
        super().__init__()
        self.houses_data = data
        self.selected_houses = set()
        self.submit_callback = submit_callback
        self.toggle_callback = toggle_callback
        self.init_ui()

    def init_ui(self):

        main_layout = QHBoxLayout(self)
        
        cards_by_size = {1: [], 2: [], 3: []}
        self.cards = []

        for house_name, data in self.houses_data.items():
            if house_name.lower() in hhc.EXCLUDE_KEYS:
                continue
            house_size = data.get("size", 1)
            if house_size in cards_by_size:
                card = HouseCard(house_name, house_size, self.toggle_callback)
                self.cards.append(card)
                cards_by_size[house_size].append(card)

        for size_num in [1, 2, 3]:
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
            
            # --- SPECIFIC ADJUSTMENT FOR SIZE 2 ---
            if size_num == 2:
                # Instead of a single vertical column, create an internal horizontal grid layout
                # built from 3 distinct vertical lanes side-by-side
                size2_master_layout = QHBoxLayout(inner_widget)
                size2_master_layout.setSpacing(10)
                size2_master_layout.setContentsMargins(5, 5, 5, 5)
                
                sub_columns = [QVBoxLayout(), QVBoxLayout(), QVBoxLayout(), QVBoxLayout(), QVBoxLayout()]
                for sub_col in sub_columns:
                    sub_col.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
                    sub_col.setSpacing(10)
                    size2_master_layout.addLayout(sub_col)
                
                for idx, card in enumerate(cards_by_size[2]):
                    target_sub_column = idx % 5
                    sub_columns[target_sub_column].addWidget(card)
            
            # --- STANDARD BEHAVIOR FOR SIZES 1 & 3 ---
            else:
                standard_layout = QVBoxLayout(inner_widget)
                standard_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
                standard_layout.setSpacing(15)
                
                for card in cards_by_size[size_num]:
                    standard_layout.addWidget(card)

            scroll.setWidget(inner_widget)
            col_wrapper.addWidget(scroll)
            
            stretch_factor = 3 if size_num == 2 else 1
            main_layout.addLayout(col_wrapper, stretch=stretch_factor)

    def bulk_toggle_cards(self, state):
        """Loops through every active UI asset block and forces state synchronization."""
        for card in self.cards:
            card.set_selected(state)
