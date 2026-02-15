from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QFrame, QMessageBox, QSizePolicy
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("KTS Transport")
        self.showMaximized()  # Open directly in fullscreen
        self.setStyleSheet("background-color: white;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)  # Padding around the edges
        main_layout.setSpacing(40)

        # ----- Header -----
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #e9f7ff; border-radius: 12px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 10, 30, 10)
        header_layout.setSpacing(20)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Truck image
        pixmap = QPixmap("/mnt/data/ac08d48b-6e0c-493e-9266-1753566eb8a3.png")
        pixmap = pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
        truck_label = QLabel()
        truck_label.setPixmap(pixmap)
        header_layout.addWidget(truck_label)

        # Title + Description container
        title_container = QVBoxLayout()
        title_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title_label = QLabel("KTS TRANSPORT")
        title_label.setFont(QFont("Arial Black", 36, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #007BFF;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_container.addWidget(title_label)

        # Description (Address & Phone)
        desc_label = QLabel("134, G NVK COMPLEX, SALEM ROAD, NAMAKKAL - 637001\nPH: 6382447660")
        desc_label.setFont(QFont("Arial", 14))
        desc_label.setStyleSheet("color: #333333;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_container.addWidget(desc_label)

        header_layout.addLayout(title_container)

        main_layout.addWidget(header_frame)

        # ----- Cards Section -----
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(40)

        # Top Row: Driver & Vehicle
        top_row = QHBoxLayout()
        top_row.setSpacing(60)
        top_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(self._make_card("👨‍✈️", "Driver & Vehicle", "Details & Management"))
        top_row.addWidget(self._make_card("🚚", "Vehicle", "Fleet and Vehicle Info"))

        # Bottom Row: Trip & Office
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(60)
        bottom_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_row.addWidget(self._make_card("🗺️", "Trip", "Trip Planning & Tracking"))
        bottom_row.addWidget(self._make_card("🏢", "Office", "Office Operations"))

        # Add rows to layout
        cards_layout.addLayout(top_row)
        cards_layout.addLayout(bottom_row)

        main_layout.addWidget(cards_container)

    def _make_card(self, icon, title, desc):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #e9f2ff;
                border-radius: 12px;
            }
        """)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        frame.setMinimumSize(300, 180)  # Slightly smaller than previous

        vbox = QVBoxLayout(frame)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.setSpacing(10)

        # Icon
        lbl_icon = QLabel(icon)
        lbl_icon.setFont(QFont("Segoe UI Emoji", 48))  # Reduced size
        lbl_icon.setStyleSheet("color: #007BFF;")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(lbl_icon)

        # Title
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))  # Reduced size
        lbl_title.setStyleSheet("color: #003366; background-color: #d8ecff; padding: 6px 16px; border-radius: 10px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(lbl_title)

        # Description
        lbl_desc = QLabel(desc)
        lbl_desc.setFont(QFont("Arial", 13))  # Slightly smaller
        lbl_desc.setStyleSheet("color: #444444;")
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(lbl_desc)

        # Hover & click events
        def enter_event(event):
            frame.setStyleSheet("""
                QFrame {
                    background-color: #d4ecff;
                    border-radius: 12px;
                }
            """)

        def leave_event(event):
            frame.setStyleSheet("""
                QFrame {
                    background-color: #e9f2ff;
                    border-radius: 12px;
                }
            """)

        def click_event(event):
            QMessageBox.information(self, "Navigation", f"{title} clicked.")

        frame.enterEvent = enter_event
        frame.leaveEvent = leave_event
        frame.mousePressEvent = click_event

        return frame


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized() # <-- Do this here, not in __init__
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
