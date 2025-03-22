import sys
import os, time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QIcon,QFont, QMovie, QKeySequence

from PyQt5.QtWidgets import QGraphicsScene,QGraphicsPixmapItem
from PyQt5.QtCore import Qt  # Import Qt for alignment
from .interactive.myUtils import CustomGraphicsView
from .layouts import time_of_flight      
from .utilities.devThread import Command
import numpy as np
from .utils import to_si_prefix
import pyqtgraph as pg

class Expt(QtWidgets.QWidget, time_of_flight.Ui_Form):
    def __init__(self, device, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.splitter.setSizes([1,1])
        self.last_counts = 0
        self.start_time = time.time()
        self.current_position=0
        self.busy = False
        self.curve= self.plot.plot()
        self.plot.setYRange(0,3.5)
        self.curveData = np.zeros(100)
        self.curve.setPen(pg.mkPen(color='r', width=2))
        self.plot.setClipToView(True)
        self.od1_state = 0
        self.sen_state = 1
        self.measurementFunction = 's2f'


        spingif = os.path.join(os.path.dirname(__file__),'interactive/spin.gif')
        self.loading_label.setScaledContents(True)  
        self.loading_movie = QMovie(spingif)  # Path to your spinning icon
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setVisible(False)  # Initially hidden

        self.scope_thread = None
        if 'scope_thread' in kwargs:
            self.scope_thread = kwargs['scope_thread']
            self.scope_thread.add_command(Command('set_sqr1',{'frequency':1000,'duty_cycle':0.5}))
            self.scope_thread.timing_ready.connect(self.updateTiming)
            self.scope_thread.voltage_ready.connect(self.updateVolts)

        self.showMessage = kwargs.get('showMessage',print)

        if 'set_status_function' in kwargs:
            self.set_status_function(kwargs['set_status_function'])


        image_widget = QtWidgets.QWidget()  # Placeholder for the image        

        self.scene = QGraphicsScene(self)
        self.view = CustomGraphicsView(self.scene)
        self.view.setFrameShape(QtWidgets.QFrame.NoFrame)  # Remove the frame border

        imagepath = os.path.join(os.path.dirname(__file__),'interactive/Gravity Using Time of Flight.png')
        mypxmp = QPixmap(imagepath)
        myimg = QGraphicsPixmapItem(mypxmp)
        myimg.setTransformationMode(Qt.SmoothTransformation)
        self.scene.addItem(myimg)

        self.imageLayout.addWidget(self.view)

        # Create a QTimer for periodic voltage measurement
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.fetch_sen)  # Connect the timeout signal to the update method
        self.timer.start(20)  # Start the timer with ms interval

    def fetch_sen(self):
        if self.busy: return
        self.scope_thread.add_command(Command('get_voltage',{'channel':'SEN'}))

    def updateVolts(self,channel,volts):
        if channel == 'SEN':
            if volts>2.5:
                self.senLabel.setText(f'SEN: HIGH {volts:.1f} V')
                self.sen_state = 1
            else:
                self.senLabel.setText(f'SEN: LOW {volts:.1f} V')
                self.sen_state = 0
            self.curveData[:-1] = self.curveData[1:]
            self.curveData[-1] = volts
            self.curve.setData(self.curveData)
            self.updateMeasurementFunction()

    def updateMeasurementFunction(self):
        if self.od1_state == 1 and self.sen_state == 1:
            self.measurementFunction = 'c2f'
        elif self.od1_state == 1 and self.sen_state == 0:
            self.measurementFunction = 'c2r'
        elif self.od1_state == 0 and self.sen_state == 1:
            self.measurementFunction = 's2f'
        elif self.od1_state == 0 and self.sen_state == 0:
            self.measurementFunction = 's2r'
        Functions = {'c2f':'Clear OD1 To Fall SEN','c2r':'Clear OD1 To Rise SEN','s2f':'Set OD1 To Fall SEN','s2r':'Set OD1 To Rise SEN'}
        self.funcLabel.setText(Functions[self.measurementFunction])

    def clearIt(self):
        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, 0)
            if item is None:
                item = QtWidgets.QTableWidgetItem()  # Create a new QTableWidgetItem
                self.tableWidget.setItem(row, 0, item)  # Set the new item in the table
            self.tableWidget.item(row, 0).setText("")  # Clear the contents of each cell
        self.current_position = 0

    def addEntry(self,value):
        item = self.tableWidget.item(self.current_position, 0)
        if item is None:
            item = QtWidgets.QTableWidgetItem()  # Create a new QTableWidgetItem
            self.tableWidget.setItem(self.current_position, 0, item)  # Set the new item in the table

        self.tableWidget.item(self.current_position, 0).setText(f'{value:.3e}')
        self.current_position += 1

    def onoff_od1(self,state):
        self.scope_thread.add_command(Command('set_state',{'OD1':state}))
        self.od1_state = state


    def toggle_od1(self):
        self.OD1Box.setChecked(not self.OD1Box.isChecked())
        self.onoff_od1(self.OD1Box.isChecked())



    def makeMeasurement(self):
        if self.busy: return
        self.busy = True
        self.toggle_od1()
        self.__makeMeasurement__()

    def __makeMeasurement__(self):
        self.scope_thread.add_command(Command('timing',{'command':self.measurementFunction,'src':'OD1','dst':'SEN','timeout':2}))
        self.loading_label.setVisible(True)  # show the loading icon
        self.loading_movie.start()  # Start the spinning animation


    def updateTiming(self,interval):
        interval -= 0.003 # 3mS subtracted to account for magnetism persistence delay of the electromagnet
        self.busy = False
        self.loading_label.setVisible(False)  # hide the loading icon
        self.loading_movie.stop()  # Stop the spinning animation
        if interval > 0:
            self.resultLabel.setText(to_si_prefix(interval,precision=3,unit='S'))
            self.addEntry(interval)
        else:
            self.resultLabel.setText('Timeout')
        self.toggle_od1()


    def set_status_function(self,func):
        self.showMessage = func



