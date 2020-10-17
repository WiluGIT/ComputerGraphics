from enum import Enum

from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QPushButton, \
    QGraphicsView, QGraphicsItem, QLabel, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem
from PySide2.QtGui import QBrush, QPen, QFont
from PySide2.QtCore import Qt, QRect, QPoint
import sys


class ToolSelect(Enum):
    Select = 0
    Line = 1
    Rectangle = 2
    Ellipse = 3


class Window(QMainWindow):
    # consts
    graphic_view_width = 840
    graphic_view_height = 440
    # mouse cords
    mouse_cords = QPoint(0, 0)
    start_point_cords = QPoint(0, 0)
    end_point_cords = QPoint(0, 0)
    # selected tool
    selected_tool = ToolSelect.Select.value
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PaintApp")
        self.resize(1200, 800)
        self.setup_ui()
        self.show()
        self.setMouseTracking(True)

    def setup_ui(self):
        # graphics view setup
        self.graphics_view = GraphicsView(self)
        self.graphics_view.setGeometry(200, 10, self.graphic_view_width, self.graphic_view_height)

        # buttons
        select_button = QPushButton("S", self)
        select_button.setGeometry(20, 10, 30, 30)
        select_button.clicked.connect(self.selectItem)

        line_button = QPushButton("L", self)
        line_button.setGeometry(60, 10, 30, 30)
        line_button.clicked.connect(self.drawLine)

        rect_button = QPushButton("R", self)
        rect_button.setGeometry(100, 10, 30, 30)
        rect_button.clicked.connect(self.drawRect)

        ellipse_button = QPushButton("E", self)
        ellipse_button.setGeometry(140, 10, 30, 30)
        ellipse_button.clicked.connect(self.drawEllipse)

        # labels
        self.mouse_cord_label = QLabel(self)
        self.mouse_cord_label.setGeometry(QRect(950, 440, 100, 50))
        self.mouse_cord_label.setText("(x: {}, y: {})".format(self.mouse_cords.x(), self.mouse_cords.y()))

    def drawLine(self):
        self.selected_tool = ToolSelect.Line.value

    def drawRect(self):
        self.selected_tool = ToolSelect.Rectangle.value

    def drawEllipse(self):
        self.selected_tool = ToolSelect.Ellipse.value

    def selectItem(self):
        self.selected_tool = ToolSelect.Select.value


class GraphicsView(QGraphicsView):
    selected_item = None
    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # scene setup
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, self.parent().graphic_view_width, self.parent().graphic_view_height)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        mouse_cord = event.pos()
        self.parent().mouse_cords = mouse_cord
        self.parent().mouse_cord_label.setText(
            "(x: {}, y: {})".format(self.parent().mouse_cords.x(), self.parent().mouse_cords.y()))
        super(GraphicsView, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        mouse_cord = event.pos()
        self.parent().start_point_cords = mouse_cord
        super(GraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        mouse_cord = event.pos()
        self.parent().end_point_cords = mouse_cord
        self.draw()
        super(GraphicsView, self).mouseReleaseEvent(event)

    def draw(self):
        selected_tool = self.parent().selected_tool
        selected_item = self.scene.selectedItems()

        if len(selected_item) == 0:
            if selected_tool == ToolSelect.Select.value:
                pass
            elif selected_tool == ToolSelect.Line.value:
                Line(self.scene, self.parent().start_point_cords, self.parent().end_point_cords)
            elif selected_tool == ToolSelect.Rectangle.value:
                Rectangle(self.scene, self.parent().start_point_cords, self.parent().end_point_cords)
            elif selected_tool == ToolSelect.Ellipse.value:
                Ellipse(self.scene, self.parent().start_point_cords, self.parent().end_point_cords)
            else:
                pass

    def preventMove(self):
        item = self.scene.selectedItems()
        self.selected_item = item
        selected_tool = self.parent().selected_tool
        print(item)
        if len(item) == 1:
            if selected_tool != ToolSelect.Select.value:
                self.selected_item[0].setFlag(QGraphicsItem.ItemIsMovable, False)
                self.selected_item[0].setFlag(QGraphicsItem.ItemIsSelectable, False)
                self.selected_item = None

    def enableMove(self):
        print(self.selected_item)
        if len(self.selected_item) == 1:
            self.selected_item[0].setFlag(QGraphicsItem.ItemIsMovable, True)
            self.selected_item[0].setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.selected_item = None


class Line(QGraphicsItem):
    def __init__(self, scene, start_cord, end_cord):
        blackPen = QPen(Qt.black)
        blackPen.setWidth(10)
        self.line = QGraphicsLineItem(start_cord.x(), start_cord.y(), end_cord.x(), end_cord.y())
        self.line.setPen(blackPen)
        self.line.setFlag(QGraphicsItem.ItemIsMovable)
        self.line.setFlag(QGraphicsItem.ItemIsSelectable)
        scene.addItem(self.line)


class Rectangle(QGraphicsItem):
    def __init__(self, scene, start_cord, end_cord):
        blackPen = QPen(Qt.black)
        blackPen.setWidth(10)
        x1 = start_cord.x()
        y1 = start_cord.y()
        x2 = end_cord.x()
        y2 = end_cord.y()
        width = abs(x1 - x2)
        height = abs(y1 - y2)

        if (x1 <= x2) & (y1 <= y2):
            self.rectangle = QGraphicsRectItem(x1, y1, width, height)
        elif (x1 >= x2) & (y1 <= y2):
            self.rectangle = QGraphicsRectItem(x2, y2 - height, width, height)
        elif (x1 >= x2) & (y1 >= y2):
            self.rectangle = QGraphicsRectItem(x2, y2, width, height)
        elif (x1 <= x2) & (y1 >= y2):
            self.rectangle = QGraphicsRectItem(x1, y1 - height, width, height)

        if self.rectangle is not None:
            self.rectangle.setPen(blackPen)
            self.rectangle.setFlag(QGraphicsItem.ItemIsMovable)
            self.rectangle.setFlag(QGraphicsItem.ItemIsSelectable)
            scene.addItem(self.rectangle)

class Ellipse(QGraphicsItem):
    def __init__(self, scene, start_cord, end_cord):
        blackPen = QPen(Qt.black)
        blackPen.setWidth(10)
        x1 = start_cord.x()
        y1 = start_cord.y()
        x2 = end_cord.x()
        y2 = end_cord.y()
        width = abs(x1 - x2)
        height = abs(y1 - y2)

        if (x1 <= x2) & (y1 <= y2):
            self.ellipse = QGraphicsEllipseItem(x1, y1, width, height)
        elif (x1 >= x2) & (y1 <= y2):
            self.ellipse = QGraphicsEllipseItem(x2, y2 - height, width, height)
        elif (x1 >= x2) & (y1 >= y2):
            self.ellipse = QGraphicsEllipseItem(x2, y2, width, height)
        elif (x1 <= x2) & (y1 >= y2):
            self.ellipse = QGraphicsEllipseItem(x1, y1 - height, width, height)

        if self.ellipse is not None:
            self.ellipse.setPen(blackPen)
            self.ellipse.setFlag(QGraphicsItem.ItemIsMovable)
            self.ellipse.setFlag(QGraphicsItem.ItemIsSelectable)
            scene.addItem(self.ellipse)


app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())
