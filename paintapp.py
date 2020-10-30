import math
import os
from enum import Enum

import numpy as np
from PIL import Image
import cv2
#from scipy.misc
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QPushButton, \
    QGraphicsView, QGraphicsItem, QLabel, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsObject, \
    QButtonGroup, QLineEdit, QLayout, QMessageBox, QComboBox, QStyle, QMenuBar, QMenu, QAction, QStatusBar, QFileDialog, \
    QGraphicsPixmapItem, QDialogButtonBox, QSlider, QDialog, QSpinBox, QAbstractSlider
from PySide2.QtGui import QBrush, QPen, QFont, QPainter, QColor, QRegExpValidator, QIcon, QPixmap, QImage
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

        self.set_color_button = QPushButton("Select color", self)
        self.set_color_button.setGeometry(QtCore.QRect(70, 180, 80, 20))
        self.set_color_button.clicked.connect(self.select_color_window)

        # labels
        self.photo = QLabel(self)
        self.photo.setGeometry(200, 50, self.graphic_view_width, self.graphic_view_height)
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

        self.colorLabel = QLabel(self)
        self.colorLabel.setGeometry(QtCore.QRect(20, 180, 40, 40))
        self.colorLabel.setStyleSheet("QLabel { background-color: black}")


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

    def select_color_window(self):
        self.window = QDialog()
        self.ui = Color_Dialog()
        self.ui.setupUi(self.window)
        self.window.show()

        if self.window.exec_() == 1:
            self.colorLabel.setStyleSheet("QLabel{{ background-color: rgb({},{},{});}}".format(self.ui.rSpin.value(), self.ui.gSpin.value(),
                                                                               self.ui.bSpin.value()))
            self.graphics_view.graphic_Pen = QPen(QColor(self.ui.rSpin.value(), self.ui.gSpin.value(),
                                                                               self.ui.bSpin.value()))


    def openFile(self):
        filter = "AllFiles (*.jpg *jpeg *.png *.bmp *.tiff *tif *ppm);;JPEG (*.jpg *jpeg);;PNG(*.png);;BMP (*.bmp);; TIF (*.tiff *.tif);; PPM (*ppm)"
        file = QFileDialog.getOpenFileName(filter=filter)
        filepath = file[0]

        if filepath.endswith(".ppm"):
            self.openPpmFile(filepath)
        else:
            self.setPhotoFromPath(filepath)

    def saveFile(self):
        filter = "JPG (*.jpg);;JPEG (*jpeg);;PNG(*.png);;BMP (*.bmp);; TIF (*.tif);; TIFF(*.tiff)"
        filename = QFileDialog.getSaveFileName(caption="Save Image", directory=os.curdir, filter=filter)

        #pixmap = self.photo.pixmap()
        pixmap = QPixmap(self.path_label.text())
        if (filename[1] == "JPG (*.jpg)") or (filename[1] == "JPEG (*jpeg)"):
            returnCode = self.showDialog()
            if returnCode == 1:
                result = pixmap.save(filename[0], None, self.ui.getValue())
        else:
            result = pixmap.save(filename[0])

    def setPhotoFromPath(self, filepath):
        image = QImage(filepath)
        scaledImg = image.scaled(840, 440, Qt.IgnoreAspectRatio)
        pixmap = QPixmap(scaledImg)
        self.photo.setPixmap(pixmap)
        self.path_label.setText(filepath)
        self.setButtonsDisabled(True)
        self.photo.setVisible(True)

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
        try:
            data = []
            ppm_params_dict = {}
            with open(filepath, errors="ignore") as f:
                file_pos = 0
                for line in f:
                    file_pos += len(line)
                    line = line.partition('#')[0]
                    line = line.rstrip().split()
                    if line == "":
                        continue
                    data += line
                    if len(data) >= 4:
                        break

                ppm_params_dict["ppm_format"] = data[0]
                ppm_params_dict["ppm_width"] = int(data[1])
                ppm_params_dict["ppm_height"] = int(data[2])
                ppm_params_dict["ppm_max"] = int(data[3])

                channel_type = np.uint16
                max_value = 65535
                if ppm_params_dict["ppm_max"] < 256:
                    channel_type = np.uint8
                    max_value = 255

                result_array = np.zeros(shape=(ppm_params_dict["ppm_height"], ppm_params_dict["ppm_width"], 3))
                pixel_count = 0
                if ppm_params_dict["ppm_format"] == 'P3':
                    if len(data) > 4:
                        data = data[4:]
                    else:
                        data = []
                    row_index = 0
                    col_index = 0
                    if (ppm_params_dict["ppm_max"] < 255) or (65535 > ppm_params_dict["ppm_max"] > 255):
                        for line in f:
                            line = line.partition('#')[0]
                            line = line.rstrip().split()
                            data += line
                            if len(data) == ppm_params_dict["ppm_width"] * 3:
                                for j in range(0, len(data), 3):
                                    result_array[row_index, col_index, 0] = int(
                                        self.scaleBetween(int(data[j + 2]), 0, max_value, 0,
                                                          ppm_params_dict["ppm_max"]))  # B
                                    result_array[row_index, col_index, 1] = int(
                                        self.scaleBetween(int(data[j + 1]), 0, max_value, 0,
                                                          ppm_params_dict["ppm_max"]))  # G
                                    result_array[row_index, col_index, 2] = int(
                                        self.scaleBetween(int(data[j]), 0, max_value, 0,
                                                          ppm_params_dict["ppm_max"]))  # R
                                    col_index += 1
                                    if col_index == ppm_params_dict["ppm_width"]:
                                        col_index = 0
                                        row_index += 1
                                        pixel_count += len(data)
                                        data = []
                                        break
                    else:
                        for line in f:
                            line = line.partition('#')[0]
                            line = line.rstrip().split()
                            data += line
                            if len(data) == ppm_params_dict["ppm_width"] * 3:
                                for j in range(0, len(data), 3):
                                    result_array[row_index, col_index, 0] = int(data[j + 2])  # B
                                    result_array[row_index, col_index, 1] = int(data[j + 1])  # G
                                    result_array[row_index, col_index, 2] = int(data[j])  # R
                                    col_index += 1
                                    if col_index == ppm_params_dict["ppm_width"]:
                                        col_index = 0
                                        row_index += 1
                                        pixel_count += len(data)
                                        data = []
                                        break

                elif ppm_params_dict["ppm_format"] == 'P6':
                    f.close()
                    data = []
                    row_index = 0
                    col_index = 0
                    with open(filepath, "rb") as f:
                        f.seek(file_pos)
                        if (ppm_params_dict["ppm_max"] < 255) or (65535 > ppm_params_dict["ppm_max"] > 255):
                            while True:
                                byte = f.read(1)
                                if not byte:
                                    break
                                data.append(ord(byte))
                                if len(data) == ppm_params_dict["ppm_width"] * 3:
                                    for j in range(0, len(data), 3):
                                        result_array[row_index, col_index, 0] = int(
                                            self.scaleBetween(int(data[j + 2]), 0, max_value, 0,
                                                              ppm_params_dict["ppm_max"]))  # B
                                        result_array[row_index, col_index, 1] = int(
                                            self.scaleBetween(int(data[j + 1]), 0, max_value, 0,
                                                              ppm_params_dict["ppm_max"]))  # G
                                        result_array[row_index, col_index, 2] = int(
                                            self.scaleBetween(int(data[j]), 0, max_value, 0,
                                                              ppm_params_dict["ppm_max"]))  # R
                                        col_index += 1
                                        if col_index == ppm_params_dict["ppm_width"]:
                                            col_index = 0
                                            row_index += 1
                                            pixel_count += len(data)
                                            data = []
                                            break
                        else:
                            while True:
                                byte = f.read(1)
                                if not byte:
                                    break
                                data.append(ord(byte))
                                if len(data) == ppm_params_dict["ppm_width"] * 3:
                                    for j in range(0, len(data), 3):
                                        result_array[row_index, col_index, 0] = int(data[j + 2])  # B
                                        result_array[row_index, col_index, 1] = int(data[j + 1])  # G
                                        result_array[row_index, col_index, 2] = int(data[j])  # R
                                        col_index += 1
                                        if col_index == ppm_params_dict["ppm_width"]:
                                            col_index = 0
                                            row_index += 1
                                            pixel_count += len(data)
                                            data = []
                                            break
                else:
                    raise Exception("File must have P3/P6 PPM format")

                proper_values_count = ppm_params_dict["ppm_width"] * ppm_params_dict["ppm_height"] * 3
                if pixel_count != proper_values_count:
                    raise Exception("File has wrong count of pixel values")

            path = "out/ppm3_out.png"
            cv2.imwrite(path, result_array.astype(channel_type))
            self.setPhotoFromPath(path)
        except Exception as error:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(str(error))
            msg.setWindowTitle("Warning!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def scaleBetween(self, unscaledNum, minAllowed, maxAllowed, min, max):
        return (maxAllowed - minAllowed) * (unscaledNum - min) / (max - min) + minAllowed

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

class Color_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.resize(537, 287)
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)

        self.ok = QPushButton("OK", Dialog)
        self.ok.setAutoDefault(False)
        self.cancel = QPushButton("Cancel", Dialog)
        self.cancel.setAutoDefault(False)
        self.ok.setGeometry(400, 240, 50, 30)
        self.cancel.setGeometry(460, 240, 50, 30)
        self.ok.clicked.connect(Dialog.accept)
        self.cancel.clicked.connect(Dialog.reject)
        # self.buttonBox.accepted.connect(Dialog.accept)
        # self.buttonBox.rejected.connect(Dialog.reject)
        # self.buttonBox = QDialogButtonBox(Dialog)
        # self.buttonBox.setGeometry(QtCore.QRect(280, 240, 171, 32))
        # self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        # self.buttonBox.setStandardButtons(cancel|ok)
        # self.buttonBox.setObjectName("buttonBox")

        self.cSlider = QSlider(Dialog)
        self.cSlider.setGeometry(QtCore.QRect(50, 20, 160, 22))
        self.cSlider.setOrientation(QtCore.Qt.Horizontal)
        self.cSlider.setMaximum(100)
        self.cSlider.actionTriggered.connect(self.cSliderValueChange)

        self.mSlider = QSlider(Dialog)
        self.mSlider.setGeometry(QtCore.QRect(50, 60, 160, 22))
        self.mSlider.setOrientation(QtCore.Qt.Horizontal)
        self.mSlider.setMaximum(100)
        self.mSlider.actionTriggered.connect(self.mSliderValueChange)

        self.ySlider = QSlider(Dialog)
        self.ySlider.setGeometry(QtCore.QRect(50, 100, 160, 22))
        self.ySlider.setOrientation(QtCore.Qt.Horizontal)
        self.ySlider.setMaximum(100)
        self.ySlider.actionTriggered.connect(self.ySliderValueChange)

        self.kSlider = QSlider(Dialog)
        self.kSlider.setGeometry(QtCore.QRect(50, 140, 160, 22))
        self.kSlider.setOrientation(QtCore.Qt.Horizontal)
        self.kSlider.setMaximum(100)
        self.kSlider.actionTriggered.connect(self.kSliderValueChange)

        self.c_label = QLabel("C", Dialog)
        self.c_label.setGeometry(QtCore.QRect(10, 10, 21, 31))
        self.c_label.setFont(font)

        self.m_label = QLabel("M", Dialog)
        self.m_label.setGeometry(QtCore.QRect(10, 50, 21, 31))
        self.m_label.setFont(font)

        self.y_label = QLabel("Y", Dialog)
        self.y_label.setGeometry(QtCore.QRect(10, 90, 21, 31))
        self.y_label.setFont(font)

        self.k_label = QLabel("K", Dialog)
        self.k_label.setGeometry(QtCore.QRect(10, 130, 21, 31))
        self.k_label.setFont(font)

        self.r_label = QLabel("R", Dialog)
        self.r_label.setGeometry(QtCore.QRect(270, 10, 21, 31))
        self.r_label.setFont(font)

        self.g_label = QLabel("G", Dialog)
        self.g_label.setGeometry(QtCore.QRect(270, 50, 21, 31))
        self.g_label.setFont(font)

        self.b_label = QLabel("B", Dialog)
        self.b_label.setGeometry(QtCore.QRect(270, 90, 21, 31))
        self.b_label.setFont(font)

        self.rSlider = QSlider(Dialog)
        self.rSlider.setGeometry(QtCore.QRect(300, 20, 160, 22))
        self.rSlider.setOrientation(QtCore.Qt.Horizontal)
        self.rSlider.setMaximum(255)
        self.rSlider.actionTriggered.connect(self.rSliderValueChange)

        self.gSlider = QSlider(Dialog)
        self.gSlider.setGeometry(QtCore.QRect(300, 60, 160, 22))
        self.gSlider.setOrientation(QtCore.Qt.Horizontal)
        self.gSlider.setMaximum(255)
        self.gSlider.actionTriggered.connect(self.gSliderValueChange)

        self.bSlider = QSlider(Dialog)
        self.bSlider.setGeometry(QtCore.QRect(300, 100, 160, 22))
        self.bSlider.setOrientation(QtCore.Qt.Horizontal)
        self.bSlider.setMaximum(255)
        self.bSlider.actionTriggered.connect(self.bSliderValueChange)

        self.color_value_label = QLabel(Dialog)
        self.color_value_label.setGeometry(QtCore.QRect(10, 210, 451, 20))

        self.color_label = QLabel("Color:", Dialog)
        self.color_label.setGeometry(QtCore.QRect(10, 180, 50, 13))
        font.setPointSize(10)
        self.color_label.setFont(font)

        self.cSpin = QSpinBox(Dialog)
        self.cSpin.setGeometry(QtCore.QRect(220, 20, 42, 22))
        self.cSpin.setMaximum(100)
        self.cSpin.valueChanged.connect(self.cSpinValueChange)
        self.cSpin.editingFinished.connect(self.convertCMYKtoRGB)

        self.mSpin = QSpinBox(Dialog)
        self.mSpin.setGeometry(QtCore.QRect(220, 60, 42, 22))
        self.mSpin.setMaximum(100)
        self.mSpin.valueChanged.connect(self.mSpinValueChange)
        self.mSpin.editingFinished.connect(self.convertCMYKtoRGB)

        self.ySpin = QSpinBox(Dialog)
        self.ySpin.setGeometry(QtCore.QRect(220, 100, 42, 22))
        self.ySpin.setMaximum(100)
        self.ySpin.valueChanged.connect(self.ySpinValueChange)
        self.ySpin.editingFinished.connect(self.convertCMYKtoRGB)

        self.kSpin = QSpinBox(Dialog)
        self.kSpin.setGeometry(QtCore.QRect(220, 140, 42, 22))
        self.kSpin.setMaximum(100)
        self.kSpin.valueChanged.connect(self.kSpinValueChange)
        self.kSpin.editingFinished.connect(self.convertCMYKtoRGB)

        self.rSpin = QSpinBox(Dialog)
        self.rSpin.setGeometry(QtCore.QRect(480, 20, 42, 22))
        self.rSpin.setMaximum(255)
        self.rSpin.valueChanged.connect(self.rSpinValueChange)
        self.rSpin.editingFinished.connect(self.convertRGBtoCMYK)

        self.gSpin = QSpinBox(Dialog)
        self.gSpin.setGeometry(QtCore.QRect(480, 60, 42, 22))
        self.gSpin.setMaximum(255)
        self.gSpin.valueChanged.connect(self.gSpinValueChange)
        self.gSpin.editingFinished.connect(self.convertRGBtoCMYK)

        self.bSpin = QSpinBox(Dialog)
        self.bSpin.setGeometry(QtCore.QRect(480, 100, 42, 22))
        self.bSpin.setMaximum(255)
        self.bSpin.valueChanged.connect(self.bSpinValueChange)
        self.bSpin.editingFinished.connect(self.convertRGBtoCMYK)

        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.convertCMYKtoRGB()


    def cSliderValueChange(self):
        value = self.cSlider.value()
        self.cSpin.setValue(value)
        self.convertCMYKtoRGB()


    def mSliderValueChange(self):
        value = self.mSlider.value()
        self.mSpin.setValue(value)
        self.convertCMYKtoRGB()

    def ySliderValueChange(self):
        value = self.ySlider.value()
        self.ySpin.setValue(value)
        self.convertCMYKtoRGB()

    def kSliderValueChange(self):
        value = self.kSlider.value()
        self.kSpin.setValue(value)
        self.convertCMYKtoRGB()

    def rSliderValueChange(self):
        value = self.rSlider.value()
        self.rSpin.setValue(value)
        self.convertRGBtoCMYK()

    def gSliderValueChange(self):
        value = self.gSlider.value()
        self.gSpin.setValue(value)
        self.convertRGBtoCMYK()

    def bSliderValueChange(self):
        value = self.bSlider.value()
        self.bSpin.setValue(value)
        self.convertRGBtoCMYK()

    def cSpinValueChange(self):
        value = self.cSpin.value()
        self.cSlider.setValue(value)

    def mSpinValueChange(self):
        value = self.mSpin.value()
        self.mSlider.setValue(value)

    def ySpinValueChange(self):
        value = self.ySpin.value()
        self.ySlider.setValue(value)

    def kSpinValueChange(self):
        value = self.kSpin.value()
        self.kSlider.setValue(value)

    def rSpinValueChange(self):
        value = self.rSpin.value()
        self.rSlider.setValue(value)

    def gSpinValueChange(self):
        value = self.gSpin.value()
        self.gSlider.setValue(value)

    def bSpinValueChange(self):
        value = self.bSpin.value()
        self.bSlider.setValue(value)

    def convertRGBtoCMYK(self):
        try:
            red = self.rSpin.value() / 255
            green = self.gSpin.value() / 255
            blue = self.bSpin.value() / 255
            black = min(1 - red, 1 - green, 1 - blue)
            cyan = (1 - red - black) / (1 - black)
            magenta = (1 - green - black) / (1 - black)
            yellow = (1 - blue - black) / (1 - black)

            self.cSpin.setValue(round(cyan * 100))
            self.mSpin.setValue(round(magenta * 100))
            self.ySpin.setValue(round(yellow * 100))
            self.kSpin.setValue(round(black * 100))
            color_label = "QLabel{{ background-color: rgb({},{},{});}}".format(self.rSpin.value(), self.gSpin.value(),
                                                                           self.bSpin.value())
            self.color_value_label.setStyleSheet(color_label)

        except ZeroDivisionError:
            pass

    def convertCMYKtoRGB(self):
        try:
            cyan = self.cSpin.value() / 100
            magenta = self.mSpin.value() / 100
            yellow = self.ySpin.value() / 100
            black = self.kSpin.value() / 100

            red = 1 - min(1, cyan * (1 - black) + black)
            green = 1 - min(1, magenta * (1 - black) + black)
            blue = 1 - min(1, yellow * (1 - black) + black)

            self.rSpin.setValue(round(red * 255))
            self.gSpin.setValue(round(green * 255))
            self.bSpin.setValue(round(blue * 255))
            color_label ="QLabel{{ background-color: rgb({},{},{});}}".format(self.rSpin.value(), self.gSpin.value(), self.bSpin.value())
            self.color_value_label.setStyleSheet(color_label)
        except ZeroDivisionError:
            pass


app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())
