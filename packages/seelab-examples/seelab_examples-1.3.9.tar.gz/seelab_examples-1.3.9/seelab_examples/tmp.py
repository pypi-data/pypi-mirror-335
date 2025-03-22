# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import sys, time, math, os.path

import utils
from QtVersion import *
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QMovie
import sys, time
from .utils import pg
import numpy as np
import eyes17.eyemath17 as em
from functools import partial
from .utils import to_si_prefix
from .layouts import schoolscope_layout
from .layouts.advancedLoggerTools import LOGGER
from .layouts.sensor_utilities import DIOSENSOR, DIOROBOT, DIOCONTROL
from .layouts.gauge import Gauge

from .utilities.devThread import Command, SCOPESTATES
from enum import Enum

import shelve

class Expt(QtWidgets.QWidget, schoolscope_layout.Ui_Form):
    TIMER = 10
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
    timeData = [None] * 5
    voltData = [None] * 5 #chans+diff
    voltDataFit = [None] * 5
    traceWidget = [None] * 5
    fft_traceWidget = [None] * 5
    lockin_traces = [None] * 4
    offSliders = [None] * 4
    offValues = [0] * 4
    DiffTraceW = None
    fitResWidget = [None] * 4
    chanSelCB = [None] * 4
    rangeSelPB = [None] * 4
    fitSelCB = [None] * 5
    fitSelLabels = [None] * 5
    fitFlags = [0] * 5
    Amplitude = [0] * 5
    Frequency = [0] * 5
    Phase = [0] * 5
    rangeVals = [4] * 5  # selected value of range
    rangeTexts = ['4 V'] * 5  # selected value of range
    scaleLabs = [None] * 5  # display fullscale value inside pg
    voltMeters = [None] * 3
    voltMeterCB = {}
    valueLabel = None
    trigEnable = True
    traceCounter=0

    sources = ['A1', 'A2', 'A3', 'MIC', 'SEN', 'IN1', 'AN8']

    tbvals = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7 , 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 5.0, 10.0, 20.0, 30., 40., 50., 100. , 500., 2000.,4000]  # allowed timebase values(mS)
    NP = 1000  # Number of samples
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
        self.showMessage = print
        self.errored = False
        self.autosetA1Flag = -1
        self.autosetA2Flag = -1
        self.optimum_tb = 0



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

        self.autosetButton.setVisible(False)
        self.singleShotButton.setVisible(self.frozen)
        self.actionFrame.setVisible(self.frozen)
        self.scopeProgress.setProperty("maximum", self.NP)


        try:
            self.shelf = shelve.open('seelab.shelf', 'c')
            theme = self.shelf['theme']
            self.shelf.close()
        except:
            theme = 'default2'


        spingif = os.path.join(os.path.dirname(__file__),'interactive/spin.gif')
        self.loading_label.setScaledContents(True)  
        self.loading_movie = QMovie(spingif)  # Path to your spinning icon
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setVisible(False)  # Initially hidden



        self.plot = pg.PlotWidget(self.pwinview)
        self.fft_plot = pg.PlotWidget(self.pwinview)
        self.fft_plot.setXRange(0, 10e3)
        self.lockin_title = "Digital Lock-In Amplifier (Ref: A1 , Signal: A2)"
        self.lockin_plot = pg.PlotWidget(self.pwinview,title=self.lockin_title)
        self.lockin_plot.getPlotItem().setTitle(self.lockin_title)
        self.lockin_plot.setXRange(0, self.TG*self.NP*1e-6)

        if theme == 'default2':
            penCols2  = ['#550', '#0f0', '#f00','magenta','cyan']     #pqtgraph pen colors
            htmlcols2  = ['#550', '#0f0', '#f00','magenta','cyan']     # high contrast pen colors for black bg
            self.plot.setBackground("w")
            self.fft_plot.setBackground("w")
            self.lockin_plot.setBackground("w")

        else:
            penCols2  = ['#ddd', '#0ff', '#f00','magenta','cyan']     # high contrast pen colors for black bg
            htmlcols2  = ['#ddd', '#0ff', '#f00','magenta','cyan']     # high contrast pen colors for black bg

        self.resultCols = penCols2
        self.traceCols = [pg.mkPen(p, width=1.3) for p in penCols2]
        self.htmlColors = htmlcols2



        self.plotLayout.addWidget(self.plot)
        self.plotLayout.addWidget(self.fft_plot)
        self.fft_plot.hide()

        self.plotLayout.addWidget(self.lockin_plot)
        self.lockin_plot.hide()

        range_ = self.plot.getViewBox().viewRange() 
        self.plot.getViewBox().setLimits(yMin=-16, yMax=16, xMin=0)  
        self.plot.setMouseEnabled(x=False, y=True)  # Disable mouse zooming on x-axis
        #self.plot = pg.PlotWidget(self.pwinview)
        self.fft_plot.getViewBox().setLimits(xMin=0, xMax=50e3, yMin=0, yMax=10)  


        # Create legend
        self.legend = pg.LegendItem((80,60), offset=(70,20), labelTextSize='13pt')
        self.legend.setParentItem(self.plot.graphicsItem())


        self.chanStatus = [1, 0, 0, 0]

        self.offSliders = [self.slider1, self.slider2, self.slider3, self.slider4]
        for ch in range(self.MAXCHAN):
            self.offSliders[ch].valueChanged.connect(partial(self.set_offset, ch))
            self.offSliders[ch].setStyleSheet('''QSlider::handle:vertical{background: %s;};''' % (self.htmlColors[ch]))
        self.plot.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.updateTV)
        self.plot.showGrid(x=True, y=True)  # with grid


        for k in range(self.MAXRES):  # pg textItem to show the Results
            self.resLabs[k] = pg.TextItem()
            self.plot.addItem(self.resLabs[k])


        vLine = pg.InfiniteLine(angle=90, movable=False, pen='r')
        self.plot.addItem(vLine, ignoreBounds=True)
        self.plot.vLine = vLine
        self.plot.vLine.setPos(-1)

        self.plot.disableAutoRange()
        ax = self.plot.getAxis('bottom')
        labelStyle = {'color': 'rgb(100,150,100)', 'font-size': '12pt'}
        ax.setLabel(self.tr('Time'),units='S',**labelStyle)
        ay = self.plot.getAxis('left')
        ay.setStyle(showValues=False)
        ay.setLabel('')
        ticks = range(-16,17,4)
        ay.setTicks([[(v, str(v)) for v in ticks ]])

        ax = self.fft_plot.getAxis('bottom')
        ax.setLabel(self.tr('Frequency'))
        ay = self.fft_plot.getAxis('left')
        ay.setLabel('Magnitude')

        ax = self.lockin_plot.getAxis('bottom')
        labelStyle = {'color': 'rgb(100,150,100)', 'font-size': '12pt'}
        ax.setLabel(self.tr('Time'),units='S',**labelStyle)
        ay = self.lockin_plot.getAxis('left')
        ay.setStyle(showValues=False)
        ay.setLabel('')
        ticks = range(-16,17,4)
        ay.setTicks([[(v, str(v)) for v in ticks ]])
        self.lockin_plot.showGrid(x=True, y=True)  # with grid


        self.set_timebase(self.TBval)
        self.plot.disableAutoRange()
        self.set_timebase(self.TBval)
        self.plot.setYRange(-16, 16)
        # Set y-axis ticks in steps of 4

        #self.plot.hideButtons()  # Do not show the 'A' button of pg

        # Create arrow item for trigger level
        self.trigger_arrow = pg.ArrowItem(angle=180, tipAngle=30, baseAngle=30, pen='g', brush='#333')
        self.plot.addItem(self.trigger_arrow)
        self.trigger_arrow.setPos( 0.,0. )  # Set initial position to 0 volts
        #self.trigger_arrow.hide()  # Hide initially


        for ch in range(self.MAXCHAN):  # initialize the pg trace widgets
            self.traceWidget[ch] = self.plot.plot([0, 0], [0, 0], pen=self.traceCols[ch], name=self.sources[ch])
            self.fft_traceWidget[ch] = self.fft_plot.plot([0, 0], [0, 0], pen=self.traceCols[ch], name=self.sources[ch])

        self.lockin_trace_names=["In-Phase Component","Quadrature Component","Amplitude","Phase"]
        for ch in range(4):
            self.lockin_traces[ch] = self.lockin_plot.plot([0, 0], [0, 0], pen=self.traceCols[ch], name=self.lockin_trace_names[ch])

        self.diffTraceW = self.plot.plot([0, 0], [0, 0], pen=self.traceCols[-1], name='Diff')

        self.CAP.clicked.connect(self.measure_cap)

        self.FREQ.clicked.connect(self.measure_freq)

        self.OD1.stateChanged.connect(self.control_od1)
        self.CCS.stateChanged.connect(self.control_ccs)
        for a in [self.CS1, self.CS2, self.CS3, self.CS4]:
            a.stateChanged.connect(self.CS_changed)

        self.first_valid_fit = -1
        self.chanSelCB = [self.A1Box, self.A2Box, self.A3Box, self.MICBox]
        self.rangeSelPB = [self.A1Range, self.A2Range, self.A3Range, self.MICRange]
        self.fitSelCB = [self.A1FitCombo, self.A2FitCombo, self.A3FitCombo, self.MICFitCombo, self.DiffFitCombo]
        self.fitSelLabels = [self.A1Fit, self.A2Fit, self.A3Fit, self.MICFit, self.DiffFit]
        self.fitOptions = ['FIT', 'sine', 'p2p', 'rms', 'avg', 'min', 'max']
        for b in self.fitSelCB:
            b.addItems(self.fitOptions)

        for a,mn,mx in zip(['A1','A2','A3'],[-16,-16,-3.3,0],[16,16,3.3,3.3]):
            gauge = Gauge(self,a)
            gauge.setObjectName(a)
            gauge.set_MinValue(mn)
            gauge.set_MaxValue(mx)
            gauge.mouseDoubleClickEvent = gauge.toggleChecked
            self.gaugeLayout.addWidget(gauge)
            self.voltMeterCB[a] = gauge

        for ch in range(4):
            self.chanSelCB[ch].stateChanged.connect(partial(self.select_channel, ch))
            self.chanSelCB[ch].setStyleSheet('''border: 1px solid %s;''' % (self.htmlColors[ch]))  # <font color="%s">

            self.rangeSelPB[ch].currentIndexChanged['int'].connect(partial(self.select_range, ch))

        self.chanSelCB[0].setChecked(True) #A1 enabled
        self.chanSelCB[1].setChecked(True) #A2 enabled
        self.trigSources = ['CH1','CH2','CH3','CH4','OFF']
        self.trigBox.addItems(self.trigSources)
        self.A1Map.addItems(self.sources)
        self.updateLegend()

        self.recover()


        self.timer.timeout.connect(self.update)
        self.timer.start(self.TIMER)


    def autosetTG(self):
        self.TBslider.setValue(self.optimum_tb)

    def autosetA1(self):
        if(self.A1Map.currentText()=='A1'):
            self.select_range(0,0)
            self.autosetA1Flag = 2 #2 captures before setting A1 range.


    def applyAutosetA1(self):
        max = self.voltData[0].max()
        index = np.argmin(np.abs(self.RangeVals12-max))
        if index>0 and max>self.RangeVals12[index]:
            index -=1 #Choose the next larger range.
        self.A1Range.blockSignals(True)
        self.A1Range.setCurrentIndex(index)
        self.A1Range.blockSignals(False)
        self.select_range(0,index)

    def autosetA2(self):
        self.select_range(1,0)
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
        self.select_range(1,index)

    def themeStateChanged(self, state):
        print('themeStateChanged', state)
        if state:
            self.themeBox.setIcon(QtGui.QIcon(":/controls/dark.png"))  # Set dark theme icon
            self.setTheme('material')
        else:
            self.themeBox.setIcon(QtGui.QIcon(":/controls/light.png"))  # Set light theme icon
            self.setTheme('material')

    def mouseMoved(self,evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.plot.sceneBoundingRect().contains(pos):
            mousePoint = self.plot.plotItem.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            #if index > 0 and index < len(self.timeData[0]):
            #    self.cursorLabel.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), self.voltData[0][index], self.voltData[1][index]))
            self.plot.vLine.setPos(mousePoint.x())
            self.plot.hLine.setPos(mousePoint.y())


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
        self.scope_thread.connErrorSignal.connect(self.connError)
        self.running = True
        self.errored = False
        self.timer.start(self.TIMER)

    def update_voltage(self, source, voltage):
        if source in self.voltMeterCB:
            self.voltMeterCB[source].update_value(voltage)
            ###PCS Monitoring in version 5+
        elif self.p.version_number >= 5.0 and source=='AN8':  # Current source monitoring
            self.pcsVal.display(int(voltage * 1e3))


    def update_resistance(self, res):
        if 50 < res < 100000:
            self.RES.setText(f'<p style="color:green;font-size:30px">Resistance {to_si_prefix(res,4,"&Omega;")}</p>')
        elif 10 < res < 500000:
            self.RES.setText(f'<p style="color:red;font-size:30px">Resistance {to_si_prefix(res,4,"&Omega;")}</p>')
        else:
            self.RES.setText(self.tr('Resistance: <100 Ohm  or  >100k'))

    def update_capacitance(self, capacitance):
        self.measured_cap(capacitance)
        self.loading_label.setVisible(False)  # hide the loading icon
        self.loading_movie.stop()  # Stop the spinning animation

    def update_frequency(self, source, frequency, hival):
        self.measured_freq(frequency, hival)
        self.loading_label.setVisible(False)  # hide the loading icon
        self.loading_movie.stop()  # Stop the spinning animation


    def update_progress(self,status, trigwait, progress):
        self.scopeProgress.setValue(int(progress))
        if (self.scope_thread.state == SCOPESTATES.CAPTURING and self.scope_thread.polling) or status:
            if self.chanStatus[2] == 1 or self.chanStatus[3] == 1:  # channel 3 or 4 selected
                self.fetch_partial_trace(1, progress)
                self.fetch_partial_trace(2, progress)
                self.fetch_partial_trace(3, progress)
                self.fetch_partial_trace(4, progress, status)


            elif self.chanStatus[1] == 1:  # channel 2 is selected
                self.fetch_partial_trace(1, progress)
                self.fetch_partial_trace(2, progress, status)

            elif self.chanStatus[0] == 1:  # only A1 selected
                self.fetch_partial_trace(1, progress, status)

        #if status:
        #    #Free after 100mS
        #    QTimer.singleShot(100, self.freeScope)

    def toggleFreeze(self):
        self.frozen = not self.frozen
        self.singleShotButton.setVisible(self.frozen)
        self.actionFrame.setVisible(self.frozen)
        if self.frozen:
            self.FreezeButton.setIcon(QIcon(':/controls/play.svg'))
            self.FreezeButton.setText('Resume')
        else:
            self.FreezeButton.setIcon(QIcon(':/controls/stop.svg'))
            self.FreezeButton.setText('Freeze')
            self.scope_thread.state = SCOPESTATES.FREE

    def singleShot(self):
        self.scope_thread.state = SCOPESTATES.FREE
        self.singleShotEnabled = True

    def fetch_partial_trace(self,channel_num, progress, finalFetch=False):
        ch = channel_num - 1
        if (progress - self.scope_thread.device.achans[ch].fetched_length)*self.TG > 200 or progress==self.NP or finalFetch: #50 new points have arrived
            if progress != self.NP:
                finalFetch = False
            self.scope_thread.add_command(Command('fetch_partial_trace',{'channel_num':channel_num, 'progress': progress, 'callback': self.freeScope if finalFetch else None}))

    def freeScope(self,*args):
        if self.autosetA1Flag==0:
            self.autosetA1Flag = -1
            self.applyAutosetA1()
        elif self.autosetA1Flag>0:
            self.autosetA1Flag -=1

        if self.autosetA2Flag==0:
            self.autosetA2Flag = -1
            self.applyAutosetA2()
        elif self.autosetA2Flag>0:
            self.autosetA2Flag -=1

        self.scope_thread.state = SCOPESTATES.FREE

    def show_fft(self,state):
        if state:
            self.fft_plot.show()
            self.NP = 10000
            if self.TBval < 7:
                self.TBslider.setValue(7)
        else:
            self.fft_plot.hide()
            self.NP = 1000
        self.set_timebase(self.TBval)
        self.scope_thread.state = SCOPESTATES.FREE


    def show_lockin(self,state):
        if state:
            global butter, filtfilt, hilbert
            from scipy.signal import butter, filtfilt, hilbert
            self.plot.setMouseEnabled(x=True, y=True)  # mouse zooming on x-axis
            self.lockin_plot.show()
            self.NP = 5000
            if self.TBval < 12:
                self.TBslider.setValue(12)
        else:
            self.plot.setMouseEnabled(x=False, y=True)  # mouse zooming on x-axis
            self.lockin_plot.hide()
            self.NP = 1000
        self.set_timebase(self.TBval)
        self.scope_thread.state = SCOPESTATES.FREE


    def update_trace(self, channel_num):
        ch = channel_num - 1
        if ch==0:
            self.first_valid_fit = -1

        self.timeData[ch]  = self.scope_thread.device.achans[ch].get_fetched_xaxis()*1.e-6
        self.voltData[ch]  = self.scope_thread.device.achans[ch].get_fetched_yaxis()
        if(len(self.voltData[ch])<50):return

        self.update_voltage(self.sources[ch], self.voltData[ch][-1])


        fitfound = 0
        if self.chanStatus[ch] == 1:
            r = 16. / self.rangeVals[ch]
            self.traceWidget[ch].setData(self.timeData[ch][:self.NP], self.voltData[ch][:self.NP] * r + 4 * self.offValues[ch])
            #fft of data
            if self.FFTBox.isChecked() and self.voltData[ch].size == self.NP:
                xa, ya = em.fft(self.voltData[ch], self.TG*1e-3)
                self.fft_traceWidget[ch].setData(xa, ya)




            if np.max(self.voltData[ch]) > self.rangeVals[ch]:
                self.msg(self.tr('%s input is clipped. Increase range') % self.sources[ch])

            fitfound = self.applyFits(ch)

        if fitfound>0:
            self.autosetButton.setVisible(True)

        if self.Diff.isChecked() == True and self.chanStatus[0] == 1 and self.chanStatus[1] == 1:
            if ch==1:
                r = 16. / self.rangeVals[0]
                maxlen = min(len(self.voltData[0]), len(self.voltData[1]))
                self.timeData[4] = self.timeData[0]
                self.voltData[4] = self.voltData[0] - self.voltData[1]
                self.diffTraceW.setData(self.timeData[4][:maxlen], r * (self.voltData[4][:maxlen]))
                self.applyFits(4)
        else:
            self.diffTraceW.setData([0, 0], [0, 0])


        # Lock-in amplifier calculations
        if self.lockinBox.isChecked() and ch==1 and self.chanStatus[0] == 1 and self.chanStatus[1] == 1 and self.voltData[0].size == self.NP and self.voltData[1].size == self.NP:
            self.lockin_plot.setXRange(0, self.TG*self.NP*1e-6)
            signal_freq = self.p.sinefreq
            t = self.timeData[0][:self.NP]
            v = self.voltData[0][:self.NP] # A1 . Reference
            vv = self.voltData[1][:self.NP] #A2 . signal
            print(f'lock-in. {self.p.sinefreq} Hz , {self.NP}, {self.TG} uS' )

            sampling_rate = 1 / (self.TG * 1e-6)  # Calculate sampling rate from time array

            reference_signal = v
            scaling_factor = np.max(np.abs(v)) # Get normalization factor
            reference_signal = v / scaling_factor  # Normalize to ±1    
            reference_shifted = np.imag(hilbert(reference_signal))
            vv_scaled  = vv/scaling_factor

            # Multiply the output signal (vv) with the reference signals
            in_phase = (vv - np.mean(vv)) * reference_signal
            quadrature = (vv - np.mean(vv)) * reference_shifted

            # Design a low-pass filter to extract DC components
            def low_pass_filter(data, cutoff, fs, order=5):
                nyquist = 0.5 * fs
                normal_cutoff = cutoff / nyquist
                b, a = butter(order, normal_cutoff, btype='low', analog=False)
                y = filtfilt(b, a, data)
                return y

            # Apply low-pass filter to in-phase and quadrature components
            cutoff_freq = signal_freq / 10  # Lower cutoff frequency for better DC extraction (Hz)
            in_phase_filtered = low_pass_filter(in_phase, cutoff_freq, sampling_rate)
            quadrature_filtered = low_pass_filter(quadrature, cutoff_freq, sampling_rate)

            # Calculate amplitude and phase
            amplitude = 2 * np.sqrt(in_phase_filtered**2 + quadrature_filtered**2)  # Scale by 2
            phase = np.arctan2(quadrature_filtered, in_phase_filtered)

            # Average the amplitude and phase to get single DC values
            window_size = 20  # Adjust as needed. last N points.
            dc_amplitude = np.mean(amplitude[-window_size:])
            dc_phase = np.mean(phase[-window_size:])

            self.lockin_traces[0].setData(t, in_phase_filtered)
            self.lockin_traces[1].setData(t, quadrature_filtered)
            self.lockin_traces[2].setData(t, amplitude)
            self.lockin_traces[3].setData(t, phase)
            self.lockin_plot.getPlotItem().setTitle(f'Lock-in A1:Ref, A2: Signal | Amp: {dc_amplitude:.4f} V, dPhi: {180*dc_phase/np.pi:.4f} °')

    def applyFits(self,ch):
        fitfound = 0
        if self.fitSelCB[ch].currentText() == 'sine':
            try:
                fa = em.fit_sine(self.timeData[ch], self.voltData[ch])
            except Exception as err:
                print('fit_sine error:', err)
                fa = None
            if fa != None:
                self.voltDataFit[ch] = fa[0]
                self.Amplitude[ch] = abs(fa[1][0])
                self.Frequency[ch] = fa[1][1]
                self.Phase[ch] = fa[1][2] * 180 / em.pi
                if self.first_valid_fit == -1: #Valid fit not found yet.
                    s = self.tr('%5.2f V, %s') % (self.Amplitude[ch], to_si_prefix(self.Frequency[ch],4,'Hz'))
                    self.first_valid_fit = ch
                    self.fitSelLabels[ch].setStyleSheet('color:darkgreen;')
                else :  #show dPhi also
                    s = self.tr('%5.2f V, %s, %.2f°') % (self.Amplitude[ch], to_si_prefix(self.Frequency[ch],4,'Hz'),self.Phase[ch]-self.Phase[self.first_valid_fit])
                    self.fitSelLabels[ch].setStyleSheet('')

                self.fitSelLabels[ch].setText(s)
                fitfound +=1 
                self.optimum_tb = np.argmin(np.abs(self.tbvals - 1000./self.Frequency[ch]))
        elif self.fitSelCB[ch].currentText() == 'p2p':
            s = self.tr('%5.2f V') % (max(self.voltData[ch]) - min(self.voltData[ch]))
            self.fitSelLabels[ch].setText(s)
        elif self.fitSelCB[ch].currentText() == 'avg':
            s = self.tr('%5.2f V') % (np.average(self.voltData[ch]))
            self.fitSelLabels[ch].setText(s)
        elif self.fitSelCB[ch].currentText() == 'rms':
            s = self.tr('%5.2f V') % (np.sqrt(np.average(self.voltData[ch]**2)))
            self.fitSelLabels[ch].setText(s)
        elif self.fitSelCB[ch].currentText() == 'max':
            s = self.tr('%5.2f V') % (max(self.voltData[ch]))
            self.fitSelLabels[ch].setText(s)
        elif self.fitSelCB[ch].currentText() == 'min':
            s = self.tr('%5.2f V') % (min(self.voltData[ch]))
            self.fitSelLabels[ch].setText(s)
        else:
            self.fitSelLabels[ch].setText('')

        return fitfound

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
                self.scope_thread.add_command(Command('configure_trigger',{'channel':0,'source':'A1','level':0}))
                self.scope_thread.add_command(Command('select_range',{'channel':'A1','value':self.RangeVals12[2]}))
                self.scope_thread.add_command(Command('select_range',{'channel':'A2','value':self.RangeVals12[2]}))

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

    def set_offset(self, ch):
        self.offValues[ch] = self.offSliders[ch].value()
        self.updateTriggerArrow()

    def cross_hair(self):
        if self.Cross.isChecked() == False:
            self.plot.vLine.setPos(-1)

    def showVoltagesAtCursor(self, xval):
        t = self.timeData[0]
        index = 0
        for k in range(len(t) - 1):  # find out Time at the cursor position
            if t[k] < xval < t[k + 1]:
                index = k
        if index>=len(self.timeData[0]):
            return


        for k in range(self.MAXRES):
            self.plot.removeItem(self.resLabs[k])

        self.resLabs[0] = pg.TextItem(
            text=self.tr('Time:') + to_si_prefix(t[index],3,'S'),
            color=self.resultCols[0]
        )

        self.resLabs[0].setPos(0, -11)
        self.plot.addItem(self.resLabs[0])

        ctext = ''
        if index > 0 and index < len(self.timeData[0]):
            ctext += "<span style='font-size: 12pt'>x=%0.1f</span><br>" % (t[index])


        for k in range(self.MAXCHAN):
            if self.chanStatus[k] == 1:
                if index>=len(self.voltData[k]):
                    continue

                self.Results[k + 1] = self.tr('%s:%6.2fV ') % (self.sources[k], self.voltData[k][index])
                self.resLabs[k + 1] = pg.TextItem(text=self.Results[k + 1], color=self.resultCols[k])
                self.resLabs[k + 1].setPos(0, -12 - 1.0 * k)
                self.plot.addItem(self.resLabs[k + 1])
                if index > 0 and index < len(self.voltData[k]):
                    ctext += "<span style='font-size: 12pt;color: %s'>%s=%0.1f</span><br>" % (self.resultCols[k],   self.sources[k], self.voltData[k][index])

        #self.cursorLabel.setText(ctext)

    def updateTV(self, evt):
        if self.p == None: return
        if self.Cross.isChecked() == False:
            self.plot.vLine.setPos(-1)
            return
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.plot.sceneBoundingRect().contains(pos):
            mousePoint = self.plot.plotItem.vb.mapSceneToView(pos)
            xval = mousePoint.x()
            self.plot.vLine.setPos(mousePoint.x())
            #self.showVoltagesAtCursor(xval)

    def action_changed(self,action):
        pass

    def connError(self):
        self.showMessage(self.tr('Error. Device disconnected? '),2000)
        self.errored = True

    def update(self):
        if self.scope_thread is None or self.scope_thread.device is None or self.errored:
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

            ###PCS Monitoring in version 5+
            if self.p.version_number >= 5.0:  # Current source monitoring
                self.scope_thread.add_command(Command('get_average_voltage', {'channel': 'AN8'}))


            self.scope_thread.add_command(Command('get_resistance',{}))

        ########### SCOPE IS FREE . START CAPTURE ################
        if self.scope_thread.state == SCOPESTATES.FREE and (not self.frozen or self.singleShotEnabled):
            self.singleShotEnabled = False
            A1Map = str(self.A1Map.currentText())
            self.traceCounter+=1
            if (A1Map in self.sources):
                self.scope_thread.state = SCOPESTATES.CAPTURING
                if self.chanStatus[2] == 1 or self.chanStatus[3] == 1:  # channel 3 or 4 selected
                    if self.NP>2500:
                        self.NP = 2500
                        self.set_timebase(self.TBval)
                    self.scope_thread.add_command(Command('capture_traces', {'num_channels':4,'channel_input': A1Map, 'samples': self.NP, 'timebase': self.TG, 'trigger': self.trigEnable}))
                elif self.chanStatus[1] == 1:  # channel 2 is selected
                    if self.NP>5000:
                        self.NP = 5000
                        self.set_timebase(self.TBval)
                    self.scope_thread.add_command(Command('capture_traces', {'num_channels':2,'channel_input': A1Map, 'samples': self.NP, 'timebase': self.TG, 'trigger': self.trigEnable}))
                elif self.chanStatus[0] == 1:  # only A1 selected
                    if self.NP>10000:
                        self.NP = 10000
                        self.set_timebase(self.TBval)
                    if self.actionBox.currentIndex() == 1 and self.frozen: #SET_LOW
                        self.toggleWithoutSignal(self.OD1, False)
                        self.scope_thread.add_command(Command('capture_action', {'channel_input': A1Map, 'samples': self.NP, 'timebase': self.TG, 'action': 'SET_LOW'}))
                    elif self.actionBox.currentIndex() == 2 and self.frozen: #SET_HIGH
                        self.toggleWithoutSignal(self.OD1, True)
                        self.scope_thread.add_command(Command('capture_action', {'channel_input': A1Map, 'samples': self.NP, 'timebase': self.TG, 'action': 'SET_HIGH'}))
                    else:#if self.hrBox.isChecked(): #Always fetch highres
                        self.scope_thread.add_command(Command('capture_hr', {'channel_input': A1Map, 'samples': self.NP, 'timebase': self.TG, 'trigger': self.trigEnable}))
                    #else:
                    #    self.scope_thread.add_command(Command('capture_traces', {'num_channels':1,'channel_input': A1Map, 'samples': self.NP, 'timebase': self.TG, 'trigger': self.trigEnable}))
                self.scope_thread.fetchTime = time.time() + 1e-6 * self.NP * self.TG + .05


        ########### SCOPE IS CAPTURING . FETCH PERIODIC PROGRESS ################
        elif self.scope_thread.state == SCOPESTATES.CAPTURING:
            if self.scope_thread.polling:
                self.scope_thread.add_command(Command('oscilloscope_progress',{}))
            elif time.time() - self.scope_thread.fetchTime > 0.02:
                self.scope_thread.add_command(Command('oscilloscope_progress',{}))

        elif self.scope_thread.state == SCOPESTATES.CAPTURING_FULLSPEED and time.time() - self.scope_thread.fetchTime > 0.02:
                self.scope_thread.add_command(Command('fetch_trace',{'channel_num':1, 'progress': self.NP}))
                self.scope_thread.state = SCOPESTATES.COMPLETED

        
        ########### SCOPE IS COMPLETED . FETCH DATA ################

        if self.Cross.isChecked():
            self.showVoltagesAtCursor(self.plot.vLine.x())
            self.updateLegend()
        else:
            for k in range(self.MAXRES):
                try:
                    self.plot.removeItem(self.resLabs[k])
                except:
                    pass



    # End of update

    def toggleWithoutSignal(self, cb, state):
        cb.blockSignals(True)
        cb.setChecked(state)
        cb.blockSignals(False)

    def show_diff(self):
        if self.Diff.isChecked() == False:
            self.diffTraceW.setData([0, 0], [0, 0])

    def showRange(self, ch):
        spacing = self.tbvals[self.TBval]
        self.plot.removeItem(self.scaleLabs[ch])
        if self.chanStatus[ch] == 0:
            return
        #self.scaleLabs[ch] = pg.TextItem(text=self.rangeTexts[ch], color=self.resultCols[ch], angle=315)
        #self.scaleLabs[ch].setPos(ch * spacing / 3, 15.5)
        # self.scaleLabs[ch].setText('hello')
        #self.plot.addItem(self.scaleLabs[ch])
        self.updateLegend()

    def select_channel(self, ch):
        hr = True
        if self.chanSelCB[ch].isChecked() == True:
            self.chanStatus[ch] = 1
            self.traceWidget[ch] = self.plot.plot([0, 0], [0, 0], pen=self.traceCols[ch])
            if ch > 0 : # anything other than A1
                hr = False
        else:
            self.chanStatus[ch] = 0
            self.plot.removeItem(self.traceWidget[ch])

        for a in self.chanSelCB[1:]: #A 2,3,MIC
            if a.isChecked():
                hr = False
        self.highresToggled(hr)
        self.showRange(ch)
        self.updateLegend()

    def select_range(self, ch, index):
        if ch <= 1:
            self.rangeTexts[ch] = self.Ranges12[index]
            self.rangeVals[ch] = self.RangeVals12[index]
            self.scope_thread.add_command(Command('select_range',{'channel':self.sources[ch],'value':self.RangeVals12[index]}))
        else:
            self.rangeTexts[ch] = self.Ranges34[index]
            self.rangeVals[ch] = self.RangeVals34[index]
        self.showRange(ch)
        ss1 = '%s' % self.sources[ch]
        ss2 = '%s' % self.rangeTexts[ch]
        self.msg(self.tr('Range of') + ss1 + self.tr(' set to ') + ss2)
        self.updateTriggerArrow()
        self.updateLegend()

    def updateLegend(self):
        pass
        return
        for ch in range(4):
            self.legend.removeItem(self.traceWidget[ch])
            if self.chanStatus[ch] == 1:
                self.legend.addItem(self.traceWidget[ch], f'{self.sources[ch]}:{self.rangeTexts[ch]}')

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

    def select_trig_source(self, index):
        src = self.trigSources[self.Trigindex]
        self.Trigindex = index
        self.trigEnable = True
        if index > 3:
            self.Trigindex = 0
            self.trigEnable = False

        if self.hrBox.isChecked() and self.scope_thread.device.channels_in_buffer == 1:
            self.scope_thread.add_command(Command('configure_trigger',{'channel':self.Trigindex,'source':self.sources[self.Trigindex],'level':self.Triglevel,'resolution':12,'prescaler':5}))
        else:
            self.scope_thread.add_command(Command('configure_trigger',{'channel':self.Trigindex,'source':self.sources[self.Trigindex],'level':self.Triglevel}))
        self.updateTriggerArrow()

    def set_status_function(self,func):
        self.showMessage = func

    def set_trigger(self, tr):
        # Update the position of the trigger arrow
        self.updateTriggerArrow()

        self.Triglevel = tr * 0.001  # convert to volts
        if self.hrBox.isChecked() and self.scope_thread.device.channels_in_buffer == 1:
            self.scope_thread.add_command(Command('configure_trigger',{'channel':self.Trigindex,'source':self.sources[self.Trigindex],'level':self.Triglevel,'resolution':12,'prescaler':5}))
        else:
            if self.TBval > 3:
                self.scope_thread.add_command(Command('configure_trigger',{'channel':self.Trigindex,'source':self.sources[self.Trigindex],'level':self.Triglevel,'resolution':10,'prescaler':5}))
            else:
                self.scope_thread.add_command(Command('configure_trigger',{'channel':self.Trigindex,'source':self.sources[self.Trigindex],'level':self.Triglevel}))

    def highresToggled(self,state):
        self.scope_thread.state = SCOPESTATES.FREE
        self.scope_thread.clearQueue()
        self.hrBox.setChecked(state)
        if state:
            self.hrBox.setText('12-bit')
            self.scope_thread.add_command(Command('configure_trigger',{'channel':self.Trigindex,'source':self.sources[self.Trigindex],'level':self.Triglevel,'resolution':12,'prescaler':5}))
            self.A2Box.setChecked(False)
            self.A3Box.setChecked(False)
            self.MICBox.setChecked(False)
        else:
            self.hrBox.setText('10-bit')
            self.scope_thread.add_command(Command('configure_trigger',{'channel':self.Trigindex,'source':self.sources[self.Trigindex],'level':self.Triglevel}))

    def updateTriggerArrow(self):
        r = 16. / self.rangeVals[self.Trigindex]

        self.trigger_arrow.setPos(0., self.Triglevel*r + 4*self.offValues[self.Trigindex])  # Update arrow position to the current trigger level
        self.trigger_arrow.setVisible(self.trigEnable)  # Show or hide based on trigger enable state
        self.trigger_arrow.setPen(self.traceCols[self.Trigindex])


    def set_timebase(self, tb):
        self.TBval = tb
        msperdiv = self.tbvals[int(tb)]  # millisecs / division
        totalusec = msperdiv * self.NP * 10.0  # total 10 divisions

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
        for k in range(self.MAXCHAN):
            self.showRange(k)
        delta = (self.TG*self.NP*1e-3)*0.002
        self.plot.getViewBox().setLimits(xMin=-delta, xMax=(self.TG*self.NP*1e-3)+delta )
        self.plot.setXRange(0, self.TG*self.NP*1e-6)
        self.scope_thread.state = SCOPESTATES.FREE


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
        self.loading_label.setVisible(True)  # show the loading icon
        self.loading_movie.start()  # Start the spinning animation


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
        self.loading_label.setVisible(True)  # show the loading icon
        self.loading_movie.start()  # Start the spinning animation

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
