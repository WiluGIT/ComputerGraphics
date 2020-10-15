from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QPushButton , QGraphicsView, QGraphicsItem
from PySide2.QtGui import QBrush, QPen, QFont
from PySide2.QtCore import Qt
import sys

class Window(QMainWindow):
    graphic_view_width = 840
    graphic_view_height = 440
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PaintApp")
        self.resize(1200, 800)
        self.setup_ui()
        self.show()

    def setup_ui(self):
        # scene setup
        scene = QGraphicsScene(self)

        # graphics view setup
        self.graphics_view = QGraphicsView(scene, self)
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

    def rotate_minus(self):
        self.view.rotate(-14)

    def rotate_plus(self):
        self.view.rotate(14)

    def mouseReleaseEvent(QGraphicsSceneMouseEvent):
        pos = QGrapihcsSceneMouseEvent.lastScenePos()
        self.signalMousePos.emit(pos)

app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())