from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QPushButton, \
    QGraphicsView, QGraphicsItem, QLabel, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem
from PySide2.QtGui import QBrush, QPen, QFont
from PySide2.QtCore import Qt, QRect, QPoint
import sys


class Window(QMainWindow):
    # consts
    graphic_view_width = 840
    graphic_view_height = 440
    # mouse cords
    mouse_cords = QPoint(0, 0)
    start_point_cords = QPoint(0, 0)
    end_point_cords = QPoint(0, 0)

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
        button = QPushButton("Rotate - ", self)
        button.setGeometry(200, 450, 100, 50)
        button.clicked.connect(self.rotate_minus)

        button2 = QPushButton("Rotate + ", self)
        button2.setGeometry(320, 450, 100, 50)
        button2.clicked.connect(self.rotate_plus)

        # labels
        self.mouse_cord_label = QLabel(self)
        self.mouse_cord_label.setGeometry(QRect(950, 440, 100, 50))
        self.mouse_cord_label.setText("(x: {}, y: {})".format(self.mouse_cords.x(), self.mouse_cords.y()))

    def rotate_minus(self):
        self.graphics_view.rotate(-14)

    def rotate_plus(self):
        self.graphics_view.rotate(14)


class GraphicsView(QGraphicsView):
    siema = "sdadsadasd"
    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setup_ui()

        blueBrush = QBrush(Qt.blue)
        blackPen = QPen(Qt.black)
        blackPen.setWidth(5)
        ellipse = self.scene.addEllipse(10, 10, 200, 200, blackPen)
        rect = self.scene.addRect(0, 0, 200, 200, blackPen, blueBrush)
        line = self.scene.addLine(10, 300, 300, 350, blackPen)
        ellipse.setFlag(QGraphicsItem.ItemIsMovable)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

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
        print(self.parent().start_point_cords)
        super(GraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        mouse_cord = event.pos()
        self.parent().end_point_cords = mouse_cord
        print(self.parent().end_point_cords)
        self.draw()
        super(GraphicsView, self).mouseReleaseEvent(event)

    def draw(self):
        print(self.scene)
        #Line(self.scene, self.parent().start_point_cords, self.parent().end_point_cords)
        #Rectangle(self.scene, self.parent().start_point_cords, self.parent().end_point_cords)
        Ellipse(self.scene, self.parent().start_point_cords, self.parent().end_point_cords)


class Line(QGraphicsItem):
    def __init__(self, scene, start_cord, end_cord):
        blackPen = QPen(Qt.black)
        blackPen.setWidth(10)
        self.line = QGraphicsLineItem(start_cord.x(), start_cord.y(), end_cord.x(), end_cord.y())
        self.line.setPen(blackPen)
        self.line.setFlag(QGraphicsItem.ItemIsMovable)
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
            scene.addItem(self.ellipse)

            
app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())
