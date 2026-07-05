import sys
import time
from datetime import timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QMovie

import house_handler_config as hhc
import house_handler_selector as hhs
import house_handler_result as hhr
import z3_solver_matrix as z3m
import my_icon

DARK_STYLE = """
    QMainWindow, QWidget { background-color: #1e1e1e; color: #ffffff; }
    .Tile { background-color: #2d2d2d; border: 1px solid #333; }
    QLabel#Title { font-size: 20px; font-weight: bold; color: #00ffcc; padding: 10px; }
"""


class NavigationHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        
        self.label_select_houses = QLabel("Select Houses", self)
        self.label_results = QLabel("Results Display", self)
        self.label_select_houses.setStyleSheet(hhc.ACTIVE_STYLESHEET)
        self.label_results.setStyleSheet(hhc.INACTIVE_STYLESHEET)

        for btn in [self.label_select_houses, self.label_results]:
            main_layout.addWidget(btn)
            
        main_layout.addStretch()

        self.btn_switch_state = QPushButton("Optimize", self)
        self.btn_switch_state.setStyleSheet(hhc.ACTIVE_STYLESHEET)

        self.btn_select_all = QPushButton("Select All", self)
        self.btn_select_all.setStyleSheet(hhc.INACTIVE_STYLESHEET)

        self.btn_deselect_all = QPushButton("Deselect All", self)
        self.btn_deselect_all.setStyleSheet(hhc.INACTIVE_STYLESHEET)
        
        for btn in [self.btn_switch_state, self.btn_select_all, self.btn_deselect_all]:
            btn.setCursor(Qt.PointingHandCursor)
            main_layout.addWidget(btn)

    def go_selector(self):
        self.label_select_houses.setStyleSheet(hhc.ACTIVE_STYLESHEET)
        self.label_results.setStyleSheet(hhc.INACTIVE_STYLESHEET)
        self.btn_switch_state.setText("Optimize")
        self.btn_select_all.setEnabled(True)
        self.btn_deselect_all.setEnabled(True)

    def go_waiting(self):
        self.btn_switch_state.setEnabled(False)
        self.btn_select_all.setEnabled(False)
        self.btn_deselect_all.setEnabled(False)

    def go_results(self):
        self.label_select_houses.setStyleSheet(hhc.INACTIVE_STYLESHEET)
        self.label_results.setStyleSheet(hhc.ACTIVE_STYLESHEET)
        self.btn_switch_state.setText("Return to Selector")
        self.btn_switch_state.setEnabled(True)

class WaitingScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.message = QLabel("Submission Successful!", self)
        self.message.setStyleSheet("color: #00ffcc; font-size: 28px; font-weight: bold;")
        
        self.sub_message1 = QLabel("Your custom house list has been cataloged.\nOptimal Solution is being computed", self)
        self.sub_message1.setStyleSheet("color: #a0a0a0; font-size: 16px; margin-top: 10px;")

        self.sub_message2 = QLabel("Runtime all buildings on \n   - Windows 16 gb RAM: ~2 mins\n   - Mac M4   16 gb RAM: XX mins", self)
        self.sub_message2.setStyleSheet("color: #a0a0a0; font-size: 14px; margin-top: 10px;")

        self.MovieLabel = QLabel(self)
        self.movie = QMovie(hhc.resource_path(hhc.GIF_FILE_NAME))
        self.MovieLabel.setMovie(self.movie)
        self.movie.start()

        layout.addWidget(self.message, alignment=Qt.AlignLeft)
        layout.addWidget(self.sub_message1, alignment=Qt.AlignLeft)
        layout.addWidget(self.sub_message2, alignment=Qt.AlignLeft)
        layout.addWidget(self.MovieLabel, alignment=Qt.AlignCenter)

class Z3SolverWorker(QThread):
    finished = pyqtSignal(bool, object, list, str)

    def __init__(self, submitted_data):
        super().__init__()
        self.submitted_data = submitted_data

    def run(self):
        start_time = time.time()

        success, numerical_result, Z3_list = z3m.run_z3_solver(self.submitted_data)

        end_time = time.time()
        elapsed_seconds = end_time - start_time
        duration_string = str(timedelta(seconds=int(elapsed_seconds)))

        self.finished.emit(success, numerical_result, Z3_list, duration_string)

class MainWindow(QWidget):
    def __init__(self, data):
        super().__init__()
        self.houses_data = data
        self.selected_houses = set()

        self.setWindowIcon(my_icon.iconFromBase64(my_icon.image_base64))
        self.setStyleSheet(DARK_STYLE)
        self.setWindowTitle("Z3 Airport City Solution Viewer")
        self.setMinimumSize(1100, 800)

        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(10, 10, 10, 10)

        self.header = NavigationHeader()
        self.stack = QStackedWidget(self)

        self.selection_screen = hhs.HouseSelectorScreen(self.houses_data, 
                                                        self.handle_submit, 
                                                        self.update_global_selection)
        self.waiting_screen = WaitingScreen()
        self.result_screen = hhr.ResultScreen()

        self.header.btn_switch_state.clicked.connect(lambda: self.handle_submit())
        self.header.btn_select_all.clicked.connect(lambda: self.selection_screen.bulk_toggle_cards(True))
        self.header.btn_deselect_all.clicked.connect(lambda: self.selection_screen.bulk_toggle_cards(False))

        self.stack.addWidget(self.selection_screen)  # Index 0
        self.stack.addWidget(self.waiting_screen) # Index 1
        self.stack.addWidget(self.result_screen) # Index 2

        window_layout.addWidget(self.header)
        window_layout.addWidget(self.stack)

        self.current_state = "SELECT_HOUSES"

    def update_global_selection(self, name, select_status):
        if select_status:
            self.selected_houses.add(name)
        else:
            self.selected_houses.discard(name)

    def handle_submit(self):
        if self.current_state == "SELECT_HOUSES":
            
            self.selected_houses.update(hhc.EXCLUDE_KEYS)
            submitted_houses_dict = {
                house_name: self.houses_data[house_name]
                for house_name in self.selected_houses
            }

            self.stack.setCurrentIndex(1)
            self.header.go_waiting()
            
            # ----
            self.worker = Z3SolverWorker(submitted_houses_dict)
            self.worker.finished.connect(self.on_solver_completed)
            self.worker.start()
            # ----

            self.current_state = "DISPLAY_RESULTS"
        else:
            self.stack.setCurrentIndex(0)
            self.header.go_selector()
            self.current_state = "SELECT_HOUSES"

    def on_solver_completed(self, success, numerical_result, Z3_list, duration_string):
        if success:
            self.result_screen.init_ui_success(numerical_result, Z3_list, duration_string)
        else:
            self.result_screen.init_ui_failure(duration_string)
        self.stack.setCurrentIndex(2)
        self.header.go_results()

        self.worker.deleteLater()

if __name__ == "__main__":

    loaded_houses = hhc.load_houses(hhc.HOUSES_FILE_NAME)

    app = QApplication(sys.argv)
    viewer = MainWindow(loaded_houses)
    viewer.show()
    sys.exit(app.exec_())