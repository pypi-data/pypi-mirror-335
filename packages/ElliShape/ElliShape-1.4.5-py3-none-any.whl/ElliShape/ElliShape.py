# -*- coding: utf-8 -*-
import sys
import numpy as np
import os
import glob
import pandas as pd
import cv2  # type: ignore
import torch
import shutil
import tempfile
import uuid
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap, QPainterPath, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPointF, QPoint, QRectF

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.append('/segment_anything')
from segment_anything import SamPredictor, sam_model_registry
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

sys.path.append('/functions')
from functions.inverted_colors_func import inverted_colors_func
from functions.grayscale_func import grayscale_func
from functions.enhancement_func import enhancement_func
from functions.binarize_func import binarize_func
from functions.corrosion_func import corrosion_func
from functions.dilation_func import dilation_func
from functions.gui_chain_code_func import gui_chain_code_func
from functions.contour_extraction_func import contour_extraction_func
from functions.cal_area_c import cal_area_c
from functions.is_completed_chain_code import is_completed_chain_code
from functions.calc_traversal_dist import calc_traversal_dist
from functions.write_Data_To_File import write_data_to_file
from functions.EFA import MainWindow_1 

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"

class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, main_window,*args, **kwargs):
        super(CustomGraphicsView, self).__init__(main_window,*args, **kwargs)
        self.setScene(scene)
        self.drawing = False
        self.last_point = QPoint()
        self.main_window = main_window
        self.pixmap_result_item = None  
        self.drawn_paths = []  # 存储所有绘制的路径项
        self.show_sam_result()
    
    def show_sam_result(self):
        self.scene().clear() 
        # print(self.main_window.bin)
        if hasattr(self.main_window, 'bin') and len(self.main_window.bin) > 0:  # 动态获取 bin
            pixmap_result = self.numpy_to_pixmap(self.main_window.bin)
            self.pixmap_result_item = QGraphicsPixmapItem(pixmap_result)
            self.scene().addItem(self.pixmap_result_item)

    def mousePressEvent(self, event):
        try:
            items = self.scene().items()
            log.info("%s", len(items))
            if len(items) > 1:
                for item in items[:-1]:
                    if  isinstance(item, QGraphicsLineItem):
                        pen = item.pen()
                        try:
                            if pen.color() == QColor(255, 0, 0) or pen.color() == QColor(0, 255, 0):
                                # print("CustomGraphicsView")
                                self.scene().removeItem(item)
                        except ValueError as e:
                            QMessageBox.warning(self,'Error','{e}')
                            return
            pos = event.pos()
            pos_adjusted = self.mapToScene(pos).toPoint()
            self.last_point = pos_adjusted
            if event.button() == Qt.LeftButton:
                self.drawing= True
            if event.button() == Qt.RightButton:
                self.show_context_menu(event)
            log.info(f"Mouse Press at {pos_adjusted}")
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return
    def mouseMoveEvent(self, event):
        try:
            if self.drawing:
                current_pos = self.mapToScene(event.pos())
                # 动态获取当前像素的 bin 值以决定画笔颜色
                x = int(current_pos.x())
                y = int(current_pos.y())
                if 0 <= x < self.main_window.bin.shape[1] and 0 <= y < self.main_window.bin.shape[0]:
                    current_value = self.main_window.bin[y, x]
                    pen_color = QColor(255, 255, 255) if current_value == 0 else QColor(0, 0, 0)
                else:
                    pen_color = QColor(255, 255, 255)  # 默认白色

                # 创建路径项并绘制线段
                path = QPainterPath()
                path.moveTo(self.last_point)
                path.lineTo(current_pos)
                path_item = QGraphicsPathItem(path)
                path_item.setPen(QPen(pen_color, 1))
                self.scene().addItem(path_item)
                self.drawn_paths.append(path_item)  # 保存路径项

                self.last_point = current_pos
                log.info(f"Mouse Move to {current_pos}")
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return
    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.LeftButton:
                self.drawing = False
                log.info("Mouse Release")
                # self.save_scene_as_image()
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return
    def draw_line(self, start_point, end_point,pen):
        try:
            line = self.scene().addLine(start_point.x(), start_point.y(), end_point.x(), end_point.y(),pen)
            log.info(f"Draw line from {start_point} to {end_point}")
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def show_context_menu(self, event):
        context_menu = QMenu(self)
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.reset_scene)
        context_menu.addAction(reset_action)
        context_menu.exec_(self.mapToGlobal(event.pos()))

    def reset_scene(self):
        self.show_sam_result()
        log.info("Scene has been reset")
        QMessageBox.information(self, "Reset", "All edits have been reset")

    def numpy_to_pixmap(self, numpy_array):
        try:
            if len(numpy_array.shape) == 2:  
                height, width = numpy_array.shape
                bytes_per_line = width
                q_image = QImage(numpy_array.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
                return QPixmap.fromImage(q_image)
            elif len(numpy_array.shape) == 3:  
                height, width, channel = numpy_array.shape
                bytes_per_line = channel * width
                if channel == 3:
                    q_image = QImage(numpy_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
                elif channel == 4:
                    q_image = QImage(numpy_array.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
                else:
                    raise ValueError("Unsupported number of channels: {}".format(channel))
                return QPixmap.fromImage(q_image)
            else:
                raise ValueError("Unsupported image format: {}".format(numpy_array.shape))
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return


class CustomGraphicsView_1(QGraphicsView):  
    def __init__(self, main_window, *args):
        super().__init__( main_window.scene, main_window, *args)
        self.setMouseTracking(True)  
        
        self.main_window = main_window  
        self.setScene(main_window.scene)
        self.scene_1 = self.main_window.scene
        
        self.start_point = None  
        self.end_point = None
        self.current_rect_item = None  
        self.is_drawing = False  
        
        self.polygon = []
        
        self.scene_2 = self.main_window.scene_2
        self.graphicsView_2 = self.main_window.graphicsView_2
        self.pushButton_8 = self.main_window.pushButton_8
        
        self.points_pre = []
        self.points = []
        
        self.polygon_item = None

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton and self.main_window.flag_btn_6==0:
            if self.main_window.image:
                self.scene_1.clear()
                pixmap_item = QGraphicsPixmapItem(self.main_window.image)
                self.scene_1.addItem(pixmap_item)
            self.is_drawing = True
        
            self.start_point = self.mapToScene(event.pos())
            
            self.current_rect_item = QGraphicsRectItem()
            self.current_rect_item.setPen(Qt.red)
            self.scene_1.addItem(self.current_rect_item)
        
        try:
            print(self.main_window.flag_btn_6)
            if (self.main_window.flag_btn_6==1) & (event.buttons() == Qt.LeftButton) : 
                # print("执行画线")   
                scenepos = self.mapToScene(event.pos())          
                
                log.info("Mouse Position (Scene Coordinates): (%s, %s)", scenepos.x(),scenepos.y())
                # print("Mouse Position (View Coordinates):", pos_adjusted.x(), pos_adjusted.y())
                # print("Mouse Position (Scene Coordinates):", self.scene_pos[0],  self.scene_pos[1])
                self.polygon.append(QPointF(scenepos.x(),scenepos.y()))
                print(self.polygon)
                self.updatePolygon()
                    

            elif (self.main_window.flag_btn_6==1) & (event.buttons() == Qt.RightButton) :
                pixmap_item=self.cropImage()          
                height=self.main_window.image.height()
                width=self.main_window.image.width()   
                mask = np.zeros((height, width), dtype=np.uint8)
                if self.polygon == None:
                    return
                print(self.polygon[0])
                self.scene_1.addLine(self.polygon[0].x(), self.polygon[0].y(), self.polygon[-1].x(), self.polygon[-1].y(), QPen(Qt.red,3))
                pts = np.array([(point.x(), point.y()) for point in self.polygon], dtype=np.int32)
                
                
                cv2.fillPoly(mask, [pts], 255)
                # print(np.shape(self.main_window.image))
                try:
                    img_num=self.main_window.pixmap_to_numpy(self.main_window.image)
                except ValueError as e:
                    QMessageBox.warning(self,'Error','{e}')
                    return
                result = cv2.bitwise_and(img_num, img_num, mask=mask)
                result[(result[:,:,0] == 0) & (result[:,:,1] == 0) & (result[:,:,2] == 0)] = [255, 255, 255]
                # cv2.imwrite('result.png',result)
                self.main_window.crop_result =  cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                pixmap_result = self.main_window.numpy_to_pixmap(self.main_window.crop_result)
                pixmap_result_item = QGraphicsPixmapItem(pixmap_result)
                self.scene_2.clear()
                self.scene_2.addItem(pixmap_result_item)
                self.graphicsView_2.setScene(self.scene_2)
                self.graphicsView_2.fitInView(self.graphicsView_2.sceneRect(), Qt.KeepAspectRatio)
                self.polygon = []
                self.polygon_item = None
                self.main_window.flag_btn_6=0
                self.pushButton_8.setEnabled(True)

            if (self.main_window.flag_point == 1) & (event.button() == Qt.LeftButton) :           
                if hasattr(self, 'points'):
                    self.points_pre.append((event.x(), event.y()))
                else:
                    self.points_pre = [(event.x(), event.y())]
                # print(self.points_pre)
                # print(len(self.points_pre))
                if len(self.points_pre) == 2:
                    pos_dis1 = QtCore.QPoint(self.points_pre[0][0], self.points_pre[0][1])
                    scenepos_dis1 = self.mapToScene(pos_dis1)
                    self.points.append((scenepos_dis1.x(),scenepos_dis1.y()))
                    pos_dis2 = QtCore.QPoint(self.points_pre[1][0], self.points_pre[1][1])
                    scenepos_dis2 = self.mapToScene(pos_dis2)
                    self.points.append((scenepos_dis2.x(),scenepos_dis2.y()))
                    # print(self.points)
                    self.main_window.distance = ((self.points[1][0] - self.points[0][0])**2 + (self.points[1][1] - self.points[0][1])**2)**0.5

                    point_item = QGraphicsEllipseItem(self.points[0][0], self.points[0][1]-10, 20, 20)
                    point_item.setBrush(Qt.red)  
                    self.scene_1.addItem(point_item)
                    point_item = QGraphicsEllipseItem(self.points[1][0]-10, self.points[1][1]-10, 20, 20)  
                    point_item.setBrush(Qt.red)  
                    self.scene_1.addItem(point_item) 

                    # self.graphicsView.setScene(self.scene)
                    self.points_pre=[]
                    self.points = []
                    self.main_window.flag_point=0
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return
        # super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        try:
            # print(self.start_point)
            if self.is_drawing and self.start_point:
                # print('movement')
                
                self.end_point = self.mapToScene(event.pos())
                
                rect = QRectF(self.start_point, self.end_point).normalized()  # 归一化确保矩形方向正确
                self.current_rect_item.setRect(rect)
            # super().mouseMoveEvent(event)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return
        
        

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.LeftButton and self.is_drawing:
                
                self.is_drawing = False
                # self.start_point = None
                # self.pointsChanged.emit(self.start_point, self.end_point)  # 触发信号
                print("Rectangle drawn:", self.current_rect_item.rect())
                # Ensure self.polygon and self.image are valid
                if not self.current_rect_item.rect().isEmpty():
                    height=self.main_window.image.height()
                    width=self.main_window.image.width()  
                    mask = np.zeros((height, width), dtype=np.uint8)

                    # 提取矩形四个顶点作为多边形点
                    rect = self.current_rect_item.rect()
                    top_left = (rect.x(), rect.y())
                    top_right = (rect.x() + rect.width(), rect.y())
                    bottom_right = (rect.x() + rect.width(), rect.y() + rect.height())
                    bottom_left = (rect.x(), rect.y() + rect.height())
                    polygon_points = np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.int32)
                    
                    cv2.fillPoly(mask, [polygon_points], 255)
                    # print(np.shape(self.main_window.image))
                    try:
                        img_num=self.main_window.pixmap_to_numpy(self.main_window.image)
                    except ValueError as e:
                        QMessageBox.warning(self,'Error','{e}')
                        return
                    result = cv2.bitwise_and(img_num, img_num, mask=mask)
                    result[(result[:,:,0] == 0) & (result[:,:,1] == 0) & (result[:,:,2] == 0)] = [255, 255, 255]
                    # cv2.imwrite('result.png',result)
                    self.main_window.crop_result =  cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                    pixmap_result = self.main_window.numpy_to_pixmap(self.main_window.crop_result)
                    pixmap_result_item = QGraphicsPixmapItem(pixmap_result)
                    self.scene_2.clear()
                    self.scene_2.addItem(pixmap_result_item)
                    self.graphicsView_2.setScene(self.scene_2)
                    self.graphicsView_2.fitInView(self.graphicsView_2.sceneRect(), Qt.KeepAspectRatio)

            # super().mouseReleaseEvent(event)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return
    def updatePolygon(self):
        try:
            # if self.polygon_item:
            #     print("polygon item")
            #     self.polygon_item=None
            #     # self.scene_1.removeItem(self.polygon_item)
            #     print("after polygon item")
            if len(self.polygon) < 2:
                return
            path = QPainterPath()
            # print(self.polygon[0])
            path.moveTo(self.polygon[0])
            for point in self.polygon[1:]:
                path.lineTo(point)
            # path.lineTo(self.polygon[0])
            self.polygon_item = self.scene_1.addPath(path, QPen(Qt.red,3))
            self.polygon_item=None
            # print("done")
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def cropImage(self):
        try:
            if len(self.polygon) < 3:
                return
            path = QPainterPath()
            path.moveTo(self.polygon[0])
            for point in self.polygon[1:]:
                path.lineTo(point)
            path.lineTo(self.polygon[0])
            region = QImage(self.main_window.image.size(), QImage.Format_ARGB32)
            region.fill(Qt.transparent)
            painter = QPainter(region)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setClipPath(path)
            # painter.drawImage(0, 0, self.image)
            painter.end()
            cropped_pixmap = QPixmap.fromImage(region)
            pixmap_item = QGraphicsPixmapItem(cropped_pixmap)
            return pixmap_item
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return
    

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.resize(1795, 950)
        # font = QtGui.QFont()
        # font.setFamily("Arial")
        # font.setPointSize(10)
        # self.setFont(font)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # 获取屏幕的DPI比例
        screen = self.screen()
        dpi_ratio = screen.logicalDotsPerInch() / 96.0  # 96是标准DPI

        # 设置字体
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))  # 根据DPI比例调整字体大小
        self.setFont(font)

        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(10, 5, 591, 65))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.groupBox_4.setFont(font)
        self.groupBox_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox_4.setObjectName("groupBox_4")


        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(12, 30, 101, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")

        self.graphicsView_2 = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView_2.setGeometry(QtCore.QRect(610, 75, 481, 321))
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.graphicsView_3 = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView_3.setGeometry(QtCore.QRect(610, 405, 481, 331))
        self.graphicsView_3.setObjectName("graphicsView_3")
        

        self.scene_3 = QGraphicsScene(self)
        self.bin = []
        self.graphicsView_4 = CustomGraphicsView(self.scene_3,self)
        self.graphicsView_4.setGeometry(QtCore.QRect(1100, 75, 681, 661))
        self.graphicsView_4.setObjectName("graphicsView_4")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(120, 30, 317, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.comboBox.setFont(font)
        self.comboBox.setObjectName("comboBox")


        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(447, 30, 71, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(22 / dpi_ratio))
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(528, 30, 71, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(22 / dpi_ratio))
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")


        self.groupBox_5 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_5.setGeometry(QtCore.QRect(610, 5, 481, 65))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.groupBox_5.setFont(font)
        self.groupBox_5.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox_5.setObjectName("groupBox_5")

        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(842, 30, 20, 35))
        self.label_6.setObjectName("label_6")
        self.label_6.setFont(font)
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(612, 30, 215, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.pushButton_5.setFont(font)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(874, 30, 215, 35)) 
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.pushButton_6.setFont(font)
        self.pushButton_6.setObjectName("pushButton_6")


        self.groupBox_6 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_6.setGeometry(QtCore.QRect(1100, 5, 681, 65))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.groupBox_6.setFont(font)
        self.groupBox_6.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox_6.setObjectName("groupBox_6")

        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(1560, 30, 219, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")

        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_7.setGeometry(QtCore.QRect(1331, 30, 219, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.pushButton_7.setFont(font)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_8 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_8.setGeometry(QtCore.QRect(1102, 30, 219, 35))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.pushButton_8.setFont(font)
        self.pushButton_8.setObjectName("pushButton_8")



        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(905, 740, 876, 120))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.pushButton_9 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_9.setGeometry(QtCore.QRect(10, 25, 200, 35))
        self.pushButton_9.setObjectName("pushButton_9")
        self.textEdit_5 = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit_5.setGeometry(QtCore.QRect(360, 25, 281, 35))
        self.textEdit_5.setObjectName("textEdit_5")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.textEdit_5.setFont(font)
        self.radioButton = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton.setGeometry(QtCore.QRect(670, 25, 51, 16))
        self.radioButton.setObjectName("radioButton")
        self.radioButton.setChecked(True)
        self.radioButton.setFixedSize(51, 16)
        self.radioButton.setFont(font)
        self.radioButton.setStyleSheet("""
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
        """)  # 固定圆形按钮标识的大小
        self.buttonGroup = QtWidgets.QButtonGroup(self)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.radioButton)
        self.radioButton_2 = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton_2.setGeometry(QtCore.QRect(670, 43, 61, 16))
        self.radioButton_2.setObjectName("radioButton_2")
        self.radioButton_2.setFixedSize(61, 16)
        self.radioButton_2.setFont(font)
        self.radioButton_2.setStyleSheet("""
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
        """)  # 固定圆形按钮标识的大小
        self.buttonGroup.addButton(self.radioButton_2)
        self.pushButton_10 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_10.setGeometry(QtCore.QRect(741, 25, 125, 35))
        self.pushButton_10.setObjectName("pushButton_10")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(220, 25, 150, 35))
        self.label_5.setObjectName("label_5")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(50, 75, 51, 35))
        self.label_4.setObjectName("label_4")
        self.textEdit_7 = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit_7.setGeometry(QtCore.QRect(110, 75, 100, 35))
        self.textEdit_7.setAutoFillBackground(False)
        self.textEdit_7.setMidLineWidth(0)
        self.textEdit_7.setObjectName("textEdit_7")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.textEdit_7.setFont(font)
        self.pushButton_16 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_16.setGeometry(QtCore.QRect(220, 75, 646, 35))
        self.pushButton_16.setObjectName("pushButton_16")


        self.pushButton_17 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_17.setGeometry(QtCore.QRect(10, 870, 1771, 50))
        self.pushButton_17.setIconSize(QtCore.QSize(30, 30))
        self.pushButton_17.setObjectName("pushButton_17")


        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 740, 885, 120))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.groupBox_2.setFont(font)
        self.groupBox_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox_2.setObjectName("groupBox_2")
        self.radioButton_3 = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton_3.setGeometry(QtCore.QRect(20, 30, 211, 19))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.radioButton_3.setFont(font)
        self.radioButton_3.setObjectName("radioButton_3")
        self.radioButton_3.setChecked(True)
        self.radioButton_3.setEnabled(False)
        self.radioButton_3.setFixedSize(211, 19)
        self.radioButton_3.setStyleSheet("""
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
        """)  # 固定圆形按钮标识的大小
        self.buttonGroup_2 = QtWidgets.QButtonGroup(self)
        self.buttonGroup_2.setObjectName("buttonGroup_2")
        self.buttonGroup_2.addButton(self.radioButton_3)
        self.radioButton_4 = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton_4.setGeometry(QtCore.QRect(20, 80, 211, 19))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.radioButton_4.setFont(font)
        self.radioButton_4.setObjectName("radioButton_4")
        self.radioButton_4.setEnabled(False)
        self.radioButton_4.setFixedSize(211, 19)
        self.radioButton_4.setStyleSheet("""
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
        """)  # 固定圆形按钮标识的大小
        self.buttonGroup_2.addButton(self.radioButton_4)
        self.pushButton_11 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_11.setGeometry(QtCore.QRect(220, 25, 100, 35))
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_12 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_12.setGeometry(QtCore.QRect(475, 25, 100, 35))
        self.pushButton_12.setObjectName("pushButton_12")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(345, 25, 40, 35))
        self.label_3.setObjectName("label_3")
        self.textEdit_6 = QtWidgets.QTextEdit(self.groupBox_2)
        self.textEdit_6.setGeometry(QtCore.QRect(395, 25, 70, 35))
        self.textEdit_6.setAutoFillBackground(False)
        self.textEdit_6.setMidLineWidth(0)
        self.textEdit_6.setObjectName("textEdit_6")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(int(12 / dpi_ratio))
        self.textEdit_6.setFont(font)
        self.pushButton_13 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_13.setGeometry(QtCore.QRect(585, 25, 150, 35))
        self.pushButton_13.setObjectName("pushButton_13")
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_2.setGeometry(QtCore.QRect(220, 75, 100, 35))
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("canny")
        self.comboBox_2.addItem("sobel")
        self.comboBox_2.addItem("zerocross")
        self.comboBox_2.addItem("laplace")
        self.comboBox_2.addItem("Roberts")
        self.comboBox_2.addItem("Prewitt")
        self.horizontalSlider = QtWidgets.QSlider(self.groupBox_2)
        self.horizontalSlider.setGeometry(QtCore.QRect(345, 75, 230, 35))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.pushButton_14 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_14.setGeometry(QtCore.QRect(585, 75, 150, 35))
        self.pushButton_14.setObjectName("pushButton_14")
        self.pushButton_15 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_15.setGeometry(QtCore.QRect(745, 25, 130, 85))
        self.pushButton_15.setObjectName("pushButton_15")


        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1795, 25))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "ElliShape"))
        self.pushButton.setText(_translate("MainWindow", "Folder"))
        self.pushButton_2.setText(_translate("MainWindow", "→"))
        self.pushButton_3.setText(_translate("MainWindow", "←"))
        self.pushButton_4.setText(_translate("MainWindow", "Inverted Colors"))
        self.pushButton_5.setText(_translate("MainWindow", "Automated Segmentation"))
        self.pushButton_6.setText(_translate("MainWindow", "Polygon Tool"))
        self.pushButton_7.setText(_translate("MainWindow", "Image Enhancement"))
        self.pushButton_8.setText(_translate("MainWindow", "Grayscale Conversion"))
        self.groupBox.setTitle(_translate("MainWindow", "4 Measurement and save"))
        self.groupBox_4.setTitle(_translate("MainWindow", "1 Input"))
        self.groupBox_5.setTitle(_translate("MainWindow", "2.1 Extraction"))
        self.groupBox_6.setTitle(_translate("MainWindow", "2.2 Image processing"))
        self.pushButton_9.setText(_translate("MainWindow", "Click two points"))

        self.textEdit_5.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Arial\',\'Arial\'; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.radioButton.setText(_translate("MainWindow", "mm"))
        self.radioButton_2.setText(_translate("MainWindow", "inch"))
        self.pushButton_10.setText(_translate("MainWindow", "Skip"))
        self.label_5.setText(_translate("MainWindow", "Actual distance:"))
        self.label_6.setText(_translate("MainWindow", "or"))

        self.groupBox_2.setTitle(_translate("MainWindow", "3 Chain code"))
        self.radioButton_3.setText(_translate("MainWindow", "Image Binarization"))
        
        self.radioButton_4.setText(_translate("MainWindow", "Edge Detection"))
        self.pushButton_11.setText(_translate("MainWindow", "Binarization"))
        self.pushButton_12.setText(_translate("MainWindow", "Erosion"))
        self.label_3.setText(_translate("MainWindow", "Size:"))
        self.textEdit_6.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Arial\',\'Arial\'; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial\';\">3</span></p></body></html>"))
        self.pushButton_13.setText(_translate("MainWindow", "Dilation "))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "Select"))
        self.pushButton_14.setText(_translate("MainWindow", "Contour Extraction"))
        self.pushButton_15.setText(_translate("MainWindow", "Chain Code"))

        self.label_4.setText(_translate("MainWindow", "Tag:"))
        self.textEdit_7.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Arial\',\'Arial\'; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial\';\">1</span></p></body></html>"))
        self.pushButton_16.setText(_translate("MainWindow", "Save (chain codes, labeled images and size)"))
        self.pushButton_17.setText(_translate("MainWindow", "Elliptic Fourier Analysis"))
        self.folder_path = ''
        self.cwd = os.getcwd() 
        self.image = []
        self.gray_img = []
        
        self.crop_result = []
        # self.scene_pos=[0,0]
        self.scene_2=QGraphicsScene()
        # self.polygon = []
        
        self.flag_point = 0
        self.flag_btn_6 = 0
        self.is_dragging = False
        # self.points = []
        # self.points_pre = []
        self.boundary = []
        self.chaincode = []
        self.last_point = QPoint()   
        self.drawing = False   
        self.last_point = [] 
        self.id_full = '1'
        self.filename = ''
        self.unit = 1
        self.distance = 0

        self.scene = QGraphicsScene(self)
        self.graphicsView = CustomGraphicsView_1(self)
        self.graphicsView.setGeometry(QtCore.QRect(10, 75, 591, 661))
        self.graphicsView.setObjectName("graphicsView")

        for widget in self.centralWidget().findChildren(QPushButton):
            widget.setDisabled(True)
        self.pushButton.setEnabled(True)
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        self.comboBox.activated.connect(self.comboBox_Callback)
        self.pushButton_2.clicked.connect(self.Nextbtn_clicked)
        self.pushButton_3.clicked.connect(self.Previousbtn_clicked)       
        self.pushButton_4.clicked.connect(self.Inverted_color)
        self.pushButton_5.clicked.connect(self.SAM_segment)
        self.pushButton_6.clicked.connect(self.ROI_selection)
        self.pushButton_8.clicked.connect(self.grayscale)
        self.pushButton_7.clicked.connect(self.enhancement)
        self.buttonGroup.buttonClicked.connect(self.units_set)
        self.buttonGroup_2.buttonClicked.connect(self.method_set)
        self.pushButton_11.clicked.connect(self.binarization)
        self.pushButton_12.clicked.connect(self.corrosion)
        self.pushButton_13.clicked.connect(self.dilation)
        self.pushButton_15.clicked.connect(self.chain_code)
        self.pushButton_14.clicked.connect(self.functions_selection)
        self.pushButton_9.clicked.connect(self.clicked_point)
        self.pushButton_16.clicked.connect(self.save)
        self.pushButton_10.clicked.connect(self.skip)
        self.pushButton_17.clicked.connect(self.go_to_window2)
        

    def on_pushButton_clicked(self):
        try:
            self.folder_path = QFileDialog.getExistingDirectory(self, "select folder", self.cwd)             
            if self.folder_path:
                self.comboBox.clear()
                self.image_files = []
                for file_path in glob.glob(os.path.join(self.folder_path, "*")):
                    if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff")):
                        self.image_files.append(os.path.basename(file_path))
                self.comboBox.addItems(self.image_files)
                log.info("Number of images: %s", len(self.image_files))
            else:
                QMessageBox.warning(self, "Warning", "folder is empty")
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return    


    def comboBox_Callback(self):
        try:
            for widget in self.centralWidget().findChildren(QPushButton):
                widget.setDisabled(True)
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True) 
            self.polygon = []
            self.polygon_item = None
            self.filename = self.comboBox.currentText()
            self.c_index = self.comboBox.currentIndex()
            file_path = os.path.join(self.folder_path,self.filename)
            if self.filename:
                # a=cv2.imread(file_path)
                # cv2.imshow('activated',a)
                # self.load_image(file_path)            
                self.image = QPixmap(file_path) 
                pixmap_item = QGraphicsPixmapItem(self.image)
                # print(pixmap_item)
                self.scene.clear()
                self.scene_2.clear()
                self.scene_3.clear()
                self.scene.addItem(pixmap_item)

                self.scene.setSceneRect(pixmap_item.boundingRect())
                self.graphicsView.setScene(self.scene)
                self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
                self.graphicsView.update()
                self.graphicsView.viewport().update()

                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setEnabled(True)
                self.pushButton_4.setEnabled(True)
                self.pushButton_5.setEnabled(True)
                self.pushButton_6.setEnabled(True)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return


    def ROI_selection(self):
        self.flag_btn_6=1
        self.scene.clear()
        pixmap_item = QGraphicsPixmapItem(self.image)
        self.scene.addItem(pixmap_item)
        


    def Previousbtn_clicked(self):
        try:
            if self.c_index != 0:
                for widget in self.centralWidget().findChildren(QPushButton):
                    widget.setDisabled(True)
                self.pushButton.setEnabled(True)
                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setEnabled(True) 
                self.c_index -= 1
                # print(self.c_index)
                self.filename = self.image_files[self.c_index]
                file_path = os.path.join(self.folder_path,self.filename)
                # print(file_path)
                self.image = QPixmap(file_path)
                ncols = self.image.width()            
                nrows = self.image.height()
                pixmap_item = QGraphicsPixmapItem(self.image)
                self.scene.clear()
                self.scene_2.clear()
                self.scene_3.clear()
                self.scene.addItem(pixmap_item)
                self.scene.setSceneRect(pixmap_item.boundingRect())
                self.graphicsView.setScene(self.scene)
                self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

                self.comboBox.setCurrentIndex(self.c_index)
                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setEnabled(True)
                self.pushButton_4.setEnabled(True)
                self.pushButton_5.setEnabled(True)
                self.pushButton_6.setEnabled(True)
            else:
                QMessageBox.warning(self, "Warning", "This is the first one.")
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def Nextbtn_clicked(self):
        try:
            if self.c_index != len(self.image_files)-1:
                for widget in self.centralWidget().findChildren(QPushButton):
                    widget.setDisabled(True)
                self.pushButton.setEnabled(True)
                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setEnabled(True) 
                self.c_index += 1
                # print(self.c_index)
                self.filename = self.image_files[self.c_index]
                file_path = os.path.join(self.folder_path,self.filename)
                # print(file_path)
                self.image = QPixmap(file_path)
                ncols = self.image.width()            
                nrows = self.image.height()
                pixmap_item = QGraphicsPixmapItem(self.image)
                self.scene.clear()
                self.scene_2.clear()
                self.scene_3.clear()
                self.scene.addItem(pixmap_item)
                self.scene.setSceneRect(pixmap_item.boundingRect())
                self.graphicsView.setScene(self.scene)
                self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
                self.comboBox.setCurrentIndex(self.c_index)
                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setEnabled(True)
                self.pushButton_4.setEnabled(True)
                self.pushButton_5.setEnabled(True)
                self.pushButton_6.setEnabled(True)
            else:
                # print("This is the last one")
                QMessageBox.warning(self, "Warning", "This is the last one.")
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def Inverted_color(self):
        try:
            if self.image:
                img_v = self.pixmap_to_numpy(self.image)
                img_inverted = inverted_colors_func(img_v)
                img_inverted = self.numpy_to_pixmap(img_inverted)
                self.image=img_inverted
                pixmap_item = QGraphicsPixmapItem(img_inverted)
                self.scene.clear()
                self.scene.addItem(pixmap_item)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def pixmap_to_numpy(self,pixmap):
        try:
            image = QImage(pixmap.toImage())
            # print(image.format())  
            if image.format() in (QImage.Format_ARGB32, QImage.Format_RGB32, QImage.Format_ARGB32_Premultiplied):
                ptr = image.bits()
                ptr.setsize(image.byteCount())      
                arr = np.array(ptr).reshape(image.height(), image.width(), 4)   
                if (image.format() == QImage.Format_RGB32) or (image.format()== QImage.Format_ARGB32) :     
                    arr = arr[:, :, :3] 
                elif image.format()  == QImage.Format_ARGB32_Premultiplied:
                    # print(arr.shape)
                    # Handle premultiplied alpha
                    alpha = arr[:, :, 3:4] / 255.0
                    bgr = arr[:, :, :3] / alpha
                    # Clip values to ensure they are in valid range [0, 255]
                    bgr = np.clip(bgr, 0, 255)
                    # Convert to uint8 data type
                    bgr = bgr.astype(np.uint8)
                    # Convert from RGBA to BGR
                    arr = bgr[..., ::-1]
                    # Debugging: print the shape and dtype of the array
                # print(f"Array shape: {arr.shape}, dtype: {arr.dtype}")        
                return arr       
            # Handle QImage.Format_RGB888
            elif image.format()== QImage.Format_RGB888:
                width = image.width()
                height = image.height()
                ptr = image.bits()
                ptr.setsize(image.byteCount())               
                # Convert to numpy array
                arr = np.array(ptr).reshape(height, width, 3)               
                # Debugging: print the shape and dtype of the array
                # print(f"Array shape: {arr.shape}, dtype: {arr.dtype}")
                return arr
            else:
                raise ValueError("The image format does not support conversion to a numpy array.")
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def numpy_to_pixmap(self, numpy_array):
        try:
            if len(numpy_array.shape) == 2:  
                height, width = numpy_array.shape
                bytes_per_line = width
                q_image = QImage(numpy_array.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
                return QPixmap.fromImage(q_image)
            elif len(numpy_array.shape) == 3:  
                height, width, channel = numpy_array.shape
                bytes_per_line = channel * width
                if channel == 3:
                    q_image = QImage(numpy_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
                elif channel == 4:
                    q_image = QImage(numpy_array.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
                else:
                    raise ValueError("Unsupported number of channels: {}".format(channel))
                return QPixmap.fromImage(q_image)
            else:
                raise ValueError("Unsupported image format: {}".format(numpy_array.shape))
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def show_mask(self, mask, random_color=False,i=0):
        try:
            if random_color:
                color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
            else:
                color = np.array([30/255, 144/255, 255/255, 0.6])
            h, w = mask.shape[-2:]
            mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
            # cv2.imshow('mask'+str(i),mask_image)
            mask_image =  (mask_image * 255).astype(np.uint8)
            # cv2.imshow('mask',mask_image)
            # print(np.max(mask_image))
            img_mask = self.numpy_to_pixmap(mask_image)
            pixmap_item = QGraphicsPixmapItem(img_mask)
            self.scene.addItem(pixmap_item)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def SAM_segment(self):  # progress_signal
        try:
            # 检查 start_point 和 end_point 是否存在
            if not hasattr(self.graphicsView, 'start_point') or not hasattr(self.graphicsView, 'end_point'):
                QMessageBox.warning(self, "Warning", "Please select a rectangle area first.")
                return

            if self.graphicsView.start_point is None or self.graphicsView.end_point is None:
                QMessageBox.warning(self, "Warning", "Please select a rectangle area first.")
                return
            progress_dialog = QProgressDialog("Running now, please wait a moment...", "Cancel", 0, 100, self)
            progress_dialog.setWindowTitle("Processing")
            progress_dialog.setWindowModality(Qt.WindowModal)  
            progress_dialog.setAutoClose(True) 
            progress_dialog.setAutoReset(True)  
            progress_dialog.setMinimumDuration(0)  
            progress_dialog.setValue(0)  

            progress_dialog.setValue(10) 

            current_dir = os.path.dirname(os.path.abspath(__file__))
            checkpoint_path_1 = os.path.join(current_dir, "sam_vit_h_4b8939.pth")
            checkpoint_path_2 = os.path.join(current_dir, "sam_vit_b_01ec64.pth")
            if torch.cuda.is_available():
                if not os.path.exists(checkpoint_path_1):
                    QMessageBox.warning(self, "Warning",  "Please download the '.pth' file first.")
                    return
                sam = sam_model_registry['vit_h'](checkpoint=checkpoint_path_1)
                device = 'cuda'
            else:
                if not os.path.exists(checkpoint_path_2):
                    QMessageBox.warning(self, "Warning",  "Please download the '.pth' file first.")
                    return
                sam = sam_model_registry['vit_b'](checkpoint=checkpoint_path_2)
                device = 'cpu'

            sam.to(device=device)
            predictor = SamPredictor(sam)
            self.filename = self.image_files[self.c_index]
            file_path = os.path.join(self.folder_path, self.filename)

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} doesn't exist")

            has_non_ascii = any(ord(c) > 127 for c in file_path)

            if has_non_ascii:
                temp_dir = tempfile.gettempdir()

                file_ext = os.path.splitext(file_path)[1]

                temp_filename = f"{uuid.uuid4().hex}{file_ext}"
                temp_path = os.path.join(temp_dir, temp_filename)

                try:
                    shutil.copy(file_path, temp_path)

                    image = cv2.imread(temp_path)

                    if image is None:
                        raise ValueError(f"Image cannot be read from temporary path: {temp_path}")

                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            else:

                image = cv2.imread(file_path)
                if image is None:
                    raise ValueError(f"Unable to read file: {file_path}")

            progress_dialog.setValue(30) 

            if image is not None:
                predictor.set_image(image)

                input_box = [self.graphicsView.start_point.x(), self.graphicsView.start_point.y(),
                            self.graphicsView.end_point.x(), self.graphicsView.end_point.y()]  #  (x_min, y_min, x_max, y_max)
                input_box = np.array(input_box)

                masks, scores, logits = predictor.predict(box=input_box)


                progress_dialog.setValue(70)  

                if masks.shape[0] != 0:
                    self.pushButton_7.setEnabled(False)
                    self.pushButton_8.setEnabled(False)
                    self.pushButton_11.setEnabled(False)
                    self.pushButton_12.setEnabled(True)
                    self.pushButton_13.setEnabled(True)
                    self.pushButton_15.setEnabled(True)
                    for i, (mask, score) in enumerate(zip(masks, scores)):
                        if i == 0:
                            self.show_mask(mask, True, i)
                            self.bin = (mask * 255).astype(np.uint8)
                            pixmap_result = self.numpy_to_pixmap(self.bin)
                            pixmap_result_item = QGraphicsPixmapItem(pixmap_result)
                            self.scene_2.clear()
                            self.scene_3.clear()
                            self.scene_3.addItem(pixmap_result_item)
                            self.graphicsView_3.setScene(self.scene_3)
                            self.graphicsView_3.fitInView(self.graphicsView_3.sceneRect(), Qt.KeepAspectRatio)
                            self.graphicsView_4.setScene(self.scene_3)
                            self.graphicsView_4.fitInView(self.graphicsView_4.sceneRect(), Qt.KeepAspectRatio)
                            progress_dialog.setValue(100)  
                            QMessageBox.information(None, "Success", "You can also try using the 'Polygon Tool'.") 
                              
                            
            else:
                QMessageBox.warning(self, "Warning", "Failed to read image. Please check the file path.")
        except ValueError as e:
            QMessageBox.warning(self, 'Error', f'{e}')

    
    def wheelEvent(self, event):
        try:
            pos=event.pos()
            pos_adjusted = QtCore.QPoint(pos.x() - 10, pos.y() - 60)  
            if self.graphicsView.viewport().rect().contains(pos_adjusted):
                if(event.angleDelta().y()>0.5):
                    self.graphicsView.scale(1.5,1.5)
                elif(event.angleDelta().y()< 0.5):
                    self.graphicsView.scale(1 /1.5,1 / 1.5)

            pos_adjusted_2 = QtCore.QPoint(pos.x() - 610, pos.y() - 60)  
            if self.graphicsView_2.viewport().rect().contains(pos_adjusted_2):
                if(event.angleDelta().y()>0.5):
                    self.graphicsView_2.scale(1.5,1.5)
                elif(event.angleDelta().y()< 0.5):
                    self.graphicsView_2.scale(1 /1.5,1 / 1.5)

            pos_adjusted_3 = QtCore.QPoint(pos.x() - 610, pos.y() - 390) 
            if self.graphicsView_3.viewport().rect().contains(pos_adjusted_3):
                if(event.angleDelta().y()>0.5):
                    self.graphicsView_3.scale(1.5,1.5)
                elif(event.angleDelta().y()< 0.5):
                    self.graphicsView_3.scale(1 /1.5,1 / 1.5)

            pos_adjusted_4 = QtCore.QPoint(pos.x() - 1100, pos.y() - 60) 
            if self.graphicsView_4.viewport().rect().contains(pos_adjusted_4):
                if(event.angleDelta().y()>0.5):
                    self.graphicsView_4.scale(1.5,1.5)
                elif(event.angleDelta().y()< 0.5):
                    self.graphicsView_4.scale(1 /1.5,1 / 1.5)    
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return


    def grayscale(self):
        try:
            self.gray_img = grayscale_func(self.crop_result)
            pixmap_result = self.numpy_to_pixmap(self.gray_img)
            pixmap_result_item = QGraphicsPixmapItem(pixmap_result)
            self.scene_2.clear()
            self.scene_2.addItem(pixmap_result_item)
            self.graphicsView_2.setScene(self.scene_2)
            self.graphicsView_2.fitInView(self.graphicsView_2.sceneRect(), Qt.KeepAspectRatio)
            self.pushButton_7.setEnabled(True)
            self.pushButton_11.setEnabled(True)
            self.radioButton_3.setEnabled(True)
            self.radioButton_4.setEnabled(True)

        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return


    def enhancement(self):
        try:
            self.gray_img=enhancement_func(self.gray_img)
            pixmap_result = self.numpy_to_pixmap(self.gray_img)
            pixmap_result_item = QGraphicsPixmapItem(pixmap_result)
            self.scene_2.clear()
            self.scene_2.addItem(pixmap_result_item)
            self.graphicsView_2.setScene(self.scene_2)
            self.graphicsView_2.fitInView(self.graphicsView_2.sceneRect(), Qt.KeepAspectRatio)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def units_set(self):
        try:
            selectedButton =self.buttonGroup.checkedButton()
            id=selectedButton.text()
            # print(id)
            if (id=='mm'):
                self.unit=1
            elif (id=='inch'):
                self.unit=2
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def method_set(self):
        try:
            selectedButton =self.buttonGroup_2.checkedButton()
            id=selectedButton.text()
            # print(id)
            if (id=='Image Binarization'):
                self.pushButton_11.setEnabled(True)
                self.pushButton_12.setEnabled(True)
                self.pushButton_13.setEnabled(True)
                self.pushButton_14.setEnabled(False)
            elif (id=='Edge Detection'):
                self.pushButton_11.setEnabled(False)
                self.pushButton_12.setEnabled(False)
                self.pushButton_13.setEnabled(False)
                self.pushButton_14.setEnabled(True)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def binarization(self):
        try:
            self.bin = binarize_func(self.gray_img)
            self.bin = cv2.bitwise_not(self.bin)
            pixmap_result = self.numpy_to_pixmap(self.bin)
            pixmap_result_item = QGraphicsPixmapItem(pixmap_result)
            self.scene_3.clear()
            self.scene_3.addItem(pixmap_result_item)
            self.graphicsView_3.setScene(self.scene_3)
            self.graphicsView_3.fitInView(self.graphicsView_3.sceneRect(), Qt.KeepAspectRatio)
            self.graphicsView_4.setScene(self.scene_3)
            self.graphicsView_4.fitInView(self.graphicsView_4.sceneRect(), Qt.KeepAspectRatio)
            self.pushButton_12.setEnabled(True)
            self.pushButton_13.setEnabled(True)
            # self.pushButton_14.setEnabled(True)
            self.pushButton_15.setEnabled(True)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def corrosion(self):
        try:
            circle=self.textEdit_6.toPlainText()
            circle=int(circle)
            self.bin=corrosion_func(self.bin,circle)
            pixmap_result = self.numpy_to_pixmap(self.bin)
            pixmap_result_item = QGraphicsPixmapItem(pixmap_result)
            self.scene_3.clear()
            self.scene_3.addItem(pixmap_result_item)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return


    def dilation(self):
        try:
            self.bin = dilation_func(self.bin)
            pixmap_result = self.numpy_to_pixmap(self.bin)
            pixmap_result_item = QGraphicsPixmapItem(pixmap_result)
            self.scene_3.clear()
            self.scene_3.addItem(pixmap_result_item)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def chain_code(self):
        try:
            scene_rect = self.scene_3.sceneRect()
            pixmap = QPixmap(scene_rect.size().toSize())
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            self.scene_3.render(painter, QRectF(pixmap.rect()), scene_rect)
            painter.end()
            image = pixmap.toImage()
            image.save("scene_image.png")
            # print("Image saved")
            
            self.bin = cv2.imread("scene_image.png",cv2.IMREAD_GRAYSCALE)
            # self.bin = self.bin[:,:,0]
            contours, _ = cv2.findContours(self.bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                max_contour = max(contours, key=cv2.contourArea)
                max_contour=np.reshape(max_contour, (max_contour.shape[0], max_contour.shape[2]))        
                # print(max_contour[0][0])
                result_image = np.zeros_like(self.bin)
                # print(self.bin.shape)
                cv2.drawContours(result_image, [max_contour], -1, 255, thickness=1)
                cv2.imwrite('result_image.png',result_image)
                max_contour[:, [0, 1]] = max_contour[:, [1, 0]]
                self.boundary=max_contour
                self.chaincode,oringin = gui_chain_code_func(result_image,max_contour[0])
                # print(self.chaincode.shape)

                # Check if chain_code is not empty
                if len(self.chaincode) == 0:
                    QMessageBox.warning(self, "Warning", "Chain code is empty")
                    return

                # Draw green line for boundary
                pen = QPen(Qt.green, 3)
                # print(self.boundary)
                for i in range(len(self.boundary)-1):
                    start_point = QPointF(self.boundary[i][1], self.boundary[i][0])
                    end_point = QPointF(self.boundary[i + 1][1], self.boundary[i + 1][0])
                    line_item_1 = QGraphicsLineItem(start_point.x(), start_point.y(), end_point.x(), end_point.y())
                    line_item_1.setPen(pen)
                    self.scene_3.addItem(line_item_1)

                x_ = calc_traversal_dist(self.chaincode)
                x = np.vstack(([0, 0], x_))
                # print(x)

                # # Draw red line for chain code traversal
                pen.setColor(Qt.red)
                pen.setWidth(2)
                origin = self.boundary[0]
                current_point = QPointF(origin[1],origin[0])
                for move in x:
                    next_point = QPointF(origin[1] + move[0],origin[0]  - move[1])
                    # print(next_point)
                    line_item = QGraphicsLineItem(current_point.x(), current_point.y(), next_point.x(), next_point.y())
                    line_item.setPen(pen)
                    self.scene_3.addItem(line_item)
                    current_point = next_point                    
                is_closed,endpoint = is_completed_chain_code(self.chaincode, self.boundary[0])
                self.graphicsView_4.fitInView(self.graphicsView_4.sceneRect(), Qt.KeepAspectRatio)
                # Get the current transform
                transform = self.graphicsView_4.transform()
                # Apply the scale transformation
                transform.scale(7, 7)
                self.graphicsView_4.setTransform(transform)
                # Center the view on the specified point
                self.graphicsView_4.centerOn(QPointF(endpoint[1],endpoint[0]))

                if not is_closed:
                    QMessageBox.critical(None, "Error", f"Chain code is not closed (length is {self.chaincode.shape[0]}), please edit.")

                else:
                    QMessageBox.information(None, "Success", f"Chain code is closed, and length is {self.chaincode.shape[0]}")               
                    # print(self.chaincode)
                    # print(self.chaincode.shape)
                    self.pushButton_9.setEnabled(True)
                    self.pushButton_10.setEnabled(True)
                    
            else:
                # print("not found boundary")
                QMessageBox.warning(self, "Warning", "not found boundary")
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def functions_selection(self):
        try:
            selected_item = self.comboBox_2.currentText()
            min_value = self.horizontalSlider.minimum()
            max_value = self.horizontalSlider.maximum()
            current_value = self.horizontalSlider.value()
            threshvalue = 255*(current_value-min_value)/(max_value-min_value)
            if selected_item=="canny":
                self.bin=contour_extraction_func(self.gray_img,1,threshvalue/2,threshvalue)
            elif selected_item=="sobel":
                self.bin=contour_extraction_func(self.gray_img,2,threshvalue/2,threshvalue)
            elif selected_item=="zerocross":
                self.bin=contour_extraction_func(self.gray_img,3,threshvalue/2,threshvalue)   
            elif selected_item=="laplace":
                self.bin=contour_extraction_func(self.gray_img,4,threshvalue/2,threshvalue)    
            elif selected_item=="Roberts":
                self.bin=contour_extraction_func(self.gray_img,5,threshvalue/2,threshvalue)  
            elif selected_item=="Prewitt":
                self.bin=contour_extraction_func(self.gray_img,6,threshvalue/2,threshvalue) 
            else:
                QMessageBox.warning(self, 'Error', 'Please select the an operator') 
                return

            pixmap_result = self.numpy_to_pixmap(self.bin)
            pixmap_result_item = QGraphicsPixmapItem(pixmap_result)
            self.scene_3.clear()
            self.scene_3.addItem(pixmap_result_item) 
            self.graphicsView_3.setScene(self.scene_3)
            self.graphicsView_3.fitInView(self.graphicsView_3.sceneRect(), Qt.KeepAspectRatio)
            self.graphicsView_4.setScene(self.scene_3)
            self.graphicsView_4.fitInView(self.graphicsView_4.sceneRect(), Qt.KeepAspectRatio) 
            self.pushButton_15.setEnabled(True)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def clicked_point(self):
        self.flag_point=1
        self.pushButton_16.setEnabled(True)

    def save(self):
        if self.textEdit_7.toPlainText():
            id_full = self.textEdit_7.toPlainText()
            self.id_full = id_full
            self.filename = self.image_files[self.c_index]

            if not os.path.exists('results'):
                os.makedirs('results')
            if not os.path.exists('label'):
                os.makedirs('label')
            # Writing boundary data to file
            boundary_filename = f"results/{self.filename[:-4]}_{id_full}_b.txt"

            write_data_to_file(self.boundary, boundary_filename)

            # Writing chain code data to file
            chain_filename = f"results/{self.filename[:-4]}_{id_full}_c.txt"
            write_data_to_file(self.chaincode, chain_filename)

            # Writing image to file
            image_filename = f"label/{self.filename[:-4]}_{id_full}.png"
            cv2.imwrite(image_filename,self.bin)
            
            try:
                # Processing distance data
                dis = float(self.textEdit_5.toPlainText())
                if dis>0:
                    dis_pixel = self.distance / dis
                    dis_mm = dis / self.distance
                else:
                    dis_pixel=0
                    dis_mm=0
                [area,circumference]=cal_area_c(self.chaincode,self.boundary)


                # Writing results to Excel file
                if self.unit==1:
                    results = {
                        'filepath': [f"{self.filename[:-4]}_{id_full}"],
                        'scale:pixels/mm': [dis_pixel],
                        'scale:mm/pixel': [dis_mm],
                        'circumference:pixel': [circumference],  
                        'area:pixel': [area],  # Example calculation
                        'circumference:mm': [circumference * dis_mm],  # Example calculation
                        'area:mm^2': [area * dis_mm ** 2],  # Example calculation
                    }
                elif self.unit==2:
                    results = {
                        'filepath': [f"{self.filename[:-4]}_{id_full}"],
                        'scale:pixels/inch': [dis_pixel],
                        'scale:inch/pixel': [dis_mm],
                        'circumference:pixel': [circumference],  
                        'area:pixel': [area],  # Example calculation
                        'circumference:inch': [circumference * dis_mm],  # Example calculation
                        'area:inch^2': [area * dis_mm ** 2],  # Example calculation
                    }
                df = pd.DataFrame(results)
                df.to_excel(f"results/{self.filename[:-4]}_{id_full}_info.xlsx", index=False,sheet_name='Sheet1')
                QMessageBox.information(None, "Success",'    done!   ')
                self.pushButton_17.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(None, "Error", str(e))
        else:
            # print('Chain code is null. /Chain code is not closed.')
            QMessageBox.warning(self, 'Error', 'Chain code is null. /Chain code is not closed.')      
        


    def go_to_window2(self):
        # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        try:
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
            self.window2 = MainWindow_1(self.chaincode,self.filename,self.id_full)
            self.window2.show()
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

    def skip(self):
        try:
            self.graphicsView.points.append((0,0))
            self.graphicsView.points.append((0,0))

            # print(self.points)

            self.distance = 0
            self.textEdit_5.setText(str(0))
            self.pushButton_16.setEnabled(True)
        except ValueError as e:
            QMessageBox.warning(self,'Error','{e}')
            return

def main():
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_DisableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    Main_Window = MainWindow()
    Main_Window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
