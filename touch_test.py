import math
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QPixmap, QFont
from PyQt5.QtCore import Qt, QPoint, QTimer, QTime, QEvent


class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing App")
        self.setGeometry(100, 100, 800, 600)

        self.setAttribute(Qt.WA_AcceptTouchEvents, True)  # 启用触控事件

        self.End_pen_width = 0
        self.drawing = False
        self.following = False
        self.last_point = QPoint()
        self.stroke_pos_x = 0.0
        self.stroke_pos_y = 0.0
        self.pen_width = 5
        self.max_pen_width = 30
        self.min_pen_width = 5
        self.pen_color = QColor(0, 0, 180)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.follow_mouse)
        self.follow_start_time = QTime()

        self.paths = []
        self.background_pixmap = QPixmap(self.size())
        self.background_pixmap.fill(Qt.transparent)

        self.loop_timer = QTimer(self)
        self.loop_timer.timeout.connect(self.loop_function)

        self.speed = 0

    def event(self, event):
        if event.type() == QEvent.TouchBegin or event.type() == QEvent.TouchUpdate or event.type() == QEvent.TouchEnd:
            self.handle_touch_event(event)
            return True
        return super().event(event)

    def handle_touch_event(self, event):
        for touch_point in event.touchPoints():
            pos = touch_point.pos().toPoint()
            state = touch_point.state()

            if state == Qt.TouchPointPressed:
                self.mousePressEvent(pos)
            elif state == Qt.TouchPointMoved:
                self.mouseMoveEvent(pos)
            elif state == Qt.TouchPointReleased:
                self.mouseReleaseEvent(pos)

    def mousePressEvent(self, event):
        if isinstance(event, QMouseEvent):
            pos = event.pos()
        else:
            pos = event

        if self.drawing:
            self.last_point = pos
            self.stroke_pos_x = self.last_point.x()
            self.stroke_pos_y = self.last_point.y()

            self.pen_width = self.min_pen_width
            self.End_pen_width = self.min_pen_width
            self.timer.stop()
            self.prev_point = self.last_point

            self.loop_timer.start(100)

    def mouseMoveEvent(self, event):
        if isinstance(event, QMouseEvent):
            pos = event.pos()
        else:
            pos = event

        if self.drawing:
            self.loop_function()
            self.pen_width = max(self.min_pen_width, min(self.max_pen_width, self.pen_width + 0.15))
            alpha = max(20, 255 - 255 * (1 - self.pen_width / self.max_pen_width))
            pen_color = self.pen_color
            pen_color.setAlpha(int(alpha))

    def mouseReleaseEvent(self, event):
        if isinstance(event, QMouseEvent):
            pos = event.pos()
        else:
            pos = event

        if self.drawing:
            self.End_pen_width = self.pen_width
            self.following = True
            self.follow_start_time.start()
            self.timer.start(9)

            self.loop_timer.stop()

    # 其他方法保持不变...


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec_())
