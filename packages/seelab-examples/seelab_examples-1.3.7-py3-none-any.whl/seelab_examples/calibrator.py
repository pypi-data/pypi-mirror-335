import sys
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap  # Import QPixmap for image handling
from PyQt5.QtWidgets import QGraphicsScene,QGraphicsPixmapItem, QLabel,QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt

from .utilities.IOWidget import MINIINPUT  # Import Qt for alignment
from .layouts.gauge import Gauge
from .layouts import ui_calibrator
from .interactive.myUtils import CustomGraphicsView
from .utilities.devThread import Command, SCOPESTATES
import numpy as np
class Expt(QtWidgets.QWidget, ui_calibrator.Ui_Form ):
    def __init__(self, device, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.device = device  # Device handler passed to the Expt class.
        if not self.device.calibrated:
            self.calibrationTitle.setText('Device not calibrated')
            self.calibrationTitle.setStyleSheet('color:red;')
        else:
            self.populate_qtable(self.device.aboutArray)


    def populate_qtable(self, data):
        row_count = len(data)
        col_count = max(len(row) if isinstance(row, list) else 1 for row in data)
        self.calibrationTable.setRowCount(row_count)
        self.calibrationTable.setColumnCount(col_count)
        
        for row_idx, row in enumerate(data):
            if isinstance(row, list):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.calibrationTable.setItem(row_idx, col_idx, item)
            else:
                item = QTableWidgetItem(str(row))
                self.calibrationTable.setItem(row_idx, 0, item)
        
        self.calibrationTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def saveCalibrationFile(self):
        pass

    def readCalibrationFile(self):
        pass


    def readCalibrationDevice(self):
        pass


    def saveCalibrationDevice(self):
        pass



# This section is necessary for running new.py as a standalone program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Expt(None)  # Pass None for the device in standalone mode
    window.show()
    sys.exit(app.exec_()) 