import os
from enum import Enum

import numpy as np
from PIL import Image
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QPushButton, \
    QGraphicsView, QGraphicsItem, QLabel, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsObject, \
    QButtonGroup, QLineEdit, QLayout, QMessageBox, QComboBox, QStyle, QMenuBar, QMenu, QAction, QStatusBar, QFileDialog, \
    QGraphicsPixmapItem, QDialogButtonBox, QSlider, QDialog
from PySide2.QtGui import QBrush, QPen, QFont, QPainter, QColor, QRegExpValidator, QIcon, QPixmap
from PySide2.QtCore import Qt, QRect, QPoint, Signal, QPointF, QRectF, Slot, QLineF, QSize
from PySide2 import QtCore
import sys


class ToolSelect(Enum):
    Select = 0
    Line = 1
    Rectangle = 2
    Ellipse = 3
    Resize = 4


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
        self.resize(1300, 800)
        self.setup_ui()
        self.show()
        self.setMouseTracking(True)

    def setup_ui(self):
        # menu bar setup
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1300, 1))
        self.menuOpen_File = QMenu(self.menubar)
        self.menuOpen_File.setTitle("File")
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.actionOpen_File = QAction(self)
        self.actionOpen_File.setText("Open File")
        self.actionOpen_File.triggered.connect(self.openFile)
        self.actionSave_File = QAction(self)
        self.actionSave_File.triggered.connect(self.saveFile)
        self.actionSave_File.setText("Save File")
        self.actionNewPaintWindow_File = QAction(self)
        self.actionNewPaintWindow_File.triggered.connect(self.newPaint)
        self.actionNewPaintWindow_File.setText("New Paint Window")
        self.menuOpen_File.addAction(self.actionNewPaintWindow_File)
        self.menuOpen_File.addSeparator()
        self.menuOpen_File.addAction(self.actionOpen_File)
        self.menuOpen_File.addSeparator()
        self.menuOpen_File.addAction(self.actionSave_File)
        self.menubar.addAction(self.menuOpen_File.menuAction())

        # graphics view setup
        self.graphics_view = GraphicsView(self)
        self.graphics_view.setGeometry(200, 50, self.graphic_view_width, self.graphic_view_height)

        # groups and sections
        self.buttonGroup = QButtonGroup()
        self.text_creator_section = []
        self.resizer_text_section = []
        # buttons
        self.select_button = QPushButton(self)
        self.select_button.setGeometry(20, 50, 30, 30)
        self.select_button.clicked.connect(self.selectItem)
        self.select_button.setIcon(QIcon(QPixmap("icons/selection.png")))
        self.buttonGroup.addButton(self.select_button)

        self.line_button = QPushButton(self)
        self.line_button.setGeometry(60, 50, 30, 30)
        self.line_button.clicked.connect(self.drawLine)
        self.line_button.setIcon(QIcon(QPixmap("icons/line.png")))
        self.buttonGroup.addButton(self.line_button)

        self.rect_button = QPushButton(self)
        self.rect_button.setGeometry(100, 50, 30, 30)
        self.rect_button.clicked.connect(self.drawRect)
        self.rect_button.setIcon(QIcon(QPixmap("icons/rectangle.png")))
        self.buttonGroup.addButton(self.rect_button)

        self.ellipse_button = QPushButton(self)
        self.ellipse_button.setGeometry(140, 50, 30, 30)
        self.ellipse_button.clicked.connect(self.drawEllipse)
        self.ellipse_button.setIcon(QIcon(QPixmap("icons/ellipse.png")))
        self.buttonGroup.addButton(self.ellipse_button)

        self.resize_button = QPushButton(self)
        self.resize_button.setGeometry(20, 100, 30, 30)
        self.resize_button.clicked.connect(self.resizeItem)
        self.resize_button.setIcon(QIcon(QPixmap("icons/resize.png")))
        self.buttonGroup.addButton(self.resize_button)

        self.create_shape_button = QPushButton("Create", self)
        self.create_shape_button.setGeometry(1120, 250, 50, 30)
        self.create_shape_button.clicked.connect(self.textDraw)
        self.text_creator_section.append(self.create_shape_button)

        self.update_shape_button = QPushButton("Update", self)
        self.update_shape_button.setGeometry(1120, 130, 50, 30)
        self.update_shape_button.clicked.connect(self.updateShape)
        self.resizer_text_section.append(self.update_shape_button)

        # labels
        self.photo = QLabel(self)
        self.photo.setGeometry(200, 50, self.graphic_view_width, self.graphic_view_height)
        self.photo.setScaledContents(True)
        self.photo.setVisible(False)

        self.mouse_cord_label = QLabel(self)
        self.mouse_cord_label.setGeometry(QRect(950, 480, 100, 50))
        self.mouse_cord_label.setText("(x: {}, y: {})".format(self.mouse_cords.x(), self.mouse_cords.y()))

        self.shape_label = QLabel(self)
        self.shape_label.setGeometry(QRect(1050, 40, 200, 30))
        self.shape_label.setText("")

        self.creator_label = QLabel(self)
        self.creator_label.setGeometry(QRect(1050, 70, 200, 30))
        self.creator_label.setText("Kreator tekstowy")
        self.text_creator_section.append(self.creator_label)

        self.point_start_label = QLabel(self)
        self.point_start_label.setGeometry(QRect(1050, 100, 200, 30))
        self.point_start_label.setText("Punkt startowy:")
        self.text_creator_section.append(self.point_start_label)

        self.point_end_label = QLabel(self)
        self.point_end_label.setGeometry(QRect(1150, 100, 200, 30))
        self.point_end_label.setText("Punkt końcowy:")
        self.text_creator_section.append(self.point_end_label)

        self.width_label = QLabel(self)
        self.width_label.setGeometry(QRect(1050, 70, 200, 30))
        self.width_label.setText("Szerokość:")
        self.resizer_text_section.append(self.width_label)

        self.height_label = QLabel(self)
        self.height_label.setGeometry(QRect(1150, 70, 200, 30))
        self.height_label.setText("Wysokość:")
        self.resizer_text_section.append(self.height_label)

        self.point_start_x1_label = QLabel(self)
        self.point_start_x1_label.setGeometry(QRect(1050, 130, 200, 30))
        self.point_start_x1_label.setText("X1:")
        self.text_creator_section.append(self.point_start_x1_label)

        self.point_start_y1_label = QLabel(self)
        self.point_start_y1_label.setGeometry(QRect(1050, 160, 200, 30))
        self.point_start_y1_label.setText("Y1:")
        self.text_creator_section.append(self.point_start_y1_label)

        self.point_end_x2_label = QLabel(self)
        self.point_end_x2_label.setGeometry(QRect(1150, 130, 200, 30))
        self.point_end_x2_label.setText("X2:")
        self.text_creator_section.append(self.point_end_x2_label)

        self.point_end_y2_label = QLabel(self)
        self.point_end_y2_label.setGeometry(QRect(1150, 160, 200, 30))
        self.point_end_y2_label.setText("Y2:")
        self.text_creator_section.append(self.point_end_y2_label)

        self.size_select_box_label = QLabel("Rozmiar:", self)
        self.size_select_box_label.setGeometry(1050, 200, 50, 30)
        self.text_creator_section.append(self.size_select_box_label)

        self.path_label = QLabel(self)
        self.path_label.setGeometry(200, 500, 780, 16)

        #line edit
        self.point_start_x1_edit = QLineEdit(self)
        self.point_start_x1_edit.setGeometry(QRect(1080, 130, 30, 30))
        self.text_creator_section.append(self.point_start_x1_edit)

        self.point_start_y1_edit = QLineEdit(self)
        self.point_start_y1_edit.setGeometry(QRect(1080, 160, 30, 30))
        self.text_creator_section.append(self.point_start_y1_edit)

        self.point_end_x2_edit = QLineEdit(self)
        self.point_end_x2_edit.setGeometry(QRect(1180, 130, 30, 30))
        self.text_creator_section.append(self.point_end_x2_edit)

        self.point_end_y2_edit = QLineEdit(self)
        self.point_end_y2_edit.setGeometry(QRect(1180, 160, 30, 30))
        self.text_creator_section.append(self.point_end_y2_edit)

        self.width_edit = QLineEdit(self)
        self.width_edit.setGeometry(QRect(1080, 100, 30, 30))
        self.resizer_text_section.append(self.width_edit)

        self.height_edit = QLineEdit(self)
        self.height_edit.setGeometry(QRect(1180, 100, 30, 30))
        self.resizer_text_section.append(self.height_edit)

        # select box
        self.size_select_box = QComboBox(self)
        self.size_select_box.setGeometry(1050, 230, 50, 30)
        self.size_select_box.addItem("1x")
        self.size_select_box.addItem("2x")
        self.size_select_box.addItem("4x")
        self.size_select_box.addItem("6x")
        self.size_select_box.addItem("8x")
        self.size_select_box.currentIndexChanged.connect(self.size_combo_box)
        self.text_creator_section.append(self.size_select_box)

        # regex
        y_regex = QtCore.QRegExp("([0-9]|[1-8][0-9]|9[0-9]|[1-3][0-9]{2}|4[0-3][0-9]|440)")  # value between 0 and 440
        y_validator = QRegExpValidator(y_regex)

        x_regex = QtCore.QRegExp("([0-9]|[1-8][0-9]|9[0-9]|[1-7][0-9]{2}|8[0-3][0-9]|840)")  # value between 0 and 840
        x_validator = QRegExpValidator(x_regex)

        self.point_start_x1_edit.setValidator(x_validator)
        self.point_end_x2_edit.setValidator(x_validator)

        self.point_start_y1_edit.setValidator(y_validator)
        self.point_end_y2_edit.setValidator(y_validator)

        self.height_edit.setValidator(y_validator)
        self.width_edit.setValidator(x_validator)

        # sections visibility
        self.setTextCreatorSectionVisibility(False)
        self.setResizerVisabilitySection(False)

    def openFile(self):
        filter = "AllFiles (*.jpg *jpeg *.png *.bmp *.tiff *tif *ppm);;JPEG (*.jpg *jpeg);;PNG(*.png);;BMP (*.bmp);; TIF (*.tiff *.tif);; PPM (*ppm)"
        file = QFileDialog.getOpenFileName(filter=filter)
        filepath = file[0]
        pixmap = QPixmap(filepath)
        #if filepath.endswith(".ppm"):
        self.openPpmFile(filepath)

        self.photo.setPixmap(pixmap)
        self.path_label.setText(filepath)
        self.setButtonsDisabled(True)
        self.photo.setVisible(True)

    def saveFile(self):
        filter = "JPG (*.jpg);;JPEG (*jpeg);;PNG(*.png);;BMP (*.bmp);; TIF (*.tif);; TIFF(*.tiff)"
        filename = QFileDialog.getSaveFileName(caption="Save Image", directory=os.curdir, filter=filter)

        pixmap = self.photo.pixmap()
        if (filename[1] == "JPG (*.jpg)") or (filename[1] == "JPEG (*jpeg)"):
            returnCode = self.showDialog()
            if returnCode == 1:
                result = pixmap.save(filename[0], None, self.ui.getValue())
        else:
            result = pixmap.save(filename[0])

    def newPaint(self):
        self.photo.setVisible(False)
        self.setButtonsDisabled(False)

    def showDialog(self):
        self.window = QDialog()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.window)
        self.window.show()
        return self.window.exec_()

    def openPpmFile(self, filepath):
        file_string = ""
        with open(filepath) as f:
            for line in f:
                line = line.partition('#')[0]
                line = line.rstrip()
                file_string += line + " "

        # file_data = " ".join(file_string.split()).split(' ')
        #
        # ppm_format = file_data[0]
        # ppm_width = int(file_data[1])
        # ppm_height = int(file_data[2])
        # ppm_values = file_data[4:]
        #
        # result_array = np.zeros(shape=(ppm_height, ppm_width, 3))
        # row_index = 0
        # col_index = 0
        # for j in range(0, len(ppm_values), 3):
        #     result_array[row_index, col_index, 0] = ppm_values[j]
        #     result_array[row_index, col_index, 1] = ppm_values[j + 1]
        #     result_array[row_index, col_index, 2] = ppm_values[j + 2]
        #     col_index += 1
        #     if col_index == ppm_width:
        #         col_index = 0
        #         row_index += 1
        #
        # print(result_array)
        # img_filter = Image.fromarray(result_array.astype('uint8'), 'RGB')
        # img_filter.save("siema.png")

    def drawLine(self):
        self.shape_label.setText("Narzędzie: Linia")
        self.clearButtonsBackground(self.line_button)
        self.selected_tool = ToolSelect.Line.value
        self.graphics_view.scene.clearSelection()
        self.clearResizer()
        self.setTextCreatorSectionVisibility(True)
        self.setResizerVisabilitySection(False)
        self.setMovable(False)

    def drawRect(self):
        self.shape_label.setText("Narzędzie: Prostokąt")
        self.clearButtonsBackground(self.rect_button)
        self.selected_tool = ToolSelect.Rectangle.value
        self.graphics_view.scene.clearSelection()
        self.clearResizer()
        self.setTextCreatorSectionVisibility(True)
        self.setResizerVisabilitySection(False)
        self.setMovable(False)

    def drawEllipse(self):
        self.shape_label.setText("Narzędzie: Elipsa")
        self.clearButtonsBackground(self.ellipse_button)
        self.selected_tool = ToolSelect.Ellipse.value
        self.graphics_view.scene.clearSelection()
        self.clearResizer()
        self.setTextCreatorSectionVisibility(True)
        self.setResizerVisabilitySection(False)
        self.setMovable(False)

    def selectItem(self):
        self.shape_label.setText("Narzędzie: Zaznacz")
        self.clearButtonsBackground(self.select_button)
        self.selected_tool = ToolSelect.Select.value
        self.graphics_view.scene.clearSelection()
        self.clearResizer()
        self.setTextCreatorSectionVisibility(False)
        self.setResizerVisabilitySection(False)
        self.setMovable(True)

    def resizeItem(self):
        self.shape_label.setText("Narzędzie: Zmiana Rozmiaru")
        self.clearButtonsBackground(self.resize_button)
        self.selected_tool = ToolSelect.Resize.value
        self.graphics_view.scene.clearSelection()
        self.clearResizer()
        self.setTextCreatorSectionVisibility(False)
        self.setResizerVisabilitySection(True)
        self.setMovable(True)

    def clearResizer(self):
        for item in self.graphics_view.scene.items():
            obj_type = type(item)
            print(obj_type)
            if obj_type == Resizer or obj_type == QGraphicsPixmapItem:
                continue
            item.resizerVisibilityChange(False)

    def clearButtonsBackground(self, buttonClicked):
        for button in self.buttonGroup.buttons():
            if button == buttonClicked:
                button.setStyleSheet("background-color: red")
            else:
                button.setStyleSheet("background-color: none")

    def setButtonsDisabled(self, disableFlag):
        for button in self.buttonGroup.buttons():
            button.setDisabled(disableFlag)

    def textDraw(self):
        try:
            x1 = int(self.point_start_x1_edit.text())
            y1 = int(self.point_start_y1_edit.text())
            x2 = int(self.point_end_x2_edit.text())
            y2 = int(self.point_end_y2_edit.text())

            if self.selected_tool == ToolSelect.Line.value:
                self.graphics_view.scene.addItem(Line(QLineF(x1, y1, x2, y2), self.graphics_view.scene, self.graphics_view.graphic_Pen))
            elif self.selected_tool == ToolSelect.Rectangle.value:
                self.graphics_view.drawRectangleLogic(x1, y1, x2, y2)
            elif self.selected_tool == ToolSelect.Ellipse.value:
                self.graphics_view.drawEllipseLogic(x1, y1, x2, y2)
            elif self.selected_tool == ToolSelect.Resize.value:
                self.updateShape(x1, y1, x2, y2, self.graphics_view.selected_item)
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Not all points have value")
            msg.setWindowTitle("Warning!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def updateShape(self):
        try:
            if type(self.graphics_view.selected_item) == Line:
                self.graphics_view.selected_item.resizeLineText(int(self.width_edit.text()))
            else:
                self.graphics_view.selected_item.resizeRectText(int(self.width_edit.text()), int(self.height_edit.text()))
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Width/Height can't be empty")
            msg.setWindowTitle("Warning!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def setTextCreatorSectionVisibility(self, visible_flag):
        for item in self.text_creator_section:
            item.setVisible(visible_flag)

    def setResizerVisabilitySection(self, visible_flag):
        for item in self.resizer_text_section:
            item.setVisible(visible_flag)

    def setMovable(self, moveFlag):
        items = self.graphics_view.scene.items()
        if items:
            for item in items:
                if type(item) is not Resizer:
                    if self.selected_tool == ToolSelect.Resize.value:
                        item.setFlag(QGraphicsItem.ItemIsSelectable, moveFlag)
                        item.setFlag(QGraphicsItem.ItemSendsGeometryChanges, moveFlag)
                        item.setFlag(QGraphicsItem.ItemIsFocusable, moveFlag)
                        item.setFlag(QGraphicsItem.ItemIsMovable, not moveFlag)
                    else:
                        item.setFlag(QGraphicsItem.ItemIsMovable, moveFlag)
                        item.setFlag(QGraphicsItem.ItemIsSelectable, moveFlag)
                        item.setFlag(QGraphicsItem.ItemIsFocusable, moveFlag)
                        item.setFlag(QGraphicsItem.ItemSendsGeometryChanges, moveFlag)

    def size_combo_box(self):
        size = self.size_select_box.currentIndex()

        if size == 0:
            self.graphics_view.graphic_Pen.setWidth(1)
        elif size == 1:
            self.graphics_view.graphic_Pen.setWidth(2)
        elif size == 2:
            self.graphics_view.graphic_Pen.setWidth(4)
        elif size == 3:
            self.graphics_view.graphic_Pen.setWidth(6)
        elif size == 4:
            self.graphics_view.graphic_Pen.setWidth(8)


class GraphicsView(QGraphicsView):
    selected_item = None
    graphic_Pen = QPen(Qt.black)
    graphic_Pen.setWidth(1)
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
        self.scene.selectionChanged.connect(self.selectionChanged)

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
                self.drawLineLogic()
            elif selected_tool == ToolSelect.Rectangle.value:
                self.drawRectangleLogic()
            elif selected_tool == ToolSelect.Ellipse.value:
                self.drawEllipseLogic()
            else:
                pass

    def selectionChanged(self):
        selectedItems = self.scene.selectedItems()
        selected_tool = self.parent().selected_tool

        if (len(selectedItems) == 1) & (selected_tool == ToolSelect.Resize.value):
            obj_type = type(selectedItems[0])
            if obj_type is not Resizer:
                self.setLineLengthControl(False)

            if (obj_type == Rectangle) | (obj_type == Line) | (obj_type == Ellipse):
                self.selected_item = selectedItems[0]
                self.selected_item.resizerVisibilityChange(True)
                self.selected_item.populateTextCreator(self)

                if obj_type == Line:
                    self.setLineLengthControl(True)

    def setLineLengthControl(self, setFlag):
        if setFlag:
            self.parent().height_edit.setDisabled(True)
            self.parent().width_label.setText("Długość:")
        else:
            self.parent().height_edit.setDisabled(False)
            self.parent().width_label.setText("Szerokość:")

    def drawRectangleLogic(self, x1=None, y1=None, x2=None, y2=None):
        if (x1 is None) | (y1 is None) | (x2 is None) | (y2 is None):
            x1 = self.parent().start_point_cords.x()
            y1 = self.parent().start_point_cords.y()
            x2 = self.parent().end_point_cords.x()
            y2 = self.parent().end_point_cords.y()
        width = abs(x1 - x2)
        height = abs(y1 - y2)

        if (x1 <= x2) & (y1 <= y2):
            self.scene.addItem(Rectangle(QRectF(x1, y1, width, height), self.scene, self.graphic_Pen))
        elif (x1 >= x2) & (y1 <= y2):
            self.scene.addItem(Rectangle(QRectF(x2, y2 - height, width, height), self.scene, self.graphic_Pen))
        elif (x1 >= x2) & (y1 >= y2):
            self.scene.addItem(Rectangle(QRectF(x2, y2, width, height), self.scene, self.graphic_Pen))
        elif (x1 <= x2) & (y1 >= y2):
            self.scene.addItem(Rectangle(QRectF(x1, y1 - height, width, height), self.scene, self.graphic_Pen))

    def drawEllipseLogic(self, x1=None, y1=None, x2=None, y2=None):
        if (x1 is None) | (y1 is None) | (x2 is None) | (y2 is None):
            x1 = self.parent().start_point_cords.x()
            y1 = self.parent().start_point_cords.y()
            x2 = self.parent().end_point_cords.x()
            y2 = self.parent().end_point_cords.y()
        width = abs(x1 - x2)
        height = abs(y1 - y2)

        if (x1 <= x2) & (y1 <= y2):
            self.scene.addItem(Ellipse(QRectF(x1, y1, width, height), self.scene, self.graphic_Pen))
        elif (x1 >= x2) & (y1 <= y2):
            self.scene.addItem(Ellipse(QRectF(x2, y2 - height, width, height), self.scene, self.graphic_Pen))
        elif (x1 >= x2) & (y1 >= y2):
            self.scene.addItem(Ellipse(QRectF(x2, y2, width, height), self.scene, self.graphic_Pen))
        elif (x1 <= x2) & (y1 >= y2):
            self.scene.addItem(Ellipse(QRectF(x1, y1 - height, width, height), self.scene, self.graphic_Pen))

    def drawLineLogic(self):
        x1 = self.parent().start_point_cords.x()
        y1 = self.parent().start_point_cords.y()
        x2 = self.parent().end_point_cords.x()
        y2 = self.parent().end_point_cords.y()

        line = Line(QLineF(x1, y1, x2, y2), self.scene, self.graphic_Pen)
        self.scene.addItem(line)


class Line(QGraphicsLineItem):
    def __init__(self, line=QLineF(0, 0, 100, 100), scene=None, pen=QPen(), parent=None):
        super().__init__(line, parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, False)
        self.setPen(pen)

        self.resizer = Resizer(parent=self)
        resizerWidth = self.resizer.rect.width() / 2
        resizerOffset = QPointF(resizerWidth, resizerWidth)
        self.resizer.setPos(self.line().p2() - resizerOffset)
        self.resizer.setVisible(False)
        self.resizer.resizeSignal.connect(self.resizeLine)

    @QtCore.Slot(QGraphicsObject)
    def resizeLine(self, change):
        self.setLine(self.line().x1(), self.line().y1(), self.line().x2() + change.x(), self.line().y2() + change.y())
        self.prepareGeometryChange()
        self.update()

    def resizerVisibilityChange(self, visibleFlag):
        self.resizer.setVisible(visibleFlag)

    def populateTextCreator(self, graphicView):
        graphicView.parent().width_edit.setText(str(int(self.line().length())))

    def resizeLineText(self, length):
        line = self.line()
        line.setLength(length)
        self.setLine(line)
        resizerWidth = self.resizer.rect.width() / 2
        resizerOffset = QPointF(resizerWidth, resizerWidth)
        self.resizer.setPos(self.line().p2() - resizerOffset)


class Rectangle(QGraphicsRectItem):
    def __init__(self, rect=QRectF(), scene=None, pen=QPen(), parent=None):
        super().__init__(rect, parent)

        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, False)
        self.setPen(pen)

        self.resizer = Resizer(parent=self)
        resizerWidth = self.resizer.rect.width() / 2
        resizerOffset = QPointF(resizerWidth, resizerWidth)
        self.resizer.setPos(self.rect().bottomRight() - resizerOffset)
        self.resizer.setVisible(False)
        self.resizer.resizeSignal.connect(self.resizeRec)

    @QtCore.Slot(QGraphicsObject)
    def resizeRec(self, change):
        self.setRect(self.rect().adjusted(0, 0, change.x(), change.y()))
        self.prepareGeometryChange()
        self.update()

    def resizerVisibilityChange(self, visibleFlag):
        self.resizer.setVisible(visibleFlag)

    def populateTextCreator(self, graphicView):
        graphicView.parent().width_edit.setText(str(int(self.rect().width())))
        graphicView.parent().height_edit.setText(str(int(self.rect().height())))

    def resizeRectText(self, width, height):
        rect = self.rect()
        rect.setWidth(width)
        rect.setHeight(height)
        self.setRect(rect)
        resizerWidth = self.resizer.rect.width() / 2
        resizerOffset = QPointF(resizerWidth, resizerWidth)
        self.resizer.setPos(self.rect().bottomRight() - resizerOffset)


class Ellipse(QGraphicsEllipseItem):
    def __init__(self, rect=QRectF(), scene=None, pen=QPen(), parent=None):
        super().__init__(rect, parent)

        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, False)
        self.setPen(pen)

        self.resizer = Resizer(parent=self)
        resizerWidth = self.resizer.rect.width() / 2
        resizerOffset = QPointF(resizerWidth, resizerWidth)
        self.resizer.setPos(self.rect().bottomRight() - resizerOffset)
        self.resizer.setVisible(False)
        self.resizer.resizeSignal.connect(self.resizeRec)

    @QtCore.Slot(QGraphicsObject)
    def resizeRec(self, change):
        self.setRect(self.rect().adjusted(0, 0, change.x(), change.y()))
        self.prepareGeometryChange()
        self.update()

    def resizerVisibilityChange(self, visibleFlag):
        self.resizer.setVisible(visibleFlag)

    def populateTextCreator(self, graphicView):
        graphicView.parent().width_edit.setText(str(int(self.rect().width())))
        graphicView.parent().height_edit.setText(str(int(self.rect().height())))

    def resizeRectText(self, width, height):
        rect = self.rect()
        rect.setWidth(width)
        rect.setHeight(height)
        self.setRect(rect)
        resizerWidth = self.resizer.rect.width() / 2
        resizerOffset = QPointF(resizerWidth, resizerWidth)
        self.resizer.setPos(self.rect().bottomRight() - resizerOffset)


