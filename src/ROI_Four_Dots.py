import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QCursor, QImage, QColor
from PyQt5.QtCore import Qt, QPoint
import os

from roi_io import save_roi

class ROIDrawer(QWidget):
    def __init__(self):
        super().__init__()
        # 화면 최대화
        self.app = QApplication.instance() or QApplication(sys.argv)
        screen = self.app.primaryScreen()
        size = screen.size()
        self.display_w, self.display_h = size.width(), size.height()
        # 실제(가상) 카메라 프레임
        self.frame = self.capture_frame()
        self.orig_h, self.orig_w = self.frame.shape[:2]
        self.display_img = cv2.resize(self.frame, (self.display_w, self.display_h))
        self.qimage = QImage(
            cv2.cvtColor(self.display_img, cv2.COLOR_BGR2RGB).data,
            self.display_w, self.display_h,
            self.display_w * 3,
            QImage.Format_RGB888
        )
        self.setWindowTitle("ROI 설정 (네 점을 클릭)")
        self.setGeometry(0, 0, self.display_w, self.display_h)
        self.setCursor(QCursor(Qt.CrossCursor))
        self.showMaximized()
        self.dots = []
        self.drag_index = None
        self.dot_radius = 14
        self.saved = False
        self.setMouseTracking(True)

    def capture_frame(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.show_message("[ERROR] 카메라 열기 실패! (인덱스: 0)")
            sys.exit(1)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            self.show_message("[ERROR] 카메라 프레임 읽기 실패")
            sys.exit(1)
        return frame

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.qimage)
        for dot in self.dots:
            color = QColor(0, 255, 0) if len(self.dots) == 4 else QColor(220, 60, 60)
            painter.setPen(QPen(color, 2))
            painter.setBrush(color)
            painter.drawEllipse(dot, self.dot_radius, self.dot_radius)
        if len(self.dots) >= 2:
            pen = QPen(QColor(0, 255, 0) if len(self.dots) == 4 else QColor(255, 165, 0), 2, Qt.SolidLine)
            painter.setPen(pen)
            for i in range(len(self.dots) - 1):
                painter.drawLine(self.dots[i], self.dots[i + 1])
            if len(self.dots) == 4:
                painter.drawLine(self.dots[-1], self.dots[0])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            for i, dot in enumerate(self.dots):
                if (event.pos() - dot).manhattanLength() <= self.dot_radius + 3:
                    self.drag_index = i
                    return
            if len(self.dots) >= 4:
                self.show_message("ROI는 최대 4개의 점만 지정 가능합니다.")
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
        elif event.key() == Qt.Key_Escape:
            self.save_points()
            self.close()

    def closeEvent(self, event):
        if not self.saved:
            self.save_points()
        event.accept()

    def save_points(self):
        if len(self.dots) != 4:
            self.show_message("점 4개를 모두 지정해야 저장됩니다.")
            return
        # 표시 좌표 → 원본 프레임 좌표로 역변환
        points = [self.display_to_orig(dot.x(), dot.y()) for dot in self.dots]
        try:
            save_roi(points)
            self.show_message("ROI 좌표를 저장했습니다. (ESC 또는 X로 창을 닫아주세요)")
            self.saved = True
        except Exception as e:
            print(f"[ERROR] save_roi() 예외 발생: {e}")

    def display_to_orig(self, x, y):
        scale_x = self.orig_w / self.display_w
        scale_y = self.orig_h / self.display_h
        return int(x * scale_x), int(y * scale_y)

    def show_message(self, message):
        msg = QMessageBox(self)
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
