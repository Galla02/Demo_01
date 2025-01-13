import math
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QFont
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
            pos = touch_point.pos().toPoint()  # 获取触控点的位置
            state = touch_point.state()  # 获取触控点的状态

            if state == Qt.TouchPointPressed:
                self.start_drawing(pos)
            elif state == Qt.TouchPointMoved:
                self.update_drawing(pos)
            elif state == Qt.TouchPointReleased:
                self.end_drawing(pos)

    def start_drawing(self, pos):
        if not self.drawing:
            self.drawing = True
            self.last_point = pos
            self.stroke_pos_x = self.last_point.x()
            self.stroke_pos_y = self.last_point.y()

            self.pen_width = self.min_pen_width
            self.End_pen_width = self.min_pen_width
            self.timer.stop()
            self.prev_point = self.last_point

            self.loop_timer.start(100)

    def update_drawing(self, pos):
        if self.drawing:
            self.loop_function(pos)
            self.pen_width = max(self.min_pen_width, min(self.max_pen_width, self.pen_width + 0.15))
            alpha = max(20, 255 - 255 * (1 - self.pen_width / self.max_pen_width))
            pen_color = self.pen_color
            pen_color.setAlpha(int(alpha))

    def end_drawing(self, pos):
        if self.drawing:
            self.End_pen_width = self.pen_width
            self.following = True
            self.follow_start_time.start()
            self.timer.start(9)

            self.loop_timer.stop()

    def loop_function(self, pos=None):
        if pos is None:
            return

        if not hasattr(self, 'prev_point'):
            self.prev_point = pos
            return

        dx = (pos.x() - self.prev_point.x()) * 0.01
        dy = (pos.y() - self.prev_point.y()) * 0.01

        if (pos.x() - self.prev_point.x()) ** 2 + (pos.y() - self.prev_point.y()) ** 2 >= 15:
            self.pen_width = max(0, self.pen_width - 0.4)

        distance = math.sqrt((self.prev_point.x() - pos.x()) ** 2 + (self.prev_point.y() - pos.y()) ** 2)

        self.speed = distance

        new_y = self.stroke_pos_y + dy + (pos.y() - self.stroke_pos_y) * 0.05
        new_x = self.stroke_pos_x + dx + (pos.x() - self.stroke_pos_x) * 0.05
        self.stroke_pos_x = new_x
        self.stroke_pos_y = new_y

        start_point = QPoint(self.last_point.x(), self.last_point.y())

        self.last_point.setX(int(new_x))
        self.last_point.setY(int(new_y))

        pen_color = self.pen_color
        self.paths.append((start_point, QPoint(int(new_x), int(new_y)), self.pen_width, pen_color))

        self.update_stroke()
        self.prev_point = pos
        self.update()

    def update_stroke(self):
        painter = QPainter(self.background_pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        for start_point, end_point, width, color in self.paths:
            pen = QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(start_point, end_point)
        self.paths.clear()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        painter.drawPixmap(0, 0, self.background_pixmap)

        if not self.drawing:
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont('Arial', 16))
            painter.drawText(10, 30, "按下空格键开始绘制")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec_())
