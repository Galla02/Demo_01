import math
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor, QPixmap, QFont
from PyQt5.QtCore import Qt, QPoint, QTimer, QTime, QElapsedTimer


class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing App")
        self.setGeometry(100, 100, 800, 600)

        self.End_pen_width = 0
        self.drawing = False
        self.following = False
        self.last_point = QPoint()
        self.stroke_pos_x = 0.0
        self.stroke_pos_y = 0.0
        self.pen_width = 1
        self.max_pen_width = 30  # 最大笔宽
        self.min_pen_width = 1
        self.pen_color = QColor(0, 0, 180)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.follow_mouse)
        self.follow_start_time = QTime()

        self.paths = []  # 用于存储绘制的路径
        self.strokes = []  # 用于存储每个笔画的离屏
        self.current_stroke = QPixmap(self.size())  # 当前笔画的离屏
        self.current_stroke.fill(Qt.transparent)

        self.loop_timer = QTimer(self)
        self.loop_timer.timeout.connect(self.loop_function)

        self.speed = 0

    def follow_mouse(self):
        elapsed = self.follow_start_time.elapsed()
        if self.pen_width == 0:  # 宽度变为0时结束
            self.following = False
            self.timer.stop()
            self.loop_timer.stop()  # 停止循环调用
        else:
            global_pos = QCursor.pos()
            local_pos = self.mapFromGlobal(global_pos)

            self.pen_width = max(0, self.pen_width - 1)

            # 将计算后的浮点数转换为整数
            new_x = int(self.last_point.x() + (local_pos.x() - self.last_point.x()) * 0.1)
            new_y = int(self.last_point.y() + (local_pos.y() - self.last_point.y()) * 0.1)
            start_point = QPoint(self.last_point.x(), self.last_point.y())

            self.last_point.setX(new_x)
            self.last_point.setY(new_y)

            pen_color = self.pen_color
            alpha = max(15, 230 - (min(1, math.log1p(self.speed) / 5) * 255))
            pen_color = self.pen_color
            pen_color.setAlpha(int(alpha))
            self.paths.append((start_point, QPoint(int(new_x), int(new_y)), self.pen_width, pen_color))  # 保存路径
            self.update_stroke()  # 更新当前笔画
            self.update()

    def loop_function(self):
        global_pos = QCursor.pos()
        local_pos = self.mapFromGlobal(global_pos)

        if not hasattr(self, 'prev_point'):
            self.prev_point = local_pos
            return

        dx = (local_pos.x() - self.prev_point.x()) * 0.01
        dy = (local_pos.y() - self.prev_point.y()) * 0.01

        if (local_pos.x() - self.prev_point.x()) ** 2 + (local_pos.y() - self.prev_point.y()) ** 2 >= 15:
            self.pen_width = max(0, self.pen_width - 0.4)

        # 将计算后的浮点数转换为整数
        # new_x = int(self.last_point.x() + dx + (local_pos.x() - self.last_point.x()) * 0.1)
        # new_y = int(self.last_point.y() + dy + (local_pos.y() - self.last_point.y()) * 0.1)

        new_y = self.stroke_pos_y + dy + (local_pos.y() - self.stroke_pos_y) * 0.05
        new_x = self.stroke_pos_x + dx + (local_pos.x() - self.stroke_pos_x) * 0.05
        self.stroke_pos_x = new_x
        self.stroke_pos_y = new_y

        start_point = QPoint(self.last_point.x(), self.last_point.y())

        self.last_point.setX(int(new_x))
        self.last_point.setY(int(new_y))

        pen_color = self.pen_color
        pen_color.setAlpha(int(max(15, 200 - (min(1, math.log1p(self.speed) / 5) * 255))))
        # self.pen_width = min(self.max_pen_width, self.pen_width + 0.15)

        self.paths.append((start_point, QPoint(int(new_x), int(new_y)), self.pen_width, pen_color))

        self.update_stroke()
        self.prev_point = local_pos
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:  # 按下空格键后开始绘制
            self.drawing = not self.drawing

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            # 初始化笔触点位置
            self.last_point = event.pos()  # 将笔触点设为鼠标位置
            self.stroke_pos_x = self.last_point.x()
            self.stroke_pos_y = self.last_point.y()

            self.pen_width = self.min_pen_width
            self.End_pen_width = self.min_pen_width  # 初始笔宽
            self.timer.stop()
            self.prev_point = self.last_point

            self.current_stroke = QPixmap(self.size())  # 创建新的离屏
            self.current_stroke.fill(Qt.transparent)  # 使背景透明

            self.loop_timer.start(100)  # 每100毫秒调用一次速度检测循环

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drawing:
            self.loop_function()  # 调用loop_function更新笔触位置
            self.pen_width = min(self.max_pen_width, self.pen_width + 0.15)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.End_pen_width = self.pen_width
            self.following = True
            self.follow_start_time.start()  # 记录开始跟随的时间
            self.timer.start(9)
            self.strokes.append(self.current_stroke)  #
            self.loop_timer.stop()

    def update_stroke(self):
        painter = QPainter(self.current_stroke)
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

        if not self.drawing:
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont('Arial', 16))
            painter.drawText(10, 30, "按下空格键开始绘制")

        for stroke in self.strokes:
            painter.drawPixmap(0, 0, stroke)

        painter.drawPixmap(0, 0, self.current_stroke)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec_())