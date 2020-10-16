from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QPushButton, \
    QGraphicsView, QGraphicsItem, QLabel
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
        # scene setup
        scene = QGraphicsScene(self)

        # graphics view setup
        self.graphics_view = GraphicsView(scene, self)
        self.graphics_view.setup_view()
        self.graphics_view.setGeometry(200, 10, self.graphic_view_width, self.graphic_view_height)
        self.graphics_view.setSceneRect(0, 0, self.graphic_view_width, self.graphic_view_height)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        blueBrush = QBrush(Qt.blue)
        blackPen = QPen(Qt.black)
        blackPen.setWidth(5)
        ellipse = scene.addEllipse(10, 10, 200, 200, blackPen)
        rect = scene.addRect(0, 0, 200, 200, blackPen, blueBrush)
        ellipse.setFlag(QGraphicsItem.ItemIsMovable)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

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
    def setup_view(self):
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        mouse_cord = event.pos()
        self.parent().mouse_cords = mouse_cord
        self.parent().mouse_cord_label.setText("(x: {}, y: {})".format(self.parent().mouse_cords.x(), self.parent().mouse_cords.y()))
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
        super(GraphicsView, self).mouseReleaseEvent(event)



app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())