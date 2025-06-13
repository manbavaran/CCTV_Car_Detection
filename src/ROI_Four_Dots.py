import sys
import cv2
import os
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QCursor, QImage, QColor
from PyQt5.QtCore import Qt, QPoint

from roi_io import save_roi

class ROIDrawer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI 설정 (카메라 해상도 기준 네 점을 클릭)")
        self.setCursor(QCursor(Qt.CrossCursor))
        self.dots = []
        self.drag_index = None
        self.dot_radius = 12
        self.saved = False
        self.setMouseTracking(True)

        # 카메라 프레임(원본 해상도) 획득
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.show_message("[ERROR] 카메라 열기 실패! (인덱스: 0)")
            sys.exit(1)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            self.show_message("[ERROR] 카메라 프레임 획득 실패")
            sys.exit(1)
        self.orig_h, self.orig_w = frame.shape[:2]

        # 창 사이즈/이미지도 카메라 원본 해상도로 고정
        self.setGeometry(100, 100, self.orig_w, self.orig_h)
        self.setFixedSize(self.orig_w, self.orig_h)

        # OpenCV 이미지를 PyQt QImage로 변환
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.image = QImage(rgb.data, self.orig_w, self.orig_h, self.orig_w * 3, QImage.Format_RGB888)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)
        # ROI 점
        for dot in self.dots:
            color = QColor(0, 255, 0) if len(self.dots) == 4 else QColor(220, 60, 60)
            painter.setPen(QPen(color, 2))
            painter.setBrush(color)
            painter.drawEllipse(dot, self.dot_radius, self.dot_radius)
        # ROI 선
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
                self.show_message("ROI는 최대 4개 점만 지정할 수 있습니다.\n점은 드래그로 이동 가능.")
                return
            self.dots.append(event.pos())
            self.update()

    def mouseMoveEvent(self, event):
        if self.drag_index is not None:
            # 점을 드래그로 이동
            # 화면 경계 넘어가지 않게 보정
            x = max(0, min(self.orig_w - 1, event.x()))
            y = max(0, min(self.orig_h - 1, event.y()))
            self.dots[self.drag_index] = QPoint(x, y)
            self.update()

    def mouseReleaseEvent(self, event):
        self.drag_index = None

    def keyPressEvent(self, event):
        # Ctrl+Z: 마지막 점 취소
        if event.key() == Qt.Key_Z and (event.modifiers() & Qt.ControlModifier):
            if self.dots:
                self.dots.pop()
                self.update()
        # Ctrl+S: 수동 저장
        elif event.key() == Qt.Key_S and (event.modifiers() & Qt.ControlModifier):
            self.save_points()
        # ESC: 저장 후 종료
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
        # PyQt QPoint → (x, y) 튜플로 변환
        points = [(dot.x(), dot.y()) for dot in self.dots]
        try:
            save_roi(points)
            self.show_message("ROI 좌표를 저장했습니다. (ESC 또는 X로 창을 닫아주세요)")
            self.saved = True
        except Exception as e:
            self.show_message(f"[ERROR] save_roi() 예외 발생: {e}")

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
