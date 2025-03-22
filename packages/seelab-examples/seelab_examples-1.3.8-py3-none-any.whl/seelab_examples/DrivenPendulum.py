import sys, time
import numpy as np
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap  # Import QPixmap for image handling
from PyQt5.QtWidgets import QGraphicsScene,QGraphicsPixmapItem
from PyQt5.QtCore import Qt  # Import Qt for alignment
from .layouts.gauge import Gauge
from .interactive.myUtils import CustomGraphicsView
from .utilities.devThread import Command
from .layouts import DrivenPendulum

class Expt(QtWidgets.QFrame, DrivenPendulum.Ui_Form):
    def __init__(self, device, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.device = device  # Device handler passed to the Expt class.

        
        self.scope_thread = None
        self.running = False
        if 'scope_thread' in kwargs:
            self.scope_thread = kwargs['scope_thread']
            self.scope_thread.add_raw_command('set_pv1',{'voltage':0})

        self.gauge_widget = Gauge(self, 'PV1')
        self.gauge_widget.setObjectName('PV1')
        self.gauge_widget.set_MinValue(-5)
        self.max_value = 5
        self.gauge_widget.set_MaxValue(self.max_value)

        self.tp = 1. 
        self.ampL = -5
        self.ampR = 5
        self.symmetric = True
        self.ampLSlider.setVisible(False)
        self.swing = (self.ampR - self.ampL)/2
        self.mid = (self.ampR + self.ampL)/2
        self.function = 0 #0: sine, 1: sawtooth,2: sawtoothR, 3: triangle

        #Graphics
        self.scene = QGraphicsScene(self)
        self.view = CustomGraphicsView(self.scene)
        self.view.setFrameShape(QtWidgets.QFrame.NoFrame)  # Remove the frame border
        imagepath = os.path.join(os.path.dirname(__file__),'interactive/Driven Pendulum.jpg')
        mypxmp = QPixmap(imagepath)
        myimg = QGraphicsPixmapItem(mypxmp)
        myimg.setTransformationMode(Qt.SmoothTransformation)
        self.scene.addItem(myimg)


        self.imageLayout.addWidget(self.view)
        
        self.gaugeLayout.addWidget(self.gauge_widget)
        self.start_time = time.time()
        self.splitter.setSizes([2,1])

        # Create a QTimer for periodic voltage measurement
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_voltage)  # Connect the timeout signal to the update method
        self.timer.start(5)  # Start the timer with a 200ms interval

    def setFunction(self,value):
        self.function = value #0: sine, 1: sawtooth, 2: triangle

    def update_voltage(self):
        phase = (time.time() - self.start_time)%self.tp 
        if self.function == 0:
            v = self.mid + self.swing*np.sin(2*np.pi*phase/self.tp)
        elif self.function == 1:
            v = self.ampL + 2*self.swing*phase/self.tp
        elif self.function == 2:
            v = self.ampR - 2*self.swing*phase/self.tp
        elif self.function == 3:
            v = self.ampL + np.abs(4*self.swing*(phase/self.tp - 0.5))
        self.scope_thread.add_raw_command('set_pv1',{'voltage':v})
        self.gauge_widget.update_value(v)  # Update the gauge with the new voltage value
        
    def setFrequency(self,value):
        self.freqLabel.setText(f'F: {value/1000:.2f} Hz')
        self.tp= 1000./value

    def setSymmetric(self,value):
        self.symmetric = value
        if self.symmetric:
            self.ampR = -self.ampL
            self.ampRSlider.setValue(int(-self.ampL*1000))
            self.ampRSlider.setMinimum(0)
        else:
            self.ampRSlider.setMinimum(-5000)
        self.setAmpLabel()
        self.ampLSlider.setVisible(not self.symmetric)

    def setAmpL(self,value):
        self.ampL = value/1000.
        if self.symmetric:
            self.ampR = -self.ampL
            self.ampRSlider.setValue(int(-self.ampL*1000))
        elif self.ampL > self.ampR:
            self.ampR = self.ampL
            self.ampRSlider.setValue(int(self.ampR*1000))
        self.setAmpLabel()

    def setAmpR(self,value):
        self.ampR = value/1000.
        if self.symmetric:
            self.ampL = -self.ampR
            self.ampLSlider.setValue(int(-self.ampR*1000))
        elif self.ampR < self.ampL:
            self.ampL = self.ampR
            self.ampLSlider.setValue(int(self.ampL*1000))

        self.setAmpLabel()

    def setAmpLabel(self):
        self.ampLabel.setText(f'PV1: {self.ampL:.2f} - {self.ampR:.2f} V')
        self.swing = (self.ampR - self.ampL)/2
        self.mid = (self.ampR + self.ampL)/2

# This section is necessary for running new.py as a standalone program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Expt(None)  # Pass None for the device in standalone mode
    window.show()
    sys.exit(app.exec_()) 