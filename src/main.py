# main.py
import sys
from PyQt5.QtWidgets import QApplication
from Control_GUI import ControlGUI

def main():
    app = QApplication(sys.argv)
    gui = ControlGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
