import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QCursor, QPixmap, QImage, QColor
from PyQt5.QtCore import Qt, QPoint
import numpy as np
import os

class ROIDrawer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CCTV_Car_Detection - ROI 설정")
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.setWindowFlag(Qt.WindowCloseButtonHint, True)
        self.setGeometry(100, 100, 1280, 720)  # 기본 창 크기

        self.image = self.capture_frame()
        self.dots = []
        self.drag_index = None
        self.dot_radius = 10

        self.setMouseTracking(True)
        self.saved = False

    def capture_frame(self):
        cap = cv2.VideoCapture(1)  # OBS 가상카메라 번호
        ret, frame = cap.read()
        cap.release()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            return QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        else:
            return QImage(1280, 720, QImage.Format_RGB888)  # 빈 이미지

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

        # 점 그리기
        for dot in self.dots:
            color = QColor(139, 0, 0) if len(self.dots) < 4 else QColor(0, 255, 0)
            painter.setPen(QPen(color, 2))
            painter.setBrush(color)
            painter.drawEllipse(dot, self.dot_radius, self.dot_radius)

        # 선 그리기
        if len(self.dots) >= 2:
            pen = QPen(QColor(255, 69, 0) if len(self.dots) < 4 else QColor(0, 255, 0), 2, Qt.DashLine if len(self.dots) < 4 else Qt.SolidLine)
            painter.setPen(pen)
            for i in range(len(self.dots) - 1):
                painter.drawLine(self.dots[i], self.dots[i + 1])
            if len(self.dots) == 4:
                painter.drawLine(self.dots[-1], self.dots[0])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            for i, dot in enumerate(self.dots):
                if (event.pos() - dot).manhattanLength() <= self.dot_radius + 2:
                    self.drag_index = i
                    return
            if len(self.dots) >= 4:
                self.show_message("ROI는 최대 4개의 점만 지정할 수 있습니다.")
                return
            self.dots.append(event.pos())
            self.update()

    def mouseMoveEvent(self, event):
        if self.drag_index is not None:
            self.dots[self.drag_index] = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.drag_index = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Z and (event.modifiers() & Qt.ControlModifier):
            if self.dots:
                self.dots.pop()
                self.update()

        elif event.key() == Qt.Key_S and (event.modifiers() & Qt.ControlModifier):
            self.save_points()
            self.show_message("ROI 좌표를 저장했습니다.")

        elif event.key() == Qt.Key_Escape:
            self.save_points()
            self.close()

    def closeEvent(self, event):
        if not self.saved:
            self.save_points()
        event.accept()

    def save_points(self):
        if not self.dots:
            return
        points = [(dot.x(), dot.y()) for dot in self.dots]
        save_dir = os.path.join("src", "profiles")
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, "roi_points.txt"), "w") as f:
            for x, y in points:
                f.write(f"{x},{y}\n")
        self.saved = True

    def show_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("알림")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ROIDrawer()
    window.show()
    sys.exit(app.exec_())
