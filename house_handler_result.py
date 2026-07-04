import os

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor

import z3_solver_matrix as z3m
import house_handler_config as hhc

# Icon by http://www.game-insight.com, Fair use, https://en.wikipedia.org/w/index.php?curid=59625305

DARK_STYLE = """
    QMainWindow, QWidget { background-color: #1e1e1e; color: #ffffff; }
    .Tile { background-color: #2d2d2d; border: 1px solid #333; }
    QLabel#Title { font-size: 20px; font-weight: bold; color: #00ffcc; padding: 10px; }
"""

class ResultScreen(QWidget):
    def __init__(self):
        super().__init__()        
        self.grid_size = 9   # tiles per grid edge
        self.tile_size = 60  # pixels per tile
        self.setStyleSheet(DARK_STYLE)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSizeConstraint(QVBoxLayout.SetFixedSize)

    def init_ui(self, numerical_result, solution_data):

        while self.main_layout.count() > 0:
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        title = QLabel(f"Layout Render with Optimal result: {numerical_result}")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)

        grid_widget = QWidget()
        self.grid = QGridLayout(grid_widget)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        
        self.grid_size_x = len(solution_data)
        self.grid_size_y = len(solution_data[0])
        
        for r in range(self.grid_size_x):
            for c in range(self.grid_size_y):
                empty_tile = QLabel()
                empty_tile.setFixedSize(self.tile_size, self.tile_size)
                empty_tile.setProperty("class", "Tile")
                self.grid.addWidget(empty_tile, r, c)

        # Place the solution items
        self.place_matrix(solution_data)

        self.main_layout.addWidget(grid_widget)

        self.setLayout(self.main_layout)

    def place_matrix(self, solution_data):
        for row in range(self.grid_size_x):
            for col in range(self.grid_size_y):
                
                kind, small_tree, big_tree, huge_tree, has_visa, value = solution_data[row][col]

                name = z3m.id_to_name.get(kind, "unknown")
                
                if name == "filler":
                    continue

                if name == "empty":
                    continue
    
                # Create the image label
                img_label = QLabel()
                img_path = os.path.join(hhc.resource_path(hhc.IMAGE_DIR), f"{name}.png")
                pixmap = QPixmap(img_path)
                size = hhc.HOUSE[name]["size"]
                if not pixmap.isNull():
                    display_size = self.tile_size * size
                    scaled_pixmap = pixmap.scaled(display_size, display_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    neighbors_road = [
                        (row - 1, col),
                        (row + 1, col),
                        (row,     col - 1),
                        (row,     col + 1)
                    ]
                    neighbors_park = [
                        (row - 1, col),
                        (row + 1, col),
                        (row,     col - 1),
                        (row,     col + 1),
                        (row - 1, col - 1),
                        (row - 1, col + 1),
                        (row + 1, col - 1),
                        (row + 1, col + 1)
                    ]

                    if name == "road":
                        # all() returns True if all neighbors pass the safe check
                        if all(self.is_safe_and_low_id_roads(solution_data, r, c) for r, c in neighbors_road):
                            continue
                    elif name == "tree":
                        # all() returns True if all neighbors pass the safe check
                        if all(self.is_safe_and_low_id_trees(solution_data, r, c) for r, c in neighbors_park):
                            continue
                    elif name != "visa":
                        painter = QPainter(scaled_pixmap)
                        font = QFont("Arial", 14, QFont.Bold)
                        painter.setFont(font)
                        if value > 0:
                            painter.setPen(QColor("green"))
                        else:
                            painter.setPen(QColor("red"))
                        painter.drawText(5, 15, str(value))
                        painter.end()
                    img_label.setToolTip(name)
                    img_label.setPixmap(scaled_pixmap)
                else:
                    img_label.setText(name[:3])
                    img_label.setStyleSheet("background-color: #444; border: 1px solid white;")
               
                img_label.setAlignment(Qt.AlignCenter)
                img_label.setFixedSize(self.tile_size * size, self.tile_size * size)

                self.grid.addWidget(img_label, row, col, size, size)

    def is_safe_and_low_id_trees(self, solution_data, r, c):
        # 1. Check if row is in bounds
        if 0 <= r < len(solution_data):
            # 2. Check if column is in bounds
            if 0 <= c < len(solution_data[0]):
                # 3. Perform your ID check (e.g., ID < 4)
                return solution_data[r][c][0] < 4
        return True # Or False, depending on if an "edge" counts as a failure

    def is_safe_and_low_id_roads(self, solution_data, r, c):
        # 1. Check if row is in bounds
        if 0 <= r < len(solution_data):
            # 2. Check if column is in bounds
            if 0 <= c < len(solution_data[0]):
                # 3. Perform your ID check (e.g., ID < 4)
                return (solution_data[r][c][0] < 4 and solution_data[r][c][0] != 1)
        return True # Or False, depending on if an "edge" counts as a failure
