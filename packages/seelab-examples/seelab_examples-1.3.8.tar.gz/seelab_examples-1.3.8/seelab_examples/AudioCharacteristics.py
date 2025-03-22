import sys, time
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap,QIcon  # Import QPixmap for image handling
from PyQt5.QtWidgets import QGraphicsScene,QGraphicsPixmapItem, QLabel
from PyQt5.QtCore import Qt

from eyes17 import eyemath17 as em
from .utilities.IOWidget import MINIINPUT  # Import Qt for alignment
from .layouts.gauge import Gauge
from .layouts import AudioCharacteristics
from .interactive.myUtils import CustomGraphicsView
from .utilities.devThread import Command, SCOPESTATES
import numpy as np
import pyqtgraph as pg
class Expt(QtWidgets.QWidget, AudioCharacteristics.Ui_Form ):
    RangeVals12 = np.array([16., 8., 4., 2.5, 1., 0.5])
    def __init__(self, device, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.device = device  # Device handler passed to the Expt class.
        self.fit1 = None

        self.scope_thread = None
        if 'scope_thread' in kwargs:
            self.scope_thread = kwargs['scope_thread']
            self.running = True
            self.scope_thread.trace_ready.connect(self.update_trace)
            self.scope_thread.add_raw_command('configure_trigger',{'channel':1,'source':'A2','level':0})
            self.scope_thread.progress_ready.connect(self.update_progress)
            self.scope_thread.state == SCOPESTATES.FREE

        self.ipy = kwargs.get('ipy',None)
        print(self.ipy)

        self.showMessage = print

        if 'set_status_function' in kwargs:
            self.set_status_function(kwargs['set_status_function'])


        self.WG = MINIINPUT(self, self.device, 'WG', confirmValues=None, scope_thread=self.scope_thread) #Don't use device directly..
        self.WG.update_write_value(1000)
        self.timeData = [None] * 2
        self.voltData = [None] * 2

        self.frequencyData = []
        self.gainData = []
        self.phaseData = []

        self.gaugeLayout.addWidget(self.WG)

        # SCOPE details
        self.NP = 1000
        self.TG = 2
        self.autosetA2Flag = -1

        # Create plots
        self.leftParameters = ['Amplitude(A2)','Frequency(A2)','Phase(A2)','Amplitude(MIC)','Frequency(MIC)','Phase(MIC)','Gain Amp(MIC/A2)','Phase Shift Phi_MIC-Phi_A2)']
        self.activeLeftParameter = 6
        self.MAXPOINTS = 10000
        self.datapoints = 0
        self.scope_plot.setTitle('Oscilloscope')
        self.scope_plot.addLegend()
        self.scope_plot.setYRange(-5,5)
        self.scope_plot.plotItem.setLabel('left', 'Voltage IN(A2)', units="<font>V</font>",
                    color='red', **{'font-size':'14pt'})

        self.scope_plot.setLabel('bottom', 'Time')

        self.datapoints=0

        self.traces = []
        self.A2Curve = pg.PlotCurveItem(pen=pg.mkPen(color='red', width=1.2))
        self.scope_plot.addItem(self.A2Curve)

        ## create a new ViewBox, link the right axis to its coordinate system
        self.sp2 = pg.ViewBox()
        self.scope_plot.plotItem.showAxis('right')
        self.scope_plot.plotItem.scene().addItem(self.sp2)
        self.scope_plot.plotItem.getAxis('right').linkToView(self.sp2)
        self.sp2.setXLink(self.scope_plot.plotItem)
        self.sp2.setYRange(-5,5)
        self.scope_plot.plotItem.setLabel('right', 'MIC Signal(A2)', units="<font>V</font>",
                    color='darkgreen', **{'font-size':'14pt'})

        self.MICCurve = pg.PlotCurveItem(pen=pg.mkPen(color='darkgreen', width=1.5))
        self.sp2.addItem(self.MICCurve)

        self.traces.append(self.A2Curve)
        self.traces.append(self.MICCurve)

        self.updateScopeViews()
        self.scope_plot.plotItem.vb.sigResized.connect(self.updateScopeViews)



        self.bode_plot.setLimits(yMin=0)
        self.bode_data = np.zeros(self.MAXPOINTS)
        self.bode_curve = self.bode_plot.plot(pen=pg.mkPen(color='red', width=2))   
        self.bode_plot.getAxis('left').setPen(pg.mkPen(color='red', width=2))
        self.bode_plot.setLabel('left', self.leftParameters[self.activeLeftParameter], color='red', **{'font-size':'14pt'})
        self.bode_plot.setLabel('bottom', 'Frequency')

        self.scope_plot.setBackground("w")
        self.bode_plot.setBackground("w")

        ## create a new ViewBox, link the right axis to its coordinate system
        self.p2 = pg.ViewBox()
        self.bode_plot.plotItem.showAxis('right')
        self.bode_plot.plotItem.scene().addItem(self.p2)
        self.bode_plot.plotItem.getAxis('right').linkToView(self.p2)
        self.p2.setXLink(self.bode_plot.plotItem)
        self.bode_plot.plotItem.setLabel('right', 'Phase', units="<font>&phi;</font>",
                    color='#025b94', **{'font-size':'14pt'})
        self.bode_plot.getAxis('right').setPen(pg.mkPen(color='magenta', width=2))

        self.phase_curve = pg.PlotCurveItem(pen=pg.mkPen(color='magenta', width=1))
        self.p2.addItem(self.phase_curve)

        self.updateViews()
        self.bode_plot.plotItem.vb.sigResized.connect(self.updateViews)


        self.splitter.setSizes([1,1])
        self.recordNextFit = False

        self.ct = time.time()

        self.waveform_settling_time = time.time()
        self.running = False
        self.value=None
        self.start=5
        self.stop=5000
        self.samples = 100
        self.step = (self.stop-self.start)/self.samples
        self.settling_delay = 0.1 #S


        # Create a QTimer for periodic voltage measurement
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_all)  # Connect the timeout signal to the update method
        self.timer.start(10)  # Start the timer with a 50mS interval

    def autosetA2(self):
        self.setA2Range(0) #Set max range.
        self.autosetA2Flag = 2 #2 captures before setting A2 range.
        self.scope_thread.state = SCOPESTATES.FREE


    def applyAutosetA2(self):
        max = self.voltData[1].max()
        index = np.argmin(np.abs(self.RangeVals12-max))
        if index>0 and max>self.RangeVals12[index]:
            index -=1 #Choose the next larger range.
        self.A2Range.blockSignals(True)
        self.A2Range.setCurrentIndex(index)
        self.A2Range.blockSignals(False)
        self.setA2Range(index)


    def setA2Range(self, r):
        print(self.RangeVals12[r])
        self.scope_thread.add_command(Command('select_range',{'channel':'A2','value':self.RangeVals12[r]}))
        self.sp2.setYRange(-1*self.RangeVals12[r],self.RangeVals12[r])

    ## Handle view resizing 
    def updateViews(self):
        ## view has resized; update auxiliary views to match
        self.p2.setGeometry(self.bode_plot.plotItem.vb.sceneBoundingRect())
        
        ## need to re-update linked axes since this was called
        ## incorrectly while views had different shapes.
        ## (probably this should be handled in ViewBox.resizeEvent)
        self.p2.linkedViewChanged(self.bode_plot.plotItem.vb, self.p2.XAxis)

    def updateScopeViews(self):
        self.sp2.setGeometry(self.scope_plot.plotItem.vb.sceneBoundingRect())
        self.sp2.linkedViewChanged(self.scope_plot.plotItem.vb, self.sp2.XAxis)

    def setLeftParameter(self,x,y,x2,y2):
        self.activeLeftParameter = x
        self.bode_plot.setLabel('left', self.leftParameters[self.activeLeftParameter], color='#c4380d', **{'font-size':'14pt'})
        self.updateViews()

    def launch_ipy(self):
        self.ipy('Filter Characteristics Data Analysis',{'device':self.device,'msg':'Access raw data x,y,y2 variables','x':self.frequencyData,'y':self.gainData,'y2':self.phaseData})

    def viewPlot1(self):
        from matplotlib import pyplot as plt
        plt.plot(self.frequencyData, self.gainData)
        plt.show()

    def viewPlot2(self):
        from matplotlib import pyplot as plt
        plt.plot(self.frequencyData, self.phaseData)
        plt.show()

    def toggleLogging(self):
        newstate = not self.running
        if not newstate:
            self.playButton.setIcon(QIcon(os.path.join("layouts","play.svg")))
            self.playButton.setText('Resume')
        else:
            if self.value is None: #clear data. starting from scratch
                self.frequencyData = []
                self.gainData = []
                self.phaseData = []

            if self.calculateParameters(): 
                self.playButton.setIcon(QIcon(os.path.join("layouts","pause.svg")))
                self.playButton.setText('Pause')
                self.showMessage(f'Start Sweep from {self.start} to {self.stop} , in steps {self.step}')
                self.WG.update_write_value(self.value)
                self.WG.update_vals()
                self.waveform_settling_time  = time.time()+0.5 # First time. give 500mS
            else:
                newstate = False
                self.showMessage('setting parameters failed',1000)

        self.scope_thread.state = SCOPESTATES.FREE
        self.running = newstate

    def stopLogging(self):
        self.running = False
        self.recordNextFit = False
        self.value = None
        self.playButton.setIcon(QIcon(os.path.join("layouts","play.svg")))
        self.playButton.setText('Start')

    def calculateParameters(self):
        try:
            self.start=float(self.startEdit.text())
            if self.value is None:
                self.value = self.start
        except:
            return False

        try:
            self.stop=float(self.stopEdit.text())
        except:
            return False

        try:
            self.samples=int(self.samplesEdit.text())
        except:
            return False

        self.step = (self.stop-self.start)/self.samples

        try:
            self.settling_delay=float(self.delayEdit.text())/1000.
        except:
            self.settling_delay = 0.1 #S
            self.delayEdit.setText(f'{self.settling_delay*1000}')

        return True


    def update_all(self):
        if self.running: #Auto Sweep Mode
            if time.time() < self.waveform_settling_time:
                return # Waveform has not settled down.
            self.recordNextFit = True

        else:
            self.WG.update_vals()

        ########### SCOPE IS FREE . START CAPTURE ################
        if self.scope_thread.state == SCOPESTATES.FREE:
            self.applied_freq = self.WG.last_value
            if self.applied_freq<20:
                self.applied_freq = 20
            self.TG = 5e6/self.applied_freq/self.NP #5 cycles
            if self.TG<2:
                self.TG=2
            elif self.TG>2000:
                self.TG=2000

            self.scope_thread.state = SCOPESTATES.CAPTURING
            self.scope_thread.add_command(Command('capture_traces', {'num_channels':2,'channel_input': 'MIC', 'samples': self.NP, 'timebase': self.TG, 'trigger': True}))
            self.scope_thread.fetchTime = time.time() + 1e-6 * self.NP * self.TG + .05


        ########### SCOPE IS CAPTURING . FETCH PERIODIC PROGRESS ################
        elif self.scope_thread.state == SCOPESTATES.CAPTURING:
            if time.time() - self.scope_thread.fetchTime > 0.02:
                self.scope_thread.add_command(Command('oscilloscope_progress',{}))
        
        ########### SCOPE IS COMPLETED . FETCH DATA ################
        self.repaint()

    def update_progress(self,status, trigwait, progress):
        if (self.scope_thread.state == SCOPESTATES.CAPTURING and self.scope_thread.polling) or status:
                self.fetch_partial_trace(1, progress)
                self.fetch_partial_trace(2, progress, status)


    def fetch_partial_trace(self,channel_num, progress, finalFetch=False):
        ch = channel_num - 1
        if (progress - self.scope_thread.device.achans[ch].fetched_length)*self.TG > 200 or progress==self.NP or finalFetch: #50 new points have arrived
            if progress != self.NP:
                finalFetch = False
            self.scope_thread.add_command(Command('fetch_partial_trace',{'channel_num':channel_num, 'progress': progress, 'callback': self.freeScope if finalFetch else None}))

    def freeScope(self,*args):
        #Analysis
        # Fit channel 1 (MIC)
        self.fitvals = np.zeros(8)
        try:
            fa = em.fit_sine(self.timeData[0], self.voltData[0])
            self.fit1 = fa[1]
            self.fitvals[0:3] = fa[1][0:3]
            self.tableWidget.item(0, 1).setText(f'{fa[1][0]:.3f}')  
            self.tableWidget.item(1, 1).setText(f'{fa[1][1]:.3f}')  
            self.tableWidget.item(2, 1).setText(f'{fa[1][2]:.3f}')  
        except Exception as err:
            fa = None
            self.fit1 = None


        # Fit channel 2 (A2)
        try:
            fa = em.fit_sine(self.timeData[1], self.voltData[1])
            self.fitvals[3:6] = fa[1][0:3]
            self.tableWidget.item(3, 1).setText(f'{fa[1][0]:.3f}')  
            self.tableWidget.item(4, 1).setText(f'{fa[1][1]:.3f}')  
            self.tableWidget.item(5, 1).setText(f'{fa[1][2]:.3f}')  
            if self.fit1 is not None:
                self.fitvals[6] = fa[1][0]/self.fit1[0]
                self.fitvals[7] = fa[1][2] - self.fit1[2]
                self.tableWidget.item(6, 1).setText(f'{fa[1][0]/self.fit1[0]:.3f}')   #gain
                self.tableWidget.item(7, 1).setText(f'{fa[1][2] - self.fit1[2]:.3f}')   #dphi
                self.xLabel.setText(f'XAXIS: {self.fitvals[1]:.3f}') #Frequency
                self.yLabel.setText(f'{self.leftParameters[self.activeLeftParameter]} : {self.fitvals[self.activeLeftParameter]:.3f}, dPhi: {fa[1][2] - self.fit1[2]:.3f}')

                if self.recordNextFit:
                    f = self.fitvals[1]
                    self.frequencyData.append(self.fitvals[1])
                    self.gainData.append(self.fitvals[self.activeLeftParameter])
                    self.phaseData.append(fa[1][2] - self.fit1[2])
                    self.bode_curve.setData(self.frequencyData, self.gainData)
                    self.phase_curve.setData(self.frequencyData, self.phaseData)
                    self.recordNextFit = False

        except Exception as err:
            print(err)
            pass

        if self.running:
            if self.value < self.stop:
                self.value += self.step
                self.WG.update_write_value(self.value)
                self.WG.update_vals()
                self.waveform_settling_time  = time.time()+self.settling_delay
            else:
                self.stopLogging()

        if self.autosetA2Flag==0:
            self.autosetA2Flag = -1
            self.applyAutosetA2()
        elif self.autosetA2Flag>0:
            self.autosetA2Flag -=1

        self.ct = time.time()
        self.update()
        self.scope_thread.state = SCOPESTATES.FREE



    def update_trace(self, channel_num):
        ch = channel_num - 1
        self.timeData[ch]  = self.scope_thread.device.achans[ch].get_fetched_xaxis()*1.e-6
        self.voltData[ch]  = self.scope_thread.device.achans[ch].get_fetched_yaxis()
        if(len(self.voltData[ch])<50):return

        self.scope_plot.setXRange(0,self.NP*self.TG*1.e-6)
        self.traces[ch].setData(self.timeData[ch][:self.NP], self.voltData[ch][:self.NP])




# This section is necessary for running new.py as a standalone program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Expt(None)  # Pass None for the device in standalone mode
    window.show()
    sys.exit(app.exec_()) 