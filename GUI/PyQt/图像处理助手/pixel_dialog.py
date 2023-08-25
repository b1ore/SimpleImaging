from Ui_dialog_pixels import Ui_Dialog
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal, QObject

class Mydialog(Ui_Dialog, QDialog):
    

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.row_lineEdit.setText(str(4))
        self.col_lineEdit.setText(str(4))
        self.rows = 4
        self.cols = 4

    def set_pixels(self):
        self.rows = int(self.row_lineEdit.text())
        self.cols = int(self.col_lineEdit.text())
        

    
class MydialogObject(QObject):
    #This object is to solve the thread problem
    _row_pixel = pyqtSignal(int)
    _col_pixel = pyqtSignal(int)
    _setting_finished = pyqtSignal(int)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.mydialog = Mydialog()


    def set_pixels(self):
        self.mydialog.set_pixels()
        self._row_pixel.emit(self.mydialog.rows)
        self._col_pixel.emit(self.mydialog.cols)
        self._setting_finished.emit(1)
        