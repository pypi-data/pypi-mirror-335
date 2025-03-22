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
from .layouts import DualDrivenPendulum

class Expt(QtWidgets.QFrame, DualDrivenPendulum.Ui_Form):
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
        self.gauge_widget.set_MaxValue(5)
        self.gauge_widget.setMinimumWidth(200)

        self.gauge_widget2 = Gauge(self, 'PV2')
        self.gauge_widget2.setObjectName('PV2')
        self.gauge_widget2.set_MinValue(-3.3)
        self.gauge_widget2.set_MaxValue(3.3)
        self.gauge_widget2.setMinimumWidth(200)


        self.tp = 1. 
        self.ampL = -5
        self.ampR = 5
        self.symmetric = True
        self.ampLSlider.setVisible(False)
        self.swing = (self.ampR - self.ampL)/2
        self.mid = (self.ampR + self.ampL)/2

        self.tp2 = 1. 
        self.ampL2 = -3.3
        self.ampR2 = 3.3
        self.symmetric2 = True
        self.ampLSlider2.setVisible(False)
        self.swing2 = (self.ampR2 - self.ampL2)/2
        self.mid2 = (self.ampR2 + self.ampL2)/2

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
        self.gaugeLayout.addWidget(self.gauge_widget2)
        self.start_time = time.time()
        self.splitter.setSizes([2,1])

        # Create a QTimer for periodic voltage measurement
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_voltage)  # Connect the timeout signal to the update method
        self.timer.start(10)  # Start the timer with a 200ms interval

    def update_voltage(self):
        phase = (time.time() - self.start_time)%self.tp
        v = self.mid + self.swing*np.sin(2*np.pi*phase/self.tp)
        self.scope_thread.add_raw_command('set_pv1',{'voltage':v})
        self.gauge_widget.update_value(v)  # Update the gauge with the new voltage value
        
        phase2 = (time.time() - self.start_time)%self.tp2
        v = self.mid2 + self.swing2*np.sin(2*np.pi*phase2/self.tp2)
        self.scope_thread.add_raw_command('set_pv2',{'voltage':v})
        self.gauge_widget2.update_value(v)  # Update the gauge with the new voltage value

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


    #PV2 controls
    def setFrequency2(self,value):
        self.freqLabel2.setText(f'F: {value/1000:.2f} Hz')
        self.tp2= 1000./value

    def setSymmetric2(self,value):
        self.symmetric2 = value
        if self.symmetric2:
            self.ampR2 = -self.ampL2
            self.ampRSlider2.setValue(int(-self.ampL2*1000))
            self.ampRSlider2.setMinimum(0)
        else:
            self.ampRSlider2.setMinimum(-5000)
        self.setAmpLabel()
        self.ampLSlider2.setVisible(not self.symmetric2)

    def setAmpL2(self,value):
        self.ampL2 = value/1000.
        if self.symmetric2:
            self.ampR2 = -self.ampL2
            self.ampRSlider2.setValue(int(-self.ampL2*1000))
        elif self.ampL2 > self.ampR2:
            self.ampR2 = self.ampL2
            self.ampRSlider2.setValue(int(self.ampR2*1000))
        self.setAmpLabel2()

    def setAmpR2(self,value):
        self.ampR2 = value/1000.
        if self.symmetric2:
            self.ampL2 = -self.ampR2
            self.ampLSlider2.setValue(int(-self.ampR2*1000))
        elif self.ampR2 < self.ampL2:
            self.ampL2 = self.ampR2
            self.ampLSlider2.setValue(int(self.ampL2*1000))

        self.setAmpLabel2()

    def setAmpLabel2(self):
        self.ampLabel2.setText(f'PV2: {self.ampL2:.2f} - {self.ampR2:.2f} V')
        self.swing2 = (self.ampR2 - self.ampL2)/2
        self.mid2 = (self.ampR2 + self.ampL2)/2








# This section is necessary for running new.py as a standalone program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Expt(None)  # Pass None for the device in standalone mode
    window.show()
    sys.exit(app.exec_()) 