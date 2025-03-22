import sys
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap  # Import QPixmap for image handling
from PyQt5.QtWidgets import QGraphicsScene,QGraphicsPixmapItem, QLabel
from PyQt5.QtCore import Qt

from .utilities.IOWidget import MINIINPUT  # Import Qt for alignment
from .layouts.gauge import Gauge
from .layouts import DCOhmsLaw
from .interactive.myUtils import CustomGraphicsView
from .utilities.devThread import Command, SCOPESTATES
import numpy as np
class Expt(QtWidgets.QWidget, DCOhmsLaw.Ui_Form ):
    def __init__(self, device, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.device = device  # Device handler passed to the Expt class.

        self.scene = QGraphicsScene(self)
        self.view = CustomGraphicsView(self.scene)
        self.view.setFrameShape(QtWidgets.QFrame.NoFrame)  # Remove the frame border
        imagepath = os.path.join(os.path.dirname(__file__),'interactive/SimpleDiodeIV.jpg')        

        mypxmp = QPixmap(imagepath)
        myimg = QGraphicsPixmapItem(mypxmp)
        myimg.setTransformationMode(Qt.SmoothTransformation)
        self.scene.addItem(myimg)
        self.RLabel.setText('Value of Resistor R1 (1K)')
        self.ILabel.setText('Calculated Current ( I = (PV1-A1)/R1)')
        self.SecondLabel.setText('Voltage Across Diode ( V = A1)')


        self.scope_thread = None
        if 'scope_thread' in kwargs:
            self.scope_thread = kwargs['scope_thread']
            self.running = True


        self.PV1 = MINIINPUT(self, self.device, 'PV1', confirmValues=None, scope_thread=self.scope_thread) #Don't use device directly..
        self.A1 = MINIINPUT(self, self.device, 'A1', confirmValues=None, scope_thread=self.scope_thread) 

        self.gaugeLayout.addWidget(self.PV1)
        self.gaugeLayout.addWidget(self.A1)

        self.imageLayout.addWidget(self.view)

        # Create a QTimer for periodic voltage measurement
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_all)  # Connect the timeout signal to the update method
        self.timer.start(5)  # Start the timer with a 5mS interval

    def update_all(self):
        self.A1.update_vals()
        self.PV1.update_vals()
        self.R1 = self.R2Value.value()
        if self.R1 > 0:
            I = (self.PV1.last_value-self.A1.last_value)/self.R1
            self.currentLabel.setText(f"{1000*I:.2f} mA")
            self.R1Value.setText(f"{self.A1.last_value:.2f} V")
        else:
            self.currentLabel.setText("Set R1 to 1K")


# This section is necessary for running new.py as a standalone program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Expt(None)  # Pass None for the device in standalone mode
    window.show()
    sys.exit(app.exec_()) 