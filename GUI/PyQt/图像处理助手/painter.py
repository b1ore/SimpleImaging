
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import (QApplication, QWidget, QMessageBox, QGridLayout) 
from PyQt5.QtCore import pyqtSignal, QObject
import re
import bisect
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import time
from Ui_painter import Ui_Form
import csv

class Painter(QWidget, Ui_Form):
    _painter_terminate_signal = pyqtSignal(int)
    
    def __init__(self, rows, cols, parent=None):
        super(Painter, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('实时成像')
        self.setFixedSize(480,480)
        self.verticalLayoutWidget.setFixedSize(480, 480)


        self.rows = rows
        self.cols = cols
        self.pixels = rows * cols
        self.rectList = np.zeros((self.rows, self.cols, 3))
        

        self.width= 480//cols
        self.height= 480//rows
        pg.setConfigOptions(leftButtonPan=True, antialias=True)
        pg.setConfigOption('imageAxisOrder', 'row-major')
        pg.setConfigOption('background', 'w')
        self.view = self.graphicsView.addViewBox()
        ## Create image item
        self.img = pg.ImageItem(border='w')
        self.view.addItem(self.img)
        # Set initial view bounds
        self.img.setImage(self.rectList)

    def closeEvent(self, e):
        result = QMessageBox.question(self, "Confirmation of Exit", "Do you want to exit?", QMessageBox.Yes | QMessageBox.No)
        if(result == QMessageBox.Yes):
            e.accept()
            self._painter_terminate_signal.emit(1)
        else:
            e.ignore()


    def updateRectList(self, row, col, color):
        for i in range(3):
            self.rectList[self.rows-row-1][col][i] = color[i]
        self.img.setImage(self.rectList)

    def setRowAndCol(self, row, col):
        self.rows = row
        self.cols = col
        self.pixels = row * col
        self.width = 480 // col
        self.height = 480 // row
        self.rectList = np.zeros((self.rows, self.cols, 3))
        self.img.setImage(self.rectList)

class PainterObject(QObject):
    #This object is to solve the thread problem
    _thread_terminate_signal = pyqtSignal(int)
    _save_picture_signal = pyqtSignal(str)
    _save_data_signal = pyqtSignal(str)
    def __init__(self, rows, cols, parent=None) -> None:
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        self.painter = Painter(rows, cols)
        self.painter._painter_terminate_signal.connect(self.terminate)
        self.rgbList = self.generate_rgb_list(51)
        self.boundaryList = self.generate_rgb_boundaries(51, 4096, 0)
        self.valList = np.zeros((self.rows, self.cols), dtype=np.float64)
    def updateRectList(self, row, col, color):
        self.painter.updateRectList(row, col, color)

    def parseData(self, data):
        st_list = self.dataParser(data)
        if len(st_list) == 0:
            return
        for st in st_list:
            row, col, val = st
            if row >= self.painter.rows or col >= self.painter.cols:
                return
            color = self.rgbList[self.findBoundary(self.boundaryList, val)]
            volt = (val / 4096) * 3.3
            self.valList[row][col] = volt
            self.updateRectList(row, col, color)
        return

    def terminate(self):
        self._thread_terminate_signal.emit(1)
       

    def setRowAndCol(self, row, col):
        self.painter.setRowAndCol(row, col)
        self.rows = row
        self.cols = col
        self.valList = np.zeros((self.rows, self.cols), dtype=np.float64)

    #--------------------------some tool funcitions--------------------------------------
    #RGB生成函数
    def generate_rgb_list(self, num):
        """
        num: 区间数量
        return: 一个(0,0,0)格式的列表
        """
        start = 0
        step = 255 // num
        res_tuple = []
        for i in range(num+1):
            res_tuple.append((start, start, start))
            start += step
        return res_tuple

    #二分查找工具函数
    def findBoundary(self, a, x):
        """
        find the first element not less than x in a (all elements in a are unique)
        a: a list
        x: target value
        return: index of the element
        """
        if x >= a[-1]:
            return len(a)-1
        res = bisect.bisect_right(a, x) # return the first element larger than x
        if res > 0 and a[res-1] == x:
            return res-1
        return res

    #边界生成函数
    def generate_rgb_boundaries(self, num, upper_bound, lower_bound):
        """
        num: 区间数量
        upper_bound:
        lower_bound:
        return: a list of length (num+1)
        """
        step = (upper_bound - lower_bound) // num
        return [upper_bound - (num-1-i)*step for i in range(num)]

    #通信语句解析函数
    def dataParser(self, data):
        """
        data: str, should match 'row+col+value\r\nrow+col+value\r\n'
        return: 
        return None if the format of data is wrong
        return (row, col, val)
        """
        da_list = data.split("\r\n")
        st_list = []
        for da in da_list:
            if da == "" or re.fullmatch(r'[0-9]+\+[0-9]+\+[0-9]+', da) == None:
                continue
            temp = da.split('+')
            st_list.append((int(temp[0]), int(temp[1]), int(temp[2])))
        return st_list
    
    def saveFig(self):
        plt.imshow(self.painter.rectList)
        plt.axis('off')
        tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst = time.localtime()
        fig_name = "fig_{}_{}_{}_{}_{}.png".format(tm_year, tm_mon, tm_mday, tm_hour, tm_min)
        plt.savefig(fig_name, dpi=200, bbox_inches="tight", pad_inches=0)
        self._save_picture_signal.emit(fig_name)

    def saveFile(self):
        tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst = time.localtime()
        file_name = "file_{}_{}_{}_{}_{}.csv".format(tm_year, tm_mon, tm_mday, tm_hour, tm_min)
        with open(file_name, "w") as file:
            writer = csv.writer(file, delimiter=',')

            writer.writerow(["Unit: V", "dtype: numpy.float64"])
            writer.writerows(self.valList)
        self._save_data_signal.emit(file_name)

