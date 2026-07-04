import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPainter, QFont, QColor

import z3_solver_matrix as z3m
#import test as z3m
import my_icon

# Icon by http://www.game-insight.com, Fair use, https://en.wikipedia.org/w/index.php?curid=59625305

DARK_STYLE = """
    QMainWindow, QWidget { background-color: #1e1e1e; color: #ffffff; }
    .Tile { background-color: #2d2d2d; border: 1px solid #333; }
    QLabel#Title { font-size: 20px; font-weight: bold; color: #00ffcc; padding: 10px; }
"""

class SolverRenderer(QMainWindow):
    def __init__(self, result, solution_data):
        super().__init__()
        self.result = result
        self.solution = solution_data
        self.grid_size = 9   # tiles per grid edge
        self.tile_size = 60  # pixels per tile
        self.setWindowIcon(my_icon.iconFromBase64(my_icon.image_base64))
        self.setStyleSheet(DARK_STYLE)
        self.setWindowTitle("Z3 Airport City Solution Viewer")
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSizeConstraint(QVBoxLayout.SetFixedSize)

        title = QLabel(f"Layout Render with Optimal result: {self.result}")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        grid_widget = QWidget()
        self.grid = QGridLayout(grid_widget)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0) # Remove padding around the grid
        
        self.grid_size_x = len(self.solution)
        self.grid_size_y = len(self.solution[0])
        # Initialize an empty grid
        for r in range(self.grid_size_x):
            for c in range(self.grid_size_y):
                empty_tile = QLabel()
                empty_tile.setFixedSize(self.tile_size, self.tile_size)
                empty_tile.setProperty("class", "Tile")
                self.grid.addWidget(empty_tile, r, c)

        # Place the solution items
        self.place_matrix()

        main_layout.addWidget(grid_widget)

    def place_matrix(self):
        for row in range(self.grid_size_x):
            for col in range(self.grid_size_y):
                
                kind, small_tree, big_tree, huge_tree, has_visa, value = self.solution[row][col]

                name = z3m.id_to_name.get(kind, "unknown")
                
                if name == "filler":
                    continue

                if name == "empty":
                    continue
    
                # Create the image label
                img_label = QLabel()
                pixmap = QPixmap(f"images/{name}.png")
                size = z3m.HOUSE[name]["size"]
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
                        if all(self.is_safe_and_low_id(r, c) for r, c in neighbors_road):
                            continue
                    elif name == "tree":
                        # all() returns True if all neighbors pass the safe check
                        if all(self.is_safe_and_low_id(r, c) for r, c in neighbors_park):
                            continue
                    elif name != "visa":
                        print(f"{name} at {row},{col}")
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

    def is_safe_and_low_id(self, r, c):
        # 1. Check if row is in bounds
        if 0 <= r < len(self.solution):
            # 2. Check if column is in bounds
            if 0 <= c < len(self.solution[0]):
                # 3. Perform your ID check (e.g., ID < 4)
                return self.solution[r][c][0] < 4
        return True # Or False, depending on if an "edge" counts as a failure

if __name__ == "__main__":
    app = QApplication(sys.argv)
    success, result, Z3_list = z3m.run_z3_solver()
    if success:
        window = SolverRenderer(result, Z3_list)
        window.show()
        sys.exit(app.exec_())
    else:
        print("solution not found")