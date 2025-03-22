import sys
import os, time
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QIcon,QFont,QCursor
from PyQt5.QtWidgets import QGraphicsScene,QGraphicsPixmapItem
from PyQt5.QtCore import Qt  # Import Qt for alignment
from .layouts.gauge import Gauge
from .interactive.myUtils import CustomGraphicsView
from .layouts import comms
from .utilities.devThread import Command
import numpy as np
import pyqtgraph as pg
#import keyboard

from .utils import fit_sine, fit_dsine, sine_eval, dsine_eval

vel_points=10

# create a widget which monitors which key

class Expt(QtWidgets.QWidget, comms.Ui_Form):
    def __init__(self, device, **kwargs):
        super().__init__()
        self.setupUi(self)
        time.sleep(0.2)
        self.startCounts = 0
        self.start_time = time.time()
        self.transmit_string = "....."
        self.transmit_index = 0
        self.last_time = time.time()
        self.interval = 0.2 #seconds
        self.mode = 0# transmit mode
        self.transmit_index = -1
        self.speed_factor = 50
        self.recvText= '_______'


        self.scope_thread = None
        self.running = True
        self.HS = 1
        self.comma = False
        if 'scope_thread' in kwargs:
            self.scope_thread = kwargs['scope_thread']
            self.scope_thread.add_command(Command('set_sqr1',{'frequency':0,'duty_cycle':50}))
            self.scope_thread.add_command(Command('set_sqr2',{'frequency':66,'duty_cycle':50}))
            self.scope_thread.frequency_ready.connect(self.got_freq)

        self.showMessage = print

        if 'set_status_function' in kwargs:
            self.set_status_function(kwargs['set_status_function'])


        self.waiting_for_frequency = False
        # Create a QTimer for periodic timing measurement
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)  # Connect the timeout signal to the update method
        self.timer.start(20)  # Start the timer with a 50ms interval


    def setHS(self,HS):
        if HS:
            self.HS = 10
            self.interval = 0.2
        else:
            self.HS = 1
            self.interval = 0.5

    def got_freq(self,channel,f,dc):
        if f == -1: #timeout
            self.recvText=self.recvText[1:]+'.'
        elif 45<dc<55:
            letter = chr(int(np.round(f/self.HS)  ))
            if letter == ',':
                self.comma = False
            elif not self.comma:
                print(f,self.HS, int(np.round(f/self.HS)  ))
                self.recvText=self.recvText[1:]+letter
                self.comma = True
        self.recvLabel.setText(self.recvText)
            
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
                    #Send the data
                    f = ord(self.transmit_string[self.transmit_index])
                    if self.comma:
                        #self.sendLabel.setText(',')
                        f = ord(',')
                        self.comma = False
                    else:
                        self.sendLabel.setText(self.transmit_string[self.transmit_index])
                        self.comma = True
                        self.transmit_index += 1
                    print(f*self.HS)
                    self.set_sqr1(f*self.HS,50)
                    self.last_time = time.time()
                else:
                    self.transmit_index = 0 #-1 for looping
                    self.scope_thread.add_command(Command('set_state',{'SQR1':0}))
            pass
        elif self.mode == 1: # receive mode
            if self.waiting_for_frequency:
                return
            self.scope_thread.add_command(Command('get_freq',{'channel':'SEN'}))
        elif self.mode == 2: # manual transmit mode
            #self.scope_thread.add_command(Command('get_freq',{'channel':'SEN'}))
            pass

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