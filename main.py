import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from vajra.ui.main_window import MainWindow

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Vajra Bi-Bootin")
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()