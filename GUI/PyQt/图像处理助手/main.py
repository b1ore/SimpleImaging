import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from Ui_imaging import Ui_MainWindow
import serial
import serial.tools.list_ports as list_ports
from pixel_dialog import MydialogObject
from painter import PainterObject
import socket
import time
import icon_rc

class Mythread(QThread):
    _update_time = pyqtSignal(int)

    def __init__(self, sleepTime, parent=None) -> None:
        super().__init__(parent)
        self.sleepTime = sleepTime
    def run(self):
        while 1:
            self._update_time.emit(1)
            time.sleep(self.sleepTime)
            

class MyMainWindow(QMainWindow, Ui_MainWindow):  # 继承 QMainWindow 类和 Ui_MainWindow 界面类
    
    _pixel_data_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent) #初始化父类
        self.setupUi(self)  # 继承 Ui_MainWindow 界面类
        #window setting
        self.setFixedSize(800, 680)

        #icon settings
        icon_update = QtGui.QIcon()
        icon_update.addPixmap(QtGui.QPixmap(":/updates.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.update_button.setIcon(icon_update)

        icon_mainWindow = QtGui.QIcon()
        icon_mainWindow.addPixmap(QtGui.QPixmap(":/semiconductor.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon_mainWindow)

        icon_helper = QtGui.QIcon()
        icon_helper.addPixmap(QtGui.QPixmap(":/About.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionconsult_help.setIcon(icon_helper)

        self.serialPort = serial.Serial()
        self.client = None
        self.dialog = None
        self.painter = None    

        #some parameters for wifi AP
        self.localIP = "192.168.4.2" #str
        self.localPort = 12000 #int
        self.remoteIP = "192.168.4.1" #str
        self.remotePort = 80 #int
        self.localIP_editline.setText(self.localIP)
        self.localPort_editline.setText(str(self.localPort))
        self.remoteIP_editline.setText(self.remoteIP)
        self.remotePort_editline.setText(str(self.remotePort))
        self.isConnected = False

        #some parameters for port
        self.portx = ""
        self.bautrate = 115200
        self.timex = 4
        self.byteSize = serial.EIGHTBITS
        self.stopbit = serial.STOPBITS_ONE
        self.parity = serial.PARITY_NONE

        self.byteList = {"8": serial.EIGHTBITS, "5": serial.FIVEBITS, "6": serial.SIXBITS,
        "7": serial.SEVENBITS}
        self.parityList = {"None": serial.PARITY_NONE, "EVEN": serial.PARITY_EVEN,
        "ODD": serial.PARITY_ODD}
        self.stopbitsList = {"1": serial.STOPBITS_ONE, "1.5": serial.STOPBITS_ONE_POINT_FIVE,
        "2": serial.STOPBITS_TWO}

        #some initializations
        self.initialize_port()
        self.initialize_baut()
        self.initialize_bytesize()
        self.initialize_parity()
        self.initialize_stopbit()
        
        #threads
        self.recvThread = Mythread(0.005)
        self.recvThread._update_time.connect(self.recv_data)

        #parameters about info window
        self.recv_row = 1

        #parameters about sending data
        self.isNewLine = False

        #parameters about pixel dialog
        self.pixel_dialog = MydialogObject()
        self.pixelThread = QThread()
        self.pixel_dialog.moveToThread(self.pixelThread)
        self.pixelThread.started.connect(self.pixel_dialog.mydialog.show)
        self.pixel_dialog.mydialog.accepted.connect(self.pixel_dialog.set_pixels)
        self.pixel_dialog.mydialog.rejected.connect(self.pixelThread.terminate)
        self.pixel_dialog._setting_finished.connect(self.pixelThread.terminate)
        self.pixel_dialog._row_pixel.connect(self._update_row_pixel)
        self.pixel_dialog._col_pixel.connect(self._update_col_pixel)
        self.rows = 4
        self.cols = 4

        #parameters about imaging
        self.painter = PainterObject(self.rows, self.cols)
        self.painterThread = QThread()
        self.painter.moveToThread(self.painterThread)
        self._pixel_data_signal.connect(self.painter.parseData)
        self.pixel_dialog._setting_finished.connect(self._update_pixel_setting)

        self.painterThread.started.connect(self.painter.painter.show)

        self.painter._thread_terminate_signal.connect(self.painterThread.terminate)
        

        self.painter._save_picture_signal.connect(self._save_picture)
        self.painter._save_data_signal.connect(self._save_data)

        #button management
        self.save_button.clicked.connect(self.painter.saveFig)
        self.file_button.clicked.connect(self.painter.saveFile)
        self.image_button.clicked.connect(self.click_image)

    def closeEvent(self, e):
        result = QMessageBox.question(self, "Confirmation of Exit", "Do you want to exit?", QMessageBox.Yes | QMessageBox.No)
        if(result == QMessageBox.Yes):
            e.accept()
        else:
            e.ignore()

    #-------------------------------initialization functions-----------------------
    def initialize_port(self):
        self.port_comboBox.clear()
        ListPorts = list(list_ports.comports())
        ListPorts = [str(i[0]) for i in ListPorts]
        if len(ListPorts):
            self.port_comboBox.addItems(ListPorts)
            self.port_comboBox.setCurrentIndex(0)
            self.portx = self.port_comboBox.currentText()

    def initialize_baut(self):
        self.baut_comboBox.clear()
        ListBaut = ["50", "75", "110", "134", "150", "200", "300",
        "600", "1200", "1800", "2400", "4800", "9600", "19200", "38400",
        "57600", "115200"]
        self.baut_comboBox.addItems(ListBaut)
        self.baut_comboBox.setCurrentIndex(len(ListBaut)-1)
        self.bautrate = int(self.baut_comboBox.currentText())

    def initialize_bytesize(self):
        self.dataBit_comboBox.clear()
        self.dataBit_comboBox.addItems(self.byteList.keys())
        self.dataBit_comboBox.setCurrentIndex(0)
        self.byteSize = self.byteList[self.dataBit_comboBox.currentText()]

    def initialize_parity(self):
        self.parity_comboBox.clear()
        self.parity_comboBox.addItems(self.parityList.keys())
        self.parity_comboBox.setCurrentIndex(0)
        self.parity = self.parityList[self.parity_comboBox.currentText()]

    def initialize_stopbit(self):
        self.stopBit_comboBox.clear()
        self.stopBit_comboBox.addItems(self.stopbitsList.keys())
        self.stopBit_comboBox.setCurrentIndex(0)
        self.stopbit = self.stopbitsList[self.stopBit_comboBox.currentText()]

    #--------------------------tool functions--------------------------------------
    def printf(self, st):
        if self.recv_row > 10000:
            self.recv_row = 1
            self.plainTextEdit_1.clear()
        self.plainTextEdit_1.appendPlainText("{} {}".format(self.recv_row, st))
        self.recv_row += 1
        return
    
    def recv_data(self, sec):
        res = ""
        if self.isConnected:
            #no blocking mode
            try:
                res = self.client.recv(1024).decode("utf-8")
                if res:
                    self.printf(res)
            except BlockingIOError as e:
                pass
        elif self.serialPort.isOpen():
            if self.serialPort.in_waiting == 0:
                return
            res = self.serialPort.read_all()
            try:
                res = res.decode("utf-8")
            except: #遭遇非UTF-8字符
                return
            if res:
                self.printf(res)
        if self.painterThread.isRunning():
            self._pixel_data_signal.emit(res)
        return

    def _update_row_pixel(self, rows):
        self.rows = rows
        self.printf("Row pixels: {}".format(self.rows))

    def _update_col_pixel(self, cols):
        self.cols = cols
        self.printf("Col pixels: {}".format(self.cols))

    def _update_pixel_setting(self):
        self.painterThread.start()
        self.painter.setRowAndCol(self.rows, self.cols)

    def _save_picture(self, st):
        self.printf("Succeeded in saving the picture:\n {}".format(st))

    def _save_data(self, st):
        self.printf("Succeeded in saving the file:\n {}".format(st))

    #--------------------------slot functions---------------------------------------
    def set_local_ip(self):
        self.localIP = self.localIP_editline.text()
        if self.check_ip_format(self.localIP) == False:
            #这里可以弹出消息框提醒
            self.localIP = "192.168.4.2"
            self.printf("IP地址格式错误")
            self.localIP_editline.setText(self.localIP)

    def set_local_port(self):
        try:
            self.localPort = int(self.localPort_editline.text())
        except:
            self.printf("本地端口为无效端口")
            self.localPort = 12000
            self.localPort_editline.setText(str(self.localPort))

    def set_remote_ip(self):
        self.remoteIP = self.remoteIP_editline.text()
        if self.check_ip_format(self.remoteIP) == False:
            #这里可以弹出消息框提醒
            self.printf("IP地址格式错误")
            self.remoteIP = "192.168.4.1"
            self.remoteIP_editline.setText(self.remoteIP)

    def set_remote_port(self):
        try:
            self.remotePort = int(self.remotePort_editline.text())
        except:
            self.printf("远程端口为无效端口")
            self.remotePort = 80
            self.remotePort_editline.setText(str(self.remotePort))

    def check_ip_format(self, st):
        return True
    
    def set_port(self):
        self.portx = self.port_comboBox.currentText()
        self.printf("Current portx is {}".format(self.port_comboBox.currentText()))
        return
    
    def set_bautrate(self):
        self.bautrate = int(self.baut_comboBox.currentText())
        self.printf("Current bautrate is {}".format(self.baut_comboBox.currentText()))
        return

    def set_stopbit(self):
        self.stopbit = self.stopbitsList[self.stopBit_comboBox.currentText()]
        self.printf("Current Stop Bit is {}".format(self.stopBit_comboBox.currentText()))
        return
    
    def set_databit(self):
        self.byteSize = self.byteList[self.dataBit_comboBox.currentText()]
        self.printf("Current bytesize is {}".format(self.dataBit_comboBox.currentText()))
        return

    def set_parity(self):
        self.parity = self.parityList[self.parity_comboBox.currentText()]
        self.printf("Current paritybit is {}".format(self.parity_comboBox.currentText()))
        return
    
    def set_newline(self):
        if self.checkBox.isChecked():
            self.isNewLine = True
        else:
            self.isNewLine = False
        return 

    def consult_help(self):
        return

    def click_openPort(self): # disconnect wifi ap 
        if not self.serialPort.isOpen():
            if self.client != None:
                self.client.close()
                self.client = None
                self.isConnected = False
                self.printf("WIFI AP is disconnected!")
            if self.portx == "":
                self.printf("当前无可用端口")
                return 
            self.serialPort.port = self.portx
            self.serialPort.baudrate = self.bautrate
            self.serialPort.bytesize = self.byteSize
            self.serialPort.stopbits = self.stopbit
            self.serialPort.parity = self.parity
            self.serialPort.timeout = self.timex
            self.serialPort.open()
            self.printf("成功打开端口 {}".format(self.serialPort.port))
        else:
            self.printf("端口已打开")
        return

    def click_closePort(self):
        if self.serialPort.isOpen():
            self.serialPort.close()
            self.printf("已关闭端口 {}".format(self.serialPort.port))
        else:
            self.printf("当前无可用端口")
        return

    def click_send(self):
        data = self.plainTextEdit_2.toPlainText()
        if len(data) == 0:
            return
        if self.isNewLine:
            data += "\r\n"
        if self.serialPort.isOpen():
            self.serialPort.write(data.encode("utf-8"))
            self.printf("发送成功：{}".format(data))
        if self.isConnected:
            self.client.send(data.encode("utf-8"))
            self.printf("发送成功：{}".format(data))
        return

    def click_clearInput(self):
        self.plainTextEdit_2.clear()
        return

    def click_rece(self):
        if not self.serialPort.isOpen() and not self.isConnected:
            self.printf("请先打开串口或连接上AP")
            return
        self.recvThread.start()    #每10ms读取一次
        self.printf("接收已打开")
        return

    def click_image(self):
        self.pixelThread.start()
        return

    def click_stopRecv(self):
        self.recvThread.quit()
        self.printf("接收已停止")
        return

    def click_listen(self):
        if self.client == None:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.bind((self.localIP, self.localPort))
        try:
            self.client.settimeout(3)
            self.client.connect((self.remoteIP, self.remotePort))
            self.client.settimeout(0)
        except socket.timeout:
            self.client.close()
            self.client = None
            self.isConnected = False
            self.printf("Connection Timeout!")
            return
        except socket.error as e:
            self.client.close()
            self.client = None
            self.isConnected = False
            self.printf("Connection Error: {}".format(e))
            self.printf("若当前端口已被使用，尝试其他端口，例如`12001`等")
            return
        self.printf("成功连接上服务器")
        self.isConnected = True
        return 
    
    def click_disconnect(self):
        if self.client != None:
            self.client.close()
            self.isConnected = False
            self.client = None
            self.printf("已断开与服务器的连接")
        else:
            self.printf("当前没有WIFI AP连接")
        return

    def click_updatePort(self):
        self.initialize_port()

if __name__ == '__main__':
    import cgitb
    cgitb.enable(format='txt', logdir='log')
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)  # 在 QApplication 方法中使用，创建应用程序对象
    myWin = MyMainWindow()  # 实例化 MyMainWindow 类，创建主窗口
    myWin.show()  # 在桌面显示控件 myWin
    sys.exit(app.exec_())  # 结束进程，退出程序

    
    
