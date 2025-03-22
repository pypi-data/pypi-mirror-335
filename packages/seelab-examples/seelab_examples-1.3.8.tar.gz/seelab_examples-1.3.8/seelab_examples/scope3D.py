# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path

import utils
from QtVersion import *
from PyQt5.QtGui import QIcon
import sys, time
from utils import pg
import numpy as np
import eyes17.eyemath17 as em
from functools import partial

from .layouts import scope3d_layout
from .layouts.advancedLoggerTools import LOGGER
from .layouts.sensor_utilities import DIOSENSOR, DIOROBOT, DIOCONTROL
from .layouts.gauge import Gauge

from .utilities.devThread import Command, SCOPESTATES
from enum import Enum

import shelve




class Expt(QtWidgets.QWidget, scope3d_layout.Ui_Form):
    TIMER = 5
    loopCounter = 0
    AWGmin = 1
    AWGmax = 5000
    AWGval = 1000
    SQ1min = 0
    SQ1max = 50000
    SQ1val = 0
    PV1min = -5.0
    PV1max = 5.0
    PV1val = 0.0
    PV2min = -3.3
    PV2max = 3.3
    PV2val = 0.0

    RPVspacing = 3  # Right panel Widget spacing
    RPWIDTH = 300
    LABW = 60

    # Scope parameters
    MAXCHAN = 4
    Ranges12 = ['16 V', '8 V', '4 V', '2.5 V', '1 V', '.5V']  # Voltage ranges for A1 and A2
    RangeVals12 = [16., 8., 4., 2.5, 1., 0.5]
    Ranges34 = ['4 V', '2 V', '1 V', '.5V']  # Voltage ranges for A3 and MIC
    RangeVals34 = [4, 2, 1, 0.5]
    chanStatus = [1, 0, 0, 0]
    timeData = [None] * 4
    voltData = [None] * 4
    Phase = [0] * 4
    rangeVal = 4  # selected value of range
    rangeText = '4 V'  # selected value of range
    voltMeters = [None] * 3
    voltMeterCB = {}
    valueLabel = None
    trigEnable = True
    traceCounter=0

    sources = ['A1', 'A2', 'A3', 'MIC', 'SEN', 'IN1', 'AN8']
    source = 'A1'

    tbvals = [0.1, 0.3, 0.4, 0.5, 0.6, 0.7 , 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 5.0, 10.0, 20.0, 30., 40., 50., 60. , 100., 200.,400]  # allowed mS/div values
    NP = 500  # Number of samples
    TG = 1  # Number of channels
    MINDEL = 1  # minimum time between samples, in usecs
    MAXDEL = 8000
    delay = MINDEL  # Time interval between samples
    TBval = 1  # timebase list index
    Trigindex = 0
    Triglevel = 0
    dutyCycle = 50
    MAXRES = 5
    resLabs = [None] * MAXRES
    Results = [None] * MAXRES

    Wgains = ['80 mV', '1V', '3V']
    wgainindex = 2

    Waves = ['sine', 'tria', 'SQR2']
    waveindex = 0
    voltmeter = None

        

    def __init__(self, device=None, **kwargs):
        super(Expt, self).__init__()
        self.sensorList = []
        self.timer = QTimer()
        self.frozen = False
        self.singleShotEnabled = False
        self.WaitingForProgress = False
        if 'scope_thread' in kwargs:
            self.set_scope_thread(kwargs['scope_thread'])
        if 'set_status_function' in kwargs:
            self.set_status_function(kwargs['set_status_function'])

        self.p = device  # connection to the device hardware
        for a in range(4):
            if self.p.achans[a].yaxis.size < 10000:
                self.p.achans[a].yaxis = np.zeros(10000)
                print('restored yaxis', a, self.p.achans[a].yaxis.size)

        self.setupUi(self)
        from pyqtgraph.opengl import GLSurfacePlotItem, GLGridItem


        g = GLGridItem()
        g.scale(1,1,1)
        g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        self.plotView.addItem(g)


        ## Animated example
        ## compute surface vertex data
        x = np.linspace(-8, 8, self.NP)
        y = np.linspace(-8, 8, self.NP)
        self.z = np.zeros([self.NP,self.NP])
        self.traceCounter = 0

        self.plot = GLSurfacePlotItem(x=x, y = y, shader='normalColor', computeNormals=True, smooth=False)
        self.plotView.addItem(self.plot)



        self.singleShotButton.setVisible(self.frozen)
        self.singleShotButton.setVisible(self.frozen)
        self.showMessage = print
        self.scopeProgress.setProperty("maximum", self.NP)

        try:
            self.shelf = shelve.open('seelab.shelf', 'c')
            theme = self.shelf['theme']
            self.shelf.close()
        except:
            theme = 'default2'

        if theme == 'default2':
            penCols2  = ['#550', '#0f0', '#f00','magenta','cyan']     #pqtgraph pen colors
            htmlcols2  = ['#550', '#0f0', '#f00','magenta','cyan']     # high contrast pen colors for black bg

        else:
            penCols2  = ['#ddd', '#0ff', '#f00','magenta','cyan']     # high contrast pen colors for black bg
            htmlcols2  = ['#ddd', '#0ff', '#f00','magenta','cyan']     # high contrast pen colors for black bg

        self.resultCols = penCols2
        self.traceCols = [pg.mkPen(p, width=1.3) for p in penCols2]
        self.htmlColors = htmlcols2



        self.chanStatus = [1, 0, 0, 0]



        self.set_timebase(self.TBval)

        self.CAP.clicked.connect(self.measure_cap)

        self.FREQ.clicked.connect(self.measure_freq)

        self.OD1.stateChanged.connect(self.control_od1)
        self.CCS.stateChanged.connect(self.control_ccs)
        for a in [self.CS1, self.CS2, self.CS3, self.CS4]:
            a.stateChanged.connect(self.CS_changed)

        for a,mn,mx in zip(['A1','A2','A3'],[-16,-16,-3.3,0],[16,16,3.3,3.3]):
            gauge = Gauge(self,a)
            gauge.setObjectName(a)
            gauge.set_MinValue(mn)
            gauge.set_MaxValue(mx)
            gauge.mouseDoubleClickEvent = gauge.toggleChecked
            self.gaugeLayout.addWidget(gauge)
            self.voltMeterCB[a] = gauge

        self.A1Range.currentIndexChanged['int'].connect(self.select_range)

        self.A1Box.setChecked(True) #A1 enabled
        self.A1Map.addItems(self.sources)

        self.recover()


        self.timer.timeout.connect(self.update)
        self.timer.start(self.TIMER)


        self.index = 0

    def themeStateChanged(self, state):
        print('themeStateChanged', state)
        if state:
            self.themeBox.setIcon(QtGui.QIcon(":/controls/dark.png"))  # Set dark theme icon
            self.setTheme('material')
        else:
            self.themeBox.setIcon(QtGui.QIcon(":/controls/light.png"))  # Set light theme icon
            self.setTheme('material')



    def set_scope_thread(self, scope_thread):
        self.timer.stop()
        if(scope_thread is None):   
            self.running = False
            return

        self.scope_thread = scope_thread
        self.scope_thread.voltage_ready.connect(self.update_voltage)
        self.scope_thread.resistance_ready.connect(self.update_resistance)
        self.scope_thread.capacitance_ready.connect(self.update_capacitance)
        self.scope_thread.frequency_ready.connect(self.update_frequency)
        self.scope_thread.progress_ready.connect(self.update_progress)
        self.scope_thread.trace_ready.connect(self.update_trace)
        self.running = True
        self.timer.start(self.TIMER)

    def update_voltage(self, source, voltage):
        if source in self.voltMeterCB:
            self.voltMeterCB[source].update_value(voltage)

    def update_resistance(self, res):
        if res != np.inf and res > 100 and res < 100000:
            self.RES.setText('Resistance: <font color="blue">' + self.tr('%5.0f Ohm') % (res))
        else:
            self.RES.setText(self.tr('Resistance: <100Ohm  or  >100k'))

    def update_capacitance(self, capacitance):
        self.measured_cap(capacitance)

    def update_frequency(self, source, frequency, hival):
        self.measured_freq(frequency, hival)

    def update_progress(self,status, trigwait, progress):
        self.WaitingForProgress = False
        if status:
            self.singleShotEnabled = False
        self.scopeProgress.setValue(int(progress))
        if (self.scope_thread.state == SCOPESTATES.CAPTURING and self.scope_thread.polling) or status:
            if self.A1Box.isChecked():
                self.fetch_partial_trace(1, progress, status)

    def toggleFreeze(self):
        self.frozen = not self.frozen
        self.singleShotButton.setVisible(self.frozen)
        self.singleShotButton.setVisible(self.frozen)
        if self.frozen:
            self.FreezeButton.setIcon(QIcon(':/controls/play.svg'))
            self.FreezeButton.setText('Resume')
        else:
            self.FreezeButton.setIcon(QIcon(':/controls/stop.svg'))
            self.FreezeButton.setText('Freeze')
            self.scope_thread.clearQueue()
            self.scope_thread.state = SCOPESTATES.FREE

    def singleShot(self):
        self.scope_thread.state = SCOPESTATES.FREE
        self.singleShotEnabled = True

    def fetch_partial_trace(self,channel_num, progress, finalFetch=False):
        ch = channel_num - 1
        if progress - self.scope_thread.device.achans[ch].fetched_length > 50 or finalFetch: #50 new points have arrived
            self.scope_thread.add_command(Command('fetch_partial_trace',{'channel_num':channel_num, 'progress': progress, 'callback': self.freeScope if finalFetch else None}))
            if finalFetch:
                self.singleShotEnabled = False


    def freeScope(self,*args):
        self.scope_thread.clearQueue()
        self.scope_thread.state = SCOPESTATES.FREE

    def update_trace(self, channel_num):
        ch = 0
        self.timeData  = self.scope_thread.device.achans[ch].get_fetched_xaxis()*1.e-3
        self.voltData  = self.scope_thread.device.achans[ch].get_fetched_yaxis()
        if(len(self.voltData)<50):return
        self.update_voltage(self.source, self.voltData[-1])

        if self.traceCounter >= self.NP:
            self.traceCounter = 0

        self.z[:,self.traceCounter] = self.voltData
        self.plot.setData(z=self.z)
        self.traceCounter+=1

        return
        if self.chanStatus == 1:
            r = 16. / self.rangeVal
            self.traceWidget.setData(self.timeData[:self.NP], self.voltData[:self.NP] * r + 4 * self.offValues[ch])
            if np.max(self.voltData) > self.rangeVal:
                self.msg(self.tr('%s input is clipped. Increase range') % self.source)

    def toggled(self):
        for inp in self.fields:
            if self.cbs[inp].isChecked():
                self.curves[inp].setVisible(True)
                self.gauges[inp][0].set_NeedleColor()
                self.gauges[inp][0].set_enable_filled_Polygon()
            else:
                self.curves[inp].setVisible(False)
                self.gauges[inp][0].set_NeedleColor(255,0,0,30)
                self.gauges[inp][0].set_enable_filled_Polygon(False)


    def recover(self):  # Recover the settings before it got disconnected
        self.showMessage('<font color="green">' + self.tr('Reconnecting...'),500)
        try:
            self.pv1_text(self.p.DAC.values['PV1'])
            self.pv2_text(self.p.DAC.values['PV2'])
            self.select_wave(self.waveindex)
 
            self.select_wgain(self.wgainindex)
            self.set_trigger(self.Triglevel * 1000)

            if self.p:
                self.scope_thread.add_command(Command('set_sqr1',{'frequency':self.SQ1val,'duty_cycle':self.dutyCycle}))
                self.scope_thread.add_command(Command('set_sine',{'frequency':self.AWGval}))
                self.scope_thread.add_command(Command('configure_trigger',{'channel':0,'source':self.source,'level':self.Triglevel,'resolution':12,'prescaler':5}))
                self.scope_thread.add_command(Command('select_range',{'channel':'A1','value':self.RangeVals12[2]}))

            if self.p and self.p.calibrated:
                cal = self.tr('Calibrated ')
            else:
                cal = self.tr('Not Calibrated ')
            self.showMessage('<font color="green">' + self.tr('Device Reconnected:') + cal,500)
            if self.p and self.p.version_number >= 5.0:
                self.pcsFrame.show()
                self.CS1.show()
                self.CS2.show()
                self.CS3.show()
                self.CS4.show()
                self.CCS.hide()
            else:
                self.pcsFrame.hide()
                self.CS1.hide()
                self.CS2.hide()
                self.CS3.hide()
                self.CS4.hide()
                self.CCS.show()

        except Exception as e:
            print(e)
            self.showMessage('<font color="red">' + self.tr('Error. Could not connect. Check cable. '),2000)


    def peak_index(self, xa, ya):
        peak = 0
        peak_index = 0
        for k in range(2, len(ya)):
            if ya[k] > peak:
                peak = ya[k]
                peak_index = xa[k]
        return peak_index

    def save_data(self):
        self.timer.stop()
        fn = QFileDialog.getSaveFileName()
        if fn != '':
            dat = []
            for ch in range(4):
                if self.chanStatus[ch] == 1:
                    dat.append([self.timeData[ch], self.voltData[ch]])
            self.p.save(dat, fn)
            ss = fn
            self.msg(self.tr('Traces saved to ') + ss)
        self.timer.start(self.TIMER)



    def update(self):
        if self.scope_thread is None:
            return

        if not self.scope_thread.device.H.connected:
            return

        self.loopCounter += 1
        if self.loopCounter % 5 == 0 and self.scope_thread.state == SCOPESTATES.FREE:
            self.loopCounter = 0
            for ch in ['A1','A2','A3']:
                if self.voltMeterCB[ch].isChecked() == True:
                    self.scope_thread.add_command(Command('get_voltage', {'channel': ch}))
                else:
                    self.voltMeterCB[ch].update_value(0)

            self.scope_thread.add_command(Command('get_resistance',{}))

        if self.frozen and not self.singleShotEnabled:
            return

        ########### SCOPE IS FREE . START CAPTURE ################
        if self.scope_thread.state == SCOPESTATES.FREE:
            A1Map = str(self.A1Map.currentText())
            self.WaitingForProgress = False
            if (A1Map in self.sources):
                self.scope_thread.state = SCOPESTATES.CAPTURING
                self.scope_thread.add_command(Command('capture_hr', {'channel_input': A1Map, 'samples': self.NP, 'timebase': self.TG, 'trigger': self.trigEnable}))
                self.scope_thread.fetchTime = time.time() + 1e-6 * self.NP * self.TG


        ########### SCOPE IS CAPTURING . FETCH PERIODIC PROGRESS ################
        elif self.scope_thread.state == SCOPESTATES.CAPTURING and not self.WaitingForProgress:
            if self.scope_thread.polling:
                self.scope_thread.add_command(Command('oscilloscope_progress',{}))
                self.WaitingForProgress = True
            elif time.time() - self.scope_thread.fetchTime > 0.02:
                self.scope_thread.add_command(Command('oscilloscope_progress',{}))
                self.WaitingForProgress = True

        elif self.scope_thread.state == SCOPESTATES.CAPTURING_FULLSPEED and time.time() - self.scope_thread.fetchTime > 0.02:
                self.scope_thread.add_command(Command('fetch_trace',{'channel_num':1, 'progress': self.NP}))
                self.scope_thread.state = SCOPESTATES.COMPLETED



    # End of update

    def toggleWithoutSignal(self, cb, state):
        cb.blockSignals(True)
        cb.setChecked(state)
        cb.blockSignals(False)

    def show_diff(self):
        if self.Diff.isChecked() == False:
            self.diffTraceW.setData([0, 0], [0, 0])



    def select_range(self, index):
        self.rangeText = self.Ranges12[index]
        self.rangeVal = self.RangeVals12[index]
        self.scope_thread.add_command(Command('select_range',{'channel':'A1','value':self.RangeVals12[index]}))

        ss1 = '%s' % self.source
        ss2 = '%s' % self.rangeText
        self.msg(self.tr('Range of') + ss1 + self.tr(' set to ') + ss2)

    def peak_index(self, xa, ya):
        peak = 0
        peak_index = 0
        for k in range(2, len(ya)):
            if ya[k] > peak:
                peak = ya[k]
                peak_index = xa[k]
        return peak_index

    def close(self):
        self.timer.stop()
        print('goodbye.')

    def save_data(self):
        self.timer.stop()
        fn = QFileDialog.getSaveFileName()
        if fn != '':
            dat = []
            for ch in range(4):
                if self.chanStatus[ch] == 1:
                    dat.append([self.timeData[ch], self.voltData[ch]])
            self.p.save(dat, fn)
            ss = fn
            self.msg(self.tr('Traces saved to ') + ss)
        self.timer.start(self.TIMER)


    def set_status_function(self,func):
        self.showMessage = func

    def set_trigger(self, tr):
        # Update the position of the trigger arrow

        self.Triglevel = tr * 0.001  # convert to volts
        self.scope_thread.add_command(Command('configure_trigger',{'channel':0,'source':self.source,'level':self.Triglevel,'resolution':12,'prescaler':5}))



    def set_timebase(self, tb):
        self.TBval = tb
        msperdiv = self.tbvals[int(tb)]  # millisecs / division
        totalusec = msperdiv * 1000 * 10.0  # total 10 divisions

        self.TG = int(totalusec / self.NP)
        sumchan = sum(self.chanStatus)
        if self.TG < 1 and sumchan ==1:
            self.TG = 1
        elif self.TG < 2 and sumchan == 2:
            self.TG = 1.5
        elif self.TG < 2 and sumchan >2:
            self.TG = 2
        elif self.TG > self.MAXDEL:
            self.TG = self.MAXDEL
        delta = (self.TG*self.NP*1e-3)*0.002


    def pv1_text(self,val):
        if self.PV1min <= val <= self.PV1max:
            self.PV1val = val

            self.scope_thread.add_command(Command('set_pv1',{'voltage':val}))
            self.PV1slider.setValue(int(val * 1000))

    def pv1_slider(self, pos):
        val = float(pos) / 1000.0
        if self.PV1min <= val <= self.PV1max:
            self.PV1val = val
            self.PV1Label.setText(f'PV1: {val:.2f}')
            self.scope_thread.add_command(Command('set_pv1',{'voltage':val}))

    def pv2_text(self,val):
        if self.PV2min <= val <= self.PV2max:
            self.PV2val = val
            self.scope_thread.add_command(Command('set_pv2',{'voltage':val}))
            self.PV2slider.setValue(int(val * 1000))
            self.pcsVal_I.setText(f'{(val + 3.3) / 6.6:.2f}')

            self.PV2Label.setText(f'PV2: {val:.2f}')

    def pv2_slider(self, pos):
        val = float(pos) / 1000.0
        if self.PV2min <= val <= self.PV2max:
            self.PV2val = val
            self.PV2Label.setText(f'PV2: {val:.2f}')
            self.pcsVal_I.setText('%.2f mA' % (3.3 - 3.3 * ((val + 3.3) / 6.6)))

            self.scope_thread.add_command(Command('set_pv2',{'voltage':val}))

    def pcs_slider(self, val):
        self.PV2slider.setValue(int(val))


    def sq1_text(self,val):
        if self.SQ1min <= val <= self.SQ1max:
            self.SQ1val = val
            self.SQ1slider.setValue(int(self.SQ1val))

            if 0 <= val < .1: val = 0
            self.SQ1Label.setText(f'SQ1: {val:d}')
            self.scope_thread.add_command(Command('set_sqr1',{'frequency':val,'duty_cycle':self.dutyCycle}))
        else:
            self.SQ1Label.setText(f'SQ1: {self.SQ1min:d}')

    def sq1_slider(self, val):
        if self.SQ1min <= val <= self.SQ1max:
            self.SQ1val = val
            self.SQ1Label.setText(f'SQ1: {val:d}')
            self.scope_thread.add_command(Command('set_sqr1',{'frequency':self.SQ1val,'duty_cycle':self.dutyCycle}))

    def sq1_dc_slider(self, val):
        if 0 <= val <= 10000:
            self.dutyCycle = val/100.  #0-100 scale from 0-10K
            self.SQ1DCLabel.setText(f'DC: {self.dutyCycle:.2f}')
            self.scope_thread.add_command(Command('set_sqr1',{'frequency':self.SQ1val,'duty_cycle':self.dutyCycle}))

    def sq1_dc_text(self, val):
        if 0 <= val <= 100:
            self.dutyCycle = val
            self.SQ1DCLabel.setText(f'DC: {val:.2f}')
            self.SQ1DCslider.setValue(val*100)
            self.scope_thread.add_command(Command('set_sqr1',{'frequency':self.SQ1val,'duty_cycle':self.dutyCycle}))

    def select_wgain(self, index):
        self.wgainindex = index
        self.scope_thread.add_command(Command('set_sine_amp',{'index':index }))

    def set_wave(self):
        if not self.p: return
        if self.waveindex <= 1:
            self.scope_thread.add_command(Command('set_wave',{'frequency':self.AWGval,'type':self.Waves[self.waveindex]}))                
            ss = '%6.2f' % self.AWGval
            self.msg(self.tr('AWG set to ') + ss + self.tr(' Hz'))
        else:
            self.scope_thread.add_command(Command('set_sqr2',{'frequency':self.AWGval,'duty_cycle':50}))
            self.msg(self.tr('Output Changed from WG to SQ2'))

    def select_wave(self, index):
        self.waveindex = index
        self.set_wave()

    def awg_text(self, val):
        try:
            if self.AWGmin <= val <= self.AWGmax:
                self.AWGval = val
                self.AWGslider.setValue(int(self.AWGval))
                self.set_wave()
        except:
            return

    def awg_slider(self, val):
        if self.AWGmin <= val <= self.AWGmax:
            self.AWGval = val
            self.WGLabel.setText(f'WG: {val:d} Hz')
            self.set_wave()

    def test(self):
        print('what?')

    def CS_changed(self):
        pos = 0
        if self.CS1.isChecked(): pos |= 1
        if self.CS2.isChecked(): pos |= 2
        if self.CS3.isChecked(): pos |= 4
        if self.CS4.isChecked(): pos |= 8
        self.scope_thread.add_command(Command('set_multiplexer',{'pos':pos}))

    def control_od1(self):
        state = self.OD1.isChecked()
        self.scope_thread.add_command(Command('set_state',{'OD1':1 if state else 0}))

    def control_ccs(self):
        state = self.CCS.isChecked()
        self.scope_thread.add_command(Command('set_state',{'CCS':1 if state else 0}))

    def measure_cap(self):
        self.scope_thread.add_command(Command('get_capacitance',{}))

    def measured_cap(self, value = None):
        cap = value
        if cap == None:
            self.msg(self.tr('Capacitance too high or short to ground'))
        else:
            if cap < 1.0e-12:
                self.CAP.setText('CAP(IN1) ' + self.tr(' : < 1pF'))
            elif cap < 1.0e-9:
                ss = '%6.1f' % (cap * 1e12)
                self.CAP.setText('CAP(IN1) ' + ss + self.tr(' pF'))
            elif cap < 1.0e-6:
                ss = '%6.1f' % (cap * 1e9)
                self.CAP.setText('CAP(IN1) ' + ss + self.tr(' nF'))
            elif cap < 1.0e-3:
                ss = '%6.1f' % (cap * 1e6)
                self.CAP.setText('CAP(IN1) ' + ss + self.tr(' uF'))


    def measure_freq(self):
        self.scope_thread.add_command(Command('get_freq', {'channel': 'IN2'}))

    def measured_freq(self, fr, hi):
        if fr > 0:
            T = 1. / fr
            dc = hi * 100 / T
            self.FREQ.setText(u'FREQUENCY(IN2) ' + self.tr('%5.1fHz %4.1f%%') % (fr, dc))
        else:
            self.FREQ.setText(u'FREQUENCY(IN2) ' + self.tr('X'))


    def msg(self, m):
        self.showMessage(self.tr(m),2000)


if __name__ == '__main__':
    import eyes17.eyes

    dev = eyes17.eyes.open()
    app = QApplication(sys.argv)

    # translation stuff
    lang = QLocale.system().name()
    t = QTranslator()
    t.load("lang/" + lang, os.path.dirname(__file__))
    app.installTranslator(t)
    t1 = QTranslator()
    t1.load("qt_" + lang,
            QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(t1)

    mw = Expt(dev)
    mw.show()
    sys.exit(app.exec_())
