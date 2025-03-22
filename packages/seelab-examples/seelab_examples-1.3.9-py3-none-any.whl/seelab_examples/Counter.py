import sys
import os, time
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QIcon,QFont,QCursor
from PyQt5.QtWidgets import QGraphicsScene,QGraphicsPixmapItem
from PyQt5.QtCore import Qt  # Import Qt for alignment
from .layouts.gauge import Gauge
from .interactive.myUtils import CustomGraphicsView
from .layouts import Counter
from .utilities.devThread import Command
import numpy as np
import pyqtgraph as pg

from .utils import fit_sine, fit_dsine, sine_eval, dsine_eval

vel_points=10

class Expt(QtWidgets.QWidget, Counter.Ui_Form):
    def __init__(self, device, **kwargs):
        super().__init__()
        self.setupUi(self)
        time.sleep(0.2)
        self.last_counts = 0
        self.input = 'SEN'
        self.startCounts = 0
        self.start_time = time.time()

        self.scope_thread = None
        self.running = False
        if 'scope_thread' in kwargs:
            self.scope_thread = kwargs['scope_thread']
            self.scope_thread.add_command(Command('set_sqr1',{'frequency':0,'duty_cycle':0.5}))
            self.scope_thread.add_command(Command('start_counter',{'channel':'SEN'}))
            self.scope_thread.add_command(Command('pause_counter',{'channel':'SEN'}))

            self.scope_thread.counts_ready.connect(self.setCounts)

        self.showMessage = print

        if 'set_status_function' in kwargs:
            self.set_status_function(kwargs['set_status_function'])

        self.shortcutActions = {}
        self.shortcuts={"f":self.sineFit,'g':self.dampedSineFit}
        for a in self.shortcuts:
            shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(a), self)
            shortcut.activated.connect(self.shortcuts[a])
            self.shortcutActions[a] = shortcut


        self.gauge_widget = Gauge(self, 'COUNTS')
        self.gauge_widget.setObjectName('COUNTS')
        self.gauge_widget.set_MinValue(0)
        self.max_value = 100
        self.gauge_widget.set_MaxValue(self.max_value)
        self.gauge_widget.setMinimumWidth(300)
        self.gaugeLayout.addWidget(self.gauge_widget)


        # Create a layout for the right side (image)
        image_widget = QtWidgets.QWidget()  # Placeholder for the image
        

        self.scene = QGraphicsScene(self)
        self.view = CustomGraphicsView(self.scene)
        self.view.setFrameShape(QtWidgets.QFrame.NoFrame)  # Remove the frame border

        imagepath = os.path.join(os.path.dirname(__file__),'interactive/flywheel.jpg')
        mypxmp = QPixmap(imagepath)
        myimg = QGraphicsPixmapItem(mypxmp)
        myimg.setTransformationMode(Qt.SmoothTransformation)
        self.scene.addItem(myimg)

        self.gaugeLayout.addWidget(self.view)

        # Create a horizontal frame for radio buttons and warning label
        self.startButton.setIcon(QIcon(os.path.join("layouts","play.svg")))
        self.startButton.setIconSize(QtCore.QSize(40, 40))

        self.stopButton.setIcon(QIcon(os.path.join("layouts","pause.svg")))
        self.stopButton.setIconSize(QtCore.QSize(40, 40))
        self.splitter.setSizes([100, 100])

        # Create plots
        self.MAXPOINTS = 10000
        self.datapoints = 0
        self.distance_plot = self.plotLayout.addPlot()

        self.T = 0

        self.time_data = np.empty(300)
        self.distance_data = np.empty(300)
        self.velocity_data = np.empty(300)
        self.datapoints=0

        self.distance_curve = self.distance_plot.plot(self.distance_data[0:self.datapoints])
        self.plotLayout.nextRow()
        self.velocity_plot = self.plotLayout.addPlot()
        self.velocity_plot.setLimits(yMin=0)
        self.velocity_data = np.zeros(self.MAXPOINTS)
        self.velocity_curve = self.velocity_plot.plot(self.velocity_data[0:self.datapoints])   
        self.fitCurve_sine = self.velocity_plot.plot()   
        self.fitCurve_dsine = self.velocity_plot.plot()

        self.distance_plot.setLabel('left', 'Distance')
        self.distance_plot.setLabel('bottom', 'Time')
        self.velocity_plot.setLabel('left', 'Velocity')
        self.velocity_plot.setLabel('bottom', 'Time')

        self.region = pg.LinearRegionItem()
        self.region.setBrush([255,0,50,50])
        self.region.setZValue(10)
        for a in self.region.lines: a.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor)); 
        self.velocity_plot.addItem(self.region, ignoreBounds=False)
        self.region.setRegion([-3,-.5])


        # Create a QTimer for periodic voltage measurement
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.fetch_counts)  # Connect the timeout signal to the update method
        self.timer.start(200)  # Start the timer with a 200ms interval


    def set_status_function(self,func):
        self.showMessage = func

    def fetch_counts(self):
        if not self.running: return
        self.scope_thread.add_command(Command('get_counts',{}))

    def setCounts(self,counts):
        self.last_counts = counts
        if counts > self.max_value and self.max_value<2e32:
            self.max_value = self.max_value*2
            self.gauge_widget.set_MaxValue(self.max_value)
            self.showMessage(f'Range increased to {self.max_value}', 2000)

        self.gauge_widget.update_value(counts)  # Update the gauge with the new voltage value

        if not self.running: return
        if self.datapoints >= self.time_data.shape[0]-1:
            tmp = self.time_data    
            self.time_data = np.empty(self.time_data.shape[0] * 2) #double the size
            self.time_data[:tmp.shape[0]] = tmp
            tmp = self.distance_data
            self.distance_data  = np.empty(self.distance_data.shape[0] * 2) #double the size
            self.distance_data[:tmp.shape[0]] = tmp
            tmp = self.velocity_data
            self.velocity_data = np.empty(self.velocity_data.shape[0] * 2) #double the size
            self.velocity_data[:tmp.shape[0]] = tmp

        self.time_data[self.datapoints] = time.time()-self.start_time
        self.distance_data[self.datapoints] = counts

        
        if self.datapoints > vel_points:
            self.velocity_data[self.datapoints-vel_points-1] = (self.distance_data[self.datapoints]-self.distance_data[self.datapoints-vel_points-1])/(self.time_data[self.datapoints]-self.time_data[self.datapoints-vel_points-1])
            self.velocity_curve.setData(self.time_data[0:self.datapoints-vel_points],self.velocity_data[0:self.datapoints-vel_points])
            self.velocity_curve.setPos(-self.time_data[self.datapoints], 0)

        self.T = time.time() - self.start_time
        self.distance_curve.setData(self.time_data[0:self.datapoints],self.distance_data[0:self.datapoints])
        self.distance_curve.setPos(-self.time_data[self.datapoints], 0)

        self.datapoints += 1



    def startCounter(self):
        self.last_counts = 0
        self.scope_thread.add_command(Command('start_counter',{'channel':self.input}))
        self.start_time = time.time()

        self.time_data = np.empty(300)
        self.distance_data = np.empty(300)
        self.velocity_data = np.empty(300)
        self.datapoints=0
        print("Starting counter")
        self.running = True


    def pauseCounter(self):
        self.running = not self.running
        if not self.running:    
            self.stopButton.setIcon(QIcon(os.path.join("layouts","play.svg")))
            self.stopButton.setText('Resume')
            self.scope_thread.add_command(Command('pause_counter',{}))
        else:
            self.stopButton.setIcon(QIcon(os.path.join("layouts","pause.svg")))
            self.stopButton.setText('Pause')
            self.scope_thread.add_command(Command('resume_counter',{}))

    def setInput(self,input):
        if input == 0:
            self.input = 'SEN'
        else:
            self.input = 'IN2'
        if self.running:
            self.startCounter()

    def set_sqr1(self):
        f = self.sqr1_freq.value()
        self.scope_thread.add_command(Command('set_sqr1',{'frequency':f,'duty_cycle':0.5}))
        if f == 0:
            self.sqr1_label.setText('SQR1 Frequency : ALWAYS ON')
        else:
            self.sqr1_label.setText(f'SQR1 Frequency ( 0 = ALWAYS ON) : {f} Hz')



    def sineFit(self):
        S,E=self.region.getRegion()
        start = (np.abs(self.time_data[:self.datapoints-vel_points]- self.T - S)).argmin()
        end = (np.abs(self.time_data[:self.datapoints-vel_points]-self.T - E)).argmin()
        print(self.T,start,end,S,E,self.time_data[start],self.time_data[end])
        res = 'Amp, Freq, Phase, Offset<br>'
        try:
                fa=fit_sine(self.time_data[start:end],self.velocity_data[start:end])
                if fa is not None:
                        amp=abs(fa[0])
                        freq=fa[1]
                        phase = fa[2]
                        offset = fa[3]
                        s = '%5.2f , %5.3f Hz, %.2f, %.1f<br>'%(amp,freq, phase, offset)
                        res+= s
                        x = np.linspace(self.time_data[start],self.time_data[end],1000)
                        self.fitCurve_sine.clear()
                        self.fitCurve_sine.setData(x-self.T,sine_eval(x,fa))
                        self.fitCurve_sine.setVisible(True)

        except Exception as e:
                res+='--<br>'
                print (e)
                pass
        self.msgBox = QtWidgets.QMessageBox(self)
        self.msgBox.setWindowModality(QtCore.Qt.NonModal)
        self.msgBox.setWindowTitle('Sine Fit Results')
        self.msgBox.setText(res)
        self.msgBox.show()

    def dampedSineFit(self):
        S,E=self.region.getRegion()
        start = (np.abs(self.time_data[:self.datapoints-vel_points]- self.T - S)).argmin()
        end = (np.abs(self.time_data[:self.datapoints-vel_points]-self.T - E)).argmin()
        print(self.T,start,end,S,E,self.time_data[start],self.time_data[end])
        res = 'Amplitude, Freq, phase, Damping<br>'
        try:
                fa=fit_dsine(self.time_data[start:end],self.velocity_data[start:end])
                if fa is not None:
                        amp=abs(fa[0])
                        freq=fa[1]
                        decay=fa[4]
                        phase = fa[2]
                        s = '%5.2f , %5.3f Hz, %.3f, %.3e<br>'%(amp,freq,phase,decay)
                        res+= s
                        x = np.linspace(self.time_data[start],self.time_data[end],1000)
                        self.fitCurve_dsine.clear()
                        self.fitCurve_dsine.setData(x-self.T,dsine_eval(x,fa))
                        self.fitCurve_dsine.setVisible(True)
        except Exception as e:
                res+='--<br>'
                print (e)
                pass
        self.msgBox = QtWidgets.QMessageBox(self)
        self.msgBox.setWindowModality(QtCore.Qt.NonModal)
        self.msgBox.setWindowTitle('Damped Sine Fit Results')
        self.msgBox.setText(res)
        self.msgBox.show()



# This section is necessary for running new.py as a standalone program

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Expt(None)  # Pass None for the device in standalone mode
    window.show()
    sys.exit(app.exec_()) 