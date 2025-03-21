import sys
import os, time
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QIcon,QFont,QCursor
from PyQt5.QtWidgets import QGraphicsScene,QGraphicsPixmapItem
from PyQt5.QtCore import Qt  # Import Qt for alignment
from .layouts.gauge import Gauge
from .interactive.myUtils import CustomGraphicsView
from .layouts import ui_comms
from .utilities.devThread import Command
import numpy as np
import pyqtgraph as pg

from .utils import fit_sine, fit_dsine, sine_eval, dsine_eval

vel_points=10

class Expt(QtWidgets.QWidget, ui_comms.Ui_Form):
    def __init__(self, device, **kwargs):
        super().__init__()
        self.setupUi(self)
        time.sleep(0.2)
        self.startCounts = 0
        self.start_time = time.time()
        self.transmit_string = "....."
        self.transmit_index = 0
        self.last_time = time.time()
        self.interval = 3 #seconds
        self.mode = 0# transmit mode
        self.transmit_index = -1
        self.HS = False
        self.speed_factor = 50

        self.ascii_mapping = {
            'A': (2, 5), 'B': (2, 10), 'C': (2, 15),  # Uppercase letters
            'D': (2, 20), 'E': (2, 25), 'F': (2, 30),
            'G': (2, 35), 'H': (2, 40), 'I': (2, 45),
            'J': (2, 50), 'K': (2, 55), 'L': (2, 60),
            'M': (2, 65), 'N': (2, 70), 'O': (2, 75),
            'P': (2, 80), 'Q': (2, 85), 'R': (2, 90),
            'S': (2, 95), 'T': (4, 5),  'U': (4, 10),
            'V': (4, 15), 'W': (4, 20), 'X': (4, 25),
            'Y': (4, 30), 'Z': (4, 35),
            'a': (6, 5),  'b': (6, 10), 'c': (6, 15),  # Lowercase letters
            'd': (6, 20), 'e': (6, 25), 'f': (6, 30),
            'g': (6, 35), 'h': (6, 40), 'i': (6, 45),
            'j': (6, 50), 'k': (6, 55), 'l': (6, 60),
            'm': (6, 65), 'n': (6, 70), 'o': (6, 75),
            'p': (6, 80), 'q': (6, 85), 'r': (6, 90),
            's': (6, 95), 't': (8, 5),  'u': (8, 10),
            'v': (8, 15), 'w': (8, 20), 'x': (8, 25),
            'y': (8, 30), 'z': (8, 35),
            '0': (10, 5), '1': (10, 10), '2': (10, 15),  # Numbers
            '3': (10, 20), '4': (10, 25), '5': (10, 30),
            '6': (10, 35), '7': (10, 40), '8': (10, 45),
            '9': (10, 50),
            ' ': (12, 5), '.': (12, 10), ',': (12, 15),  # Common symbols
            '!': (12, 20), '?': (12, 25), '@': (12, 30)
        }
        self.reverse_mapping_x = np.zeros(255)

        # loop through keys and values of ascii_mapping and fill the reverse_mapping_x and reverse_mapping_y arrays
        num=0
        for key,value in self.ascii_mapping.items():
            self.reverse_mapping_x[ord(key)] = value[0]*value[1]
            num += 1

        print(self.reverse_mapping_x)

        self.scope_thread = None
        self.running = True
        self.HS = False
        if 'scope_thread' in kwargs:
            self.scope_thread = kwargs['scope_thread']
            self.scope_thread.add_command(Command('set_sqr1',{'frequency':0,'duty_cycle':0.5}))
            self.scope_thread.duty_cycle_ready.connect(self.got_duty_cycle)

        self.showMessage = print

        if 'set_status_function' in kwargs:
            self.set_status_function(kwargs['set_status_function'])


        self.waiting_for_frequency = False
        # Create a QTimer for periodic timing measurement
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)  # Connect the timeout signal to the update method
        self.timer.start(50)  # Start the timer with a 50ms interval


    def setHS(self,HS):
        self.HS = HS
        if self.HS:
            self.interval = 0.3
        else:
            self.interval = 3

    def got_duty_cycle(self,f,dc):
        dc = 100-dc # invert for phototransistor operation
        if self.HS:
            f/=self.speed_factor
        index = np.argmin(np.abs(self.reverse_mapping_x - f*dc))
        print(f,dc,index)
        if index == 0:
            self.recvLabel.setText('')
        else:
            self.recvLabel.setText(chr(index))
            
        self.waiting_for_frequency = False

    def set_status_function(self,func):
        self.showMessage = func

    def sendData(self):
        self.last_time = 0
        self.transmit_index =0 
        self.transmit_string = self.dataEdit.text()
        print('sending',self.transmit_string)

    def update(self):
        if not self.running: return
        if self.mode == 0:  #in transmit mode.
            if time.time() - self.last_time > self.interval:
                if self.transmit_index < len(self.transmit_string) and self.transmit_index >= 0:
                    self.sendLabel.setText(self.transmit_string[self.transmit_index])
                    #Send the data
                    encoding = self.ascii_mapping[self.transmit_string[self.transmit_index]]
                    f,dc = encoding
                    if self.HS:
                        f*=self.speed_factor

                    self.set_sqr1(f,dc)
                    self.transmit_index += 1
                    self.last_time = time.time()
                else:
                    self.transmit_index = -1
                    self.scope_thread.add_command(Command('set_state',{'SQR1':0}))
            pass
        else:
            if self.waiting_for_frequency:
                return
            self.scope_thread.add_command(Command('get_duty_cycle',{'channel':'SEN','timeout':2}))

    def setMode(self,mode):
        self.mode = mode

    def set_sqr1(self,freq,dc):
        self.scope_thread.add_command(Command('set_sqr1',{'frequency':freq,'duty_cycle':dc}))
        self.sqr1_freq.setValue(freq)
        self.sqr1_dc.setValue(dc)



# This section is necessary for running new.py as a standalone program

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Expt(None)  # Pass None for the device in standalone mode
    window.show()
    sys.exit(app.exec_()) 