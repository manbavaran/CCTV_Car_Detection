import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QCursor
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

class VideoWindow(QWidget):
    closed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OBS Camera")
        self.setCursor(QCursor(Qt.ArrowCursor))  # 기본 커서 유지

        self.label = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 약 30fps

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(img))

    def closeEvent(self, event):
        self.closed.emit()  # X버튼
        event.accept()
        
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_Q):
            self.closed.emit()  # ESC, Q키
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VideoWindow()
    win.show()
    sys.exit(app.exec_())