class Resizer(QGraphicsObject):
    resizeSignal = QtCore.Signal(QPointF)

    def __init__(self, rect=QRectF(0, 0, 10, 10), parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.rect = rect

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(QColor(255, 0, 0, 255)))
            painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawEllipse(self.rect)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            if self.isSelected():
                self.resizeSignal.emit(value - self.pos())
        return value

class Ui_Dialog(QDialog):
    def setupUi(self, Dialog):
        Dialog.resize(400, 200)
        font = QFont()
        font.setPointSize(23)

        self.value = 80

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 160, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.quality_label = QLabel("Quality:", Dialog)
        self.quality_label.setGeometry(QtCore.QRect(20, 30, 366, 41))
        self.quality_label.setFont(font)

        self.startValue = QLabel("0", Dialog)
        self.startValue.setGeometry(QtCore.QRect(10, 90, 42, 61))
        self.startValue.setFont(font)

        self.endValue = QLabel("80", Dialog)
        self.endValue.setGeometry(QtCore.QRect(350, 90, 41, 51))
        self.endValue.setFont(font)

        self.horizontalSlider = QSlider(Dialog)
        self.horizontalSlider.setGeometry(QtCore.QRect(50, 100, 271, 41))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.valueChanged.connect(self.sliderValueChange)
        self.horizontalSlider.setValue(self.value)

        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def sliderValueChange(self):
        self.value = self.horizontalSlider.value()
        self.endValue.setText(str(self.value))

    def getValue(self):
        return self.value


app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())
