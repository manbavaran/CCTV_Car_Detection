import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QCursor, QImage, QColor
from PyQt5.QtCore import Qt, QPoint, pyqtSignal

from roi_io import save_roi

class ROIDrawer(QWidget):
    closed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI 설정 (최대화 + 모든 모니터/비율 완벽 대응)")
        self.setCursor(QCursor(Qt.CrossCursor))
        self.dots = []  # ROI 점들(창 좌표계)
        self.drag_index = None
        self.dot_radius = 14
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
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.qimg = QImage(rgb.data, self.orig_w, self.orig_h, self.orig_w * 3, QImage.Format_RGB888)

        # QImage가 창 중앙에 배치될 실제 위치/크기 저장용
        self.pixmap_rect = (0, 0, self.orig_w, self.orig_h)

        self.showMaximized()
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        widget_w, widget_h = self.width(), self.height()
        scaled_img = self.qimg.scaled(widget_w, widget_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        img_x = (widget_w - scaled_img.width()) // 2
        img_y = (widget_h - scaled_img.height()) // 2
        self.pixmap_rect = (img_x, img_y, scaled_img.width(), scaled_img.height())
        painter.drawImage(img_x, img_y, scaled_img)
        # ROI 점/선 (모두 창 좌표계 기준)
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
        x, y, w, h = self.pixmap_rect
        # QImage 내부만 클릭 가능
        if not (x <= event.x() < x + w and y <= event.y() < y + h):
            return
        # 점 위 클릭 시 드래그 준비
        for i, dot in enumerate(self.dots):
            if (event.pos() - dot).manhattanLength() <= self.dot_radius + 3:
                self.drag_index = i
                return
        # 점 추가
        if len(self.dots) >= 4:
            self.show_message("ROI는 최대 4개 점만 지정할 수 있습니다.\n점은 드래그로 이동 가능.")
            return
        self.dots.append(event.pos())
        self.update()

    def mouseMoveEvent(self, event):
        if self.drag_index is not None:
            x, y, w, h = self.pixmap_rect
            # QImage 내부로 제한
            px = max(x, min(x + w - 1, event.x()))
            py = max(y, min(y + h - 1, event.y()))
            self.dots[self.drag_index] = QPoint(px, py)
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
        elif event.key() in (Qt.Key_Escape, Qt.Key_Q):
            self.closed.emit()  # ESC, Q키
            self.close()

    def closeEvent(self, event):
        self.closed.emit()  # X버튼
        event.accept()

    def save_points(self):
        if len(self.dots) != 4:
            self.show_message("점 4개를 모두 지정해야 저장됩니다.")
            return
        x, y, w, h = self.pixmap_rect
        points = []
        for dot in self.dots:
            # QImage 내부 상대좌표 → 원본 카메라 좌표 환산
            img_x = dot.x() - x
            img_y = dot.y() - y
            orig_x = int(img_x * self.orig_w / w)
            orig_y = int(img_y * self.orig_h / h)
            points.append((orig_x, orig_y))
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
