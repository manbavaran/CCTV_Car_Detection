import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QCursor, QImage, QColor
from PyQt5.QtCore import Qt, QPoint
import numpy as np
import os

from roi_io import save_roi

class ROIDrawer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI 설정 (점 네 개를 클릭하세요)")
        self.setCursor(QCursor(Qt.CrossCursor))
        self.setGeometry(200, 100, 1280, 720)

        try:
            self.image = self.capture_frame()
        except Exception as e:
            print(f"[ERROR] 캡처 프레임 생성 중 예외 발생: {e}")
            input("에러 발생! 엔터를 누르면 창이 닫힙니다.")
            raise

        self.dots = []
        self.drag_index = None
        self.dot_radius = 12
        self.saved = False
        self.setMouseTracking(True)

    def capture_frame(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("[ERROR] 카메라 열기 실패! (인덱스: 0)")
                input("엔터를 누르면 창이 닫힙니다.")
                sys.exit(1)
            ret, frame = cap.read()
            cap.release()
            if not ret:
                print("[ERROR] 카메라에서 프레임을 읽지 못했습니다.")
                input("엔터를 누르면 창이 닫힙니다.")
                sys.exit(1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            return QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        except Exception as e:
            print(f"[ERROR] capture_frame() 예외 발생: {e}")
            input("엔터를 누르면 창이 닫힙니다.")
            sys.exit(1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image.scaled(self.width(), self.height(), Qt.KeepAspectRatio))
        # 점
        for dot in self.dots:
            color = QColor(0, 255, 0) if len(self.dots) == 4 else QColor(220, 60, 60)
            painter.setPen(QPen(color, 2))
            painter.setBrush(color)
            painter.drawEllipse(dot, self.dot_radius, self.dot_radius)
        # 선
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
                self.show_message("ROI는 최대 4개의 점만 지정할 수 있습니다.\n점은 드래그로 이동 가능.")
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
        points = [(dot.x(), dot.y()) for dot in self.dots]
        try:
            save_roi(points)
            self.show_message("ROI 좌표를 저장했습니다. (ESC 또는 X로 창을 닫아주세요)")
            self.saved = True
        except Exception as e:
            print(f"[ERROR] save_roi() 예외 발생: {e}")
            input("엔터를 누르면 창이 닫힙니다.")

    def show_message(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("알림")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = ROIDrawer()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"[ERROR] 메인 루프 예외 발생: {e}")
        input("엔터를 누르면 창이 닫힙니다.")
