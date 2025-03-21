import sys
import os, time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QIcon,QFont, QMovie

from PyQt5.QtWidgets import QGraphicsScene,QGraphicsPixmapItem
from PyQt5.QtCore import Qt  # Import Qt for alignment
from .interactive.myUtils import CustomGraphicsView
from .layouts import Timing      
from .utilities.devThread import Command
import numpy as np
from .utils import to_si_prefix
import pyqtgraph as pg

class Expt(QtWidgets.QWidget, Timing.Ui_Form):
    def __init__(self, device, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.splitter.setSizes([1,1])
        self.last_counts = 0
        self.start_time = time.time()
        self.current_position=0
        self.repeat = False
        self.busy = False
        self.curve= self.plot.plot()
        self.curveData = []
        self.curve.setPen(pg.mkPen(color='r', width=2))
        self.plot.setClipToView(True)

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

        self.showMessage = kwargs.get('showMessage',print)

        if 'set_status_function' in kwargs:
            self.set_status_function(kwargs['set_status_function'])


        image_widget = QtWidgets.QWidget()  # Placeholder for the image        

        self.scene = QGraphicsScene(self)
        self.view = CustomGraphicsView(self.scene)
        self.view.setFrameShape(QtWidgets.QFrame.NoFrame)  # Remove the frame border

        imagepath = os.path.join(os.path.dirname(__file__),'interactive/timings.jpeg')
        mypxmp = QPixmap(imagepath)
        myimg = QGraphicsPixmapItem(mypxmp)
        myimg.setTransformationMode(Qt.SmoothTransformation)
        self.scene.addItem(myimg)

        self.imageLayout.addWidget(self.view)

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

    def setCommandType(self,i):
        command_string = ['r2r','f2f','f2r','r2f','s2r','s2f','c2r','c2f'][i]
        if command_string in ['r2r','f2f','f2r','r2f']:
            self.IN1Box.clear()
            self.IN1Box.addItems(['SEN','IN2'])
            self.IN1Box.setCurrentIndex(0)
        elif command_string in ['s2r','s2f','c2r','c2f']:
            self.IN1Box.clear()
            self.IN1Box.addItems(['OD1','SQR1','SQR2'])
            self.IN1Box.setCurrentIndex(0)
            self.modifyOutputs(1)

    def modifyOutputs(self,i=1):
        cmd = self.commandBox.currentIndex()
        i1 = self.IN1Box.currentIndex()
        if cmd == 6 or cmd == 7: #Set Output HIGH commands
            if i1 == 0: #OD1
                self.OD1Box.setChecked(True)
                self.scope_thread.add_command(Command('set_state',{'OD1':True}))
            elif i1 == 1: #SQR1
                self.SQ1Box.setChecked(True)
                self.scope_thread.add_command(Command('set_state',{'SQ1':True}))
            elif i1 == 2: #SQR2
                self.SQ2Box.setChecked(True)
                self.scope_thread.add_command(Command('set_state',{'SQ2':True}))
        elif cmd == 4 or cmd == 5: #Set Output LOW commands
            if i1 == 0: #OD1
                self.OD1Box.setChecked(False)
                self.scope_thread.add_command(Command('set_state',{'OD1':False}))
            elif i1 == 1: #SQR1
                self.SQ1Box.setChecked(False)
                self.scope_thread.add_command(Command('set_state',{'SQ1':False}))
            elif i1 == 2: #SQR2
                self.SQ2Box.setChecked(False)
                self.scope_thread.add_command(Command('set_state',{'SQ2':False}))

    def makeMeasurement(self):
        if self.busy: return
        self.busy = True
        if self.repeat:
            self.curve.clear()
            self.curveData = []
        self.__makeMeasurement__()

    def __makeMeasurement__(self):
        i1 = self.IN1Box.currentIndex()
        i2 = self.IN2Box.currentIndex()

        command = self.commandBox.currentIndex()
        command_string = ['r2r','f2f','f2r','r2f','s2r','s2f','c2r','c2f'][command]
        if command_string in ['r2r','f2f','f2r','r2f']:
            src = ['SEN','IN2'][i1]
        else:
            src = ['OD1','SQR1','SQR2'][i1]

        dst = ['SEN','IN2'][i2]
        self.scope_thread.add_command(Command('timing',{'command':command_string,'src':src,'dst':dst,'timeout':self.timeoutBox.value()}))

        self.loading_label.setVisible(True)  # show the loading icon
        self.loading_movie.start()  # Start the spinning animation

    def set_status_function(self,func):
        self.showMessage = func

    def onoff_sqr1(self,state):
        self.scope_thread.add_command(Command('set_state',{'SQ1':state}))

    def onoff_sqr2(self,state):
        self.scope_thread.add_command(Command('set_state',{'SQ2':state}))

    def onoff_od1(self,state):
        self.scope_thread.add_command(Command('set_state',{'OD1':state}))


    def updateTiming(self,interval):
        self.busy = False
        self.loading_label.setVisible(False)  # hide the loading icon
        self.loading_movie.stop()  # Stop the spinning animation
        self.modifyOutputs(0)
        if interval > 0:
            self.resultLabel.setText(to_si_prefix(interval,precision=3,unit='S'))
            if self.repeat:
                self.curveData.append(interval)
                self.curve.setData(np.arange(len(self.curveData)),self.curveData)
                self.__makeMeasurement__()
            else:
                self.addEntry(interval)
        else:
            self.resultLabel.setText('Timeout')

    def setRepeat(self,state):
        self.repeat = state

    def set_sqr1(self):
        f = self.sqr1_freq.value()
        dc = self.sqr1_dc.value()
        self.scope_thread.add_command(Command('set_sqr1',{'frequency':f,'duty_cycle':dc}))
        self.SQ1Box.blockSignals(True)
        if f == 0:
            self.sqr1_label.setText('SQR1 Frequency : ALWAYS ON')
            self.SQ1Box.setChecked(True)
        else:
            self.sqr1_label.setText(f'SQR1 Frequency ( 0 = ALWAYS ON) : {f} Hz, : {dc}%')
            self.SQ1Box.setChecked(False)
        self.SQ1Box.blockSignals(False)
