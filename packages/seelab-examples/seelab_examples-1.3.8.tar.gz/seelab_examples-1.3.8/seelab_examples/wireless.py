import sys
import os, time, socket, select
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QIcon,QFont,QCursor
from PyQt5.QtWidgets import QGraphicsScene,QGraphicsPixmapItem,QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer, pyqtSignal  # Import Qt for alignment
from .layouts.gauge import Gauge
from .layouts import wireless
import numpy as np
from scipy.interpolate import RectBivariateSpline
import pyqtgraph as pg
from functools import partial
try:
    import pyqtgraph.opengl as gl
except:
    gl = None   

MPU6050_ID = b'\x00'
HEATCAM_ID = b'\x01'

class CustomViewBox(pg.ViewBox):
    def __init__(self, on_click_callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_click_callback = on_click_callback

    def mouseClickEvent(self, ev):
        super().mouseClickEvent(ev)  # Call the parent method for default behavior
        
        # Check if the left mouse button was clicked
        if ev.button() == 1:  # Left mouse button
            #pos = ev.pos()  # Position of the click in the ViewBox
            # Call the attached slot if available
            if self.on_click_callback:
                self.on_click_callback()

class ClickableLabel(QLabel):
    # Define a custom signal that will be emitted when the label is clicked
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)  # Call the parent method
        self.clicked.emit()  # Emit the custom signal

class SensorSelectButton(QPushButton):
    def __init__(self,*args, **kwargs):
        super().__init__(kwargs.get('ip'))
        self.callback = kwargs.get('callback')
        self.name = kwargs.get('name')
        self.ip = kwargs.get('ip')
        self.clicked.connect(partial(self.callback, self.name, self.ip))


class Expt(QtWidgets.QWidget, wireless.Ui_Form):
    def __init__(self, device, **kwargs):
        super().__init__()
        self.setupUi(self)
        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.SENDPORT=12345
        self.CONFIGPORT=5555
        self.SHOWUP = 101
        self.plots = []
        self.sensorList = {}

        self.bg = None
        # Create a UDP socket for listening to broadcasts
        self.bsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bsock.setblocking(False)
        self.BCASTPORT=9999

        self.sock.bind(('0.0.0.0', self.SENDPORT))
        self.bsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.bsock.bind(('0.0.0.0', self.BCASTPORT))

        self.scanning = True


        self.sensor = MPU6050_ID

        if self.sensor == HEATCAM_ID:
            self.setup_heatcam()
        elif self.sensor == MPU6050_ID:
            self.setup_mpu6050()

        self.first_time = None
        #self.addr = ['10.42.0.16',self.CONFIGPORT]
        self.addr = None
        self.splitter.setSizes([1,4])

        self.graph_updated = time.time()
        # Set up a timer to read UDP data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_udp_data)
        #self.timer.start(200)  # Check for data every 2 ms

        self.btimer = QTimer(self)
        self.btimer.timeout.connect(self.read_bcast_data)
        self.btimer.start(50)  # Check for broadcast data every x mS


    def close(self):
        self.timer.stop()
        self.btimer.stop()
        self.bsock.close()
        self.sock.close()

    def setup_heatcam(self):
        self.clearPlots()

        self.temperature_matrix = np.zeros((24, 32))
        # Define the original grid
        self.hx = np.arange(32)  # 32 columns
        self.hy = np.arange(24)  # 24 rows
        # Define the new (finer) grid for interpolation
        self.new_x = np.linspace(0, 31, 128)  # Interpolated to 128 columns
        self.new_y = np.linspace(0, 23, 96)   # Interpolated to 96 rows
        # Perform the interpolation
        self.spline = RectBivariateSpline(self.hy, self.hx, self.temperature_matrix)
        self.smoothed_matrix = self.spline(self.new_y, self.new_x)

        #--- add non-interactive image with integrated color ------------------
        self.heatplot = self.addPlot("thermal image")
        # Basic steps to create a false color image with color bar:
        self.heatdata = pg.ImageItem(image=self.smoothed_matrix)
        self.heatplot.addItem( self.heatdata )
        self.heatplot.addColorBar( self.heatdata, colorMap='CET-D1A', values=(20, 50) , interactive=True, pen='#8888FF', hoverPen='#EEEEFF', hoverBrush='#EEEEFF80')
        self.heatplot.setMouseEnabled( x=False, y=False)
        self.heatplot.disableAutoRange()
        self.heatplot.hideButtons()
        self.heatplot.setRange(xRange=(0,96), yRange=(0,128), padding=0)
        self.heatplot.showAxes(True, showValues=(True,False,False,True) )



        self.lw = pg.GraphicsLayoutWidget()
        self.lw.setFixedWidth(300)
        self.lw.setFixedHeight(2500)
        self.lw.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.scr = QtWidgets.QScrollArea(self.gaugeFrame)
        self.scr.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scr.setWidget(self.lw)
        self.gaugeLayout.addWidget(self.scr,0,0)
        self.bar_data = pg.colormap.modulatedBarData(width=50)
        self.num_bars = 0

        def add_heading(lw, name):
            lw.addLabel('=== '+name+' ===')
            self.num_bars += 1
            lw.nextRow()

        def add_bar(lw, name, cm):
            lw.addLabel(name)
            imi = pg.ImageItem( self.bar_data )
            imi.setLookupTable( cm.getLookupTable(alpha=True) )
            vb = CustomViewBox(partial(self.set_color_map, name))
            lw.addItem(vb)
            #vb = lw.addViewBox(lockAspect=True, enableMouse=False)
            vb.addItem( imi )
            self.num_bars += 1
            lw.nextRow()

        add_heading(self.lw, 'Color Maps')
        self.list_of_maps = pg.colormap.listMaps()
        self.list_of_maps = sorted( self.list_of_maps, key=lambda x: x.swapcase() )
        for map_name in self.list_of_maps:
            cm = pg.colormap.get(map_name)
            add_bar(self.lw, map_name, cm)

        try:
            import pyqtgraph.opengl as gl
            self.barw = gl.GLViewWidget()
            self.barw.setMinimumSize(300,300)
            self.barw.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
            self.barw.setCameraPosition(distance=50)

            self.bgpos = np.mgrid[0:24, 0:32, 0:1].reshape(3,24,32).transpose(1,2,0)
            # fixed widths, random heights
            self.bgsize = np.empty((24,32,3))
            self.bgsize[...,0:2] = 0.4
            self.bgsize[...,2] = np.random.normal(size=(24,32))

            self.bg = gl.GLBarGraphItem(self.bgpos, self.bgsize)
            self.bg.translate(-12, -16, 0)
            self.barw.addItem(self.bg)

            self.gaugeLayout.addWidget(self.barw,0,1)

        except Exception as e:
            print(e)
            pass

    def set_color_map(self, map_name, m=None):
        print(map_name,m) 
        cm = pg.colormap.get(map_name)
        self.heatdata.setLookupTable( cm.getLookupTable(alpha=True) )



    def setup_mpu6050(self):
        self.clearPlots()
        # Prepare for plotting
        self.plot = self.plotLayout.addPlot(title="Acceleration")
        self.plot.setLabel('left', 'Acceleration (m/s^2)')
        self.plot.setLabel('bottom', 'Time (s)')
        self.curve_x = self.plot.plot(pen='y', name='Ax')
        self.curve_y = self.plot.plot(pen='r', name='Ay')
        self.curve_z = self.plot.plot(pen='g', name='Az')

        self.curve_gx = pg.PlotCurveItem(pen=pg.mkPen(color='cyan', width=1))
        self.curve_gy = pg.PlotCurveItem(pen=pg.mkPen(color='magenta', width=1))
        self.curve_gz = pg.PlotCurveItem(pen=pg.mkPen(color='white', width=1))
        self.combinedPlot = False

        if self.combinedPlot:
            ## create a new ViewBox, link the right axis to its coordinate system
            self.p2 = pg.ViewBox()
            self.plot.showAxis('right')
            self.plot.scene().addItem(self.p2)
            self.plot.getAxis('right').linkToView(self.p2)
            self.p2.setXLink(self.plot)
            self.plot.setLabel('right', 'Gyro', units="<font>&omega;</font>",
                        color='#025b94', **{'font-size':'14pt'})
            self.plot.getAxis('right').setPen(pg.mkPen(color='magenta', width=2))

            self.p2.addItem(self.curve_gx)
            self.p2.addItem(self.curve_gy)
            self.p2.addItem(self.curve_gz)

            self.updateViews()
            self.plot.vb.sigResized.connect(self.updateViews)
        else:
            self.plotLayout.nextRow()
            self.gyroplot = self.plotLayout.addPlot(title="Angular Velocity")
            self.gyroplot.setLabel('left', 'Angular Velocity (rad/s)')
            self.gyroplot.setLabel('bottom', 'Time (s)')
            self.gyroplot.addItem(self.curve_gx)
            self.gyroplot.addItem(self.curve_gy)
            self.gyroplot.addItem(self.curve_gz)

        self.gauge_widgets = []
        r=0;c=0;
        self.ar = 16
        self.gr = 4.5
        for a in ['Ax','Ay','Az','Gx','Gy','Gz']:
            self.gauge_widget = Gauge(self, a)
            self.gauge_widget.setObjectName(a)
            self.gauge_widget.set_MinValue(-1*self.ar)
            self.gauge_widget.set_MaxValue(self.ar)
            self.gauge_widget.setMinimumWidth(50)
            self.gaugeLayout.addWidget(self.gauge_widget, r, c)
            self.gauge_widgets.append(self.gauge_widget)
            if c==1:
                self.gauge_widget.set_MinValue(-1*self.gr)
                self.gauge_widget.set_MaxValue(self.gr)

            r+=1
            if r==3:
                r=0
                c+=1

        self.g_offsets=None
        self.g_avgs = np.zeros([50,3])
        self.g_avg_points=-1

        self.NP = 2000
        self.data = np.full((self.NP, 7), np.nan)  # Store timestamp, x, y, z filled with NaN
        self.ptr = 0


    def clearPlots(self):
        for p in self.plots:
            self.plotLayout.removeItem(p)
        self.plots = []

    def addPlot(self,title):
        x = self.plotLayout.addPlot(title=title)
        self.plots.append(x)
        return x

    ## Handle view resizing 
    def updateViews(self):
        self.p2.setGeometry(self.plot.vb.sceneBoundingRect())
        self.p2.linkedViewChanged(self.plot.vb, self.p2.XAxis)

    def read_bcast_data(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(chr(self.SHOWUP).encode(), ("255.255.255.255", self.CONFIGPORT))

        if select.select([self.bsock],[],[],0.1)[0]:
            dat, addr = self.bsock.recvfrom(20)
            print(dat, addr)
            if dat.decode().startswith('CSPark') and addr[0] not in self.sensorList:
                self.addr = addr[0]                
                self.sensorList[self.addr]=SensorSelectButton(ip = self.addr, callback = self.selectSensor, name = f'{len(self.sensorList)}')
                self.choicesLayout.addWidget(self.sensorList[self.addr])
                self.statusLabel.setText(f'Found Sensors {len(self.sensorList)} @ {self.addr}')
                self.statusLabel.setStyleSheet('color:green;')
                self.controlsFrame.setEnabled(True)

    def selectSensor(self,name,  ip):
        self.addr = ip
        self.statusLabel.setText(f'Set Sensor {name} @ {ip}')

    def crc32(self,data: bytes, polynomial: int = 0x04C11DB7, initial_crc: int = 0xFFFFFFFF, final_xor: int = 0xFFFFFFFF, reflect_input: bool = True, reflect_output: bool = True) -> int:
        """
        Calculate the CRC-32 checksum.

        Args:
            data (bytes): Input data as a bytes object.
            polynomial (int): CRC-32 polynomial (default is 0x04C11DB7).
            initial_crc (int): Initial CRC value (default is 0xFFFFFFFF).
            final_xor (int): Value to XOR with final CRC (default is 0xFFFFFFFF).
            reflect_input (bool): Whether to reflect input bytes.
            reflect_output (bool): Whether to reflect the final CRC value.

        Returns:
            int: Calculated CRC-32 value.
        """

        def reflect_bits(value: int, num_bits: int) -> int:
            """Reflect the `num_bits` least significant bits of `value`."""
            reflection = 0
            for _ in range(num_bits):
                reflection = (reflection << 1) | (value & 1)
                value >>= 1
            return reflection

        # Initialize CRC
        crc = initial_crc

        # Process each byte in the data
        for byte in data:
            if reflect_input:
                byte = reflect_bits(byte, 8)
            crc ^= (byte << 24)
            for _ in range(8):  # Process each bit in the byte
                if crc & 0x80000000:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc <<= 1
                crc &= 0xFFFFFFFF  # Keep CRC 32-bit

        # Final reflection and XOR
        if reflect_output:
            crc = reflect_bits(crc, 32)
        return crc ^ final_xor

    def read_udp_data(self):
        # Receive data

        if not select.select([self.sock],[],[],0.1)[0]:
            return


        if self.sensor == MPU6050_ID:    
            NB = 1+28+4
        elif self.sensor == HEATCAM_ID:
            NB = 1 + 1+ 32*4 + 4 #sensor id, Row number , row data, crc
        else:
            return

        dat, _ = self.sock.recvfrom(NB)

        if(self.sensor == MPU6050_ID):
            if len(dat) == NB:
                dat= dat[1:] #skip ID.
                timestamp, x, y, z, gx, gy, gz, crc = np.frombuffer(dat, dtype=[('timestamp', 'u4'), ('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('gx', 'f4'), ('gy', 'f4'), ('gz', 'f4'), ('crc', np.uint32)])[0]
                timestamp = timestamp * 1e-3 # convert to seconds
                if self.crc32(dat[:NB-5]) != crc:
                    print("CRC mismatch")
                    return

                if self.g_offsets is not None:
                    gx -= self.g_offsets[0]
                    gy -= self.g_offsets[1]
                    gz -= self.g_offsets[2]
                elif self.g_avg_points>0:
                    self.g_avgs[self.g_avg_points-1] = [gx,gy,gz]
                    self.g_avg_points -= 1
                elif self.g_avg_points==0:
                    self.g_offsets = np.zeros([3])
                    self.g_offsets[0] = np.average(self.g_avgs[:,0])
                    self.g_offsets[1] = np.average(self.g_avgs[:,1])
                    self.g_offsets[2] = np.average(self.g_avgs[:,2])
                    self.g_avg_points = -1

                if self.first_time is None:
                    self.first_time = timestamp
                self.data[:-1] = self.data[1:]
                # Update plot data
                self.data[-1] = [timestamp-self.first_time, x, y, z, gx, gy, gz]
                self.ptr += 1

                if time.time() - self.graph_updated>0.03: # S
                    self.gauge_widgets[0].update_value(x)
                    self.gauge_widgets[1].update_value(y)
                    self.gauge_widgets[2].update_value(z)
                    self.gauge_widgets[3].update_value(gx)
                    self.gauge_widgets[4].update_value(gy)
                    self.gauge_widgets[5].update_value(gz)
                    # Prevent connecting the last point to the first point
                    self.curve_x.setData(self.data[:, 0], self.data[:, 1])
                    self.curve_y.setData(self.data[:, 0], self.data[:, 2])
                    self.curve_z.setData(self.data[:, 0], self.data[:, 3])
                    self.curve_gx.setData(self.data[:, 0], self.data[:, 4])
                    self.curve_gy.setData(self.data[:, 0], self.data[:, 5])
                    self.curve_gz.setData(self.data[:, 0], self.data[:, 6])
                    self.graph_updated = time.time()

                if self.ptr%1000==0:
                    print(self.ptr,timestamp-self.first_time)

        elif self.sensor == HEATCAM_ID:
            s = dat[0]
            row = dat[1]
            rowfloats = np.frombuffer(dat[2:-4], dtype=np.float32)
            self.temperature_matrix[row,:] = rowfloats
            if row==23:
                self.spline = RectBivariateSpline(self.hy, self.hx, self.temperature_matrix)
                self.smoothed_matrix = self.spline(self.new_y, self.new_x)
                self.heatdata.setImage(self.smoothed_matrix)

                if self.bg is not None:
                    self.bgsize[...,2] = self.temperature_matrix-30
                    self.barw.removeItem(self.bg)
                    self.bg = gl.GLBarGraphItem(self.bgpos, self.bgsize)
                    self.bg.translate(-12, -16, 0)
                    self.barw.addItem(self.bg)

            #print(dat[0], dat[1], len(dat), rowfloats)#, self.temperature_matrix)


        else:
            #dat, self.addr = self.sock.recvfrom(5000)  # Clear buffer
            print('clear buffer')



    def setAccelRange(self,r):
        if self.addr is not None:
            self.sock.sendto(chr(10+r).encode(), (self.addr, self.CONFIGPORT))  # Set accelerometer range
        mr = [20,40,80,160]
        for a in range(3):
            self.gauge_widgets[a].set_MinValue(-1*mr[r])
            self.gauge_widgets[a].set_MaxValue(mr[r])
        self.plot.setYRange(-1*mr[r],mr[r])

    def setGyroRange(self,r):
        if self.addr is not None:
            self.sock.sendto(chr(20+r).encode(), (self.addr, self.CONFIGPORT))  # Set accelerometer range
        mr = [4,8,16,32]
        for a in range(3):
            self.gauge_widgets[a+3].set_MinValue(-1*mr[r])
            self.gauge_widgets[a+3].set_MaxValue(mr[r])
        try:
            self.gyroplot.setYRange(-1*mr[r],mr[r])
        except:
            self.p2.setYRange(-1*mr[r],mr[r])

    def setFilter(self,r):
        if self.addr is not None:
            self.sock.sendto(chr(30+r).encode(), (self.addr, self.CONFIGPORT))  # Set filter frequency

    def offsetZero(self):
        reply = QtWidgets.QMessageBox.question(self, 'Correct Gyro Offset', "Place the device flat and free from any vibrations first.\ndone?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.g_offsets=None
            self.g_avg_points=40
            self.g_avgs = np.zeros([self.g_avg_points,3])


    def startCounter(self):
        print(self.addr)
        self.stopScan()
        if self.addr is not None:
            print(self.addr, 'start..')
            self.first_time = None
            self.sock.sendto(b'\x01', (self.addr, self.CONFIGPORT))  # Send start signal
            self.ptr = 0
            if self.sensor == MPU6050_ID:
                self.data = np.full((self.NP, 7), np.nan)
            self.first_time = None
            self.timer.start(2)

    def pauseCounter(self):
        if self.addr is not None:
            self.sock.sendto(b'\x00', (self.addr, self.CONFIGPORT))  # Send pause signal
            self.timer.stop()

    def reboot(self):
        self.timer.stop()
        self.stopScan()

        self.sock.sendto(chr(100).encode(), (self.addr, self.CONFIGPORT))  # Send reboot signal
        self.addr = None
        while select.select([self.bsock],[],[],0.1)[0]:
            dat, addr = self.bsock.recvfrom(9)

        self.statusLabel.setText(f'Rebooted hardware. Restart app as well...')
        self.statusLabel.setStyleSheet('color:red;')
        self.controlsFrame.setEnabled(False);
        self.startScan()

    def startScan(self):
        for a in self.sensorList:
            self.sensorList[a].setParent(None)
        self.sensorList = {}
        self.statusLabel.setText(f'Searching...')
        self.statusLabel.setStyleSheet('color:red;')

        self.scanning = True
        self.scanButton.setIcon(QIcon(os.path.join("layouts","play.svg" if not self.scanning else "pause.svg")))
        self.btimer.start(200)

    def stopScan(self):
        self.scanning = False
        self.scanButton.setIcon(QIcon(os.path.join("layouts","play.svg" if not self.scanning else "pause.svg")))
        self.btimer.stop()

    def clearChoices(self):
        if self.scanning:
            self.stopScan()
        else:
            self.startScan()



    def setWiFi(self):
        print(self.ipEdit.text(),self.pwdEdit.text())
        if self.addr is not None:
            self.sock.sendto(chr(50).encode() + f'{self.ipEdit.text()}\n{self.pwdEdit.text()}\n'.encode(), (self.addr, self.CONFIGPORT))  # Send wifi creds


# This section is necessary for running new.py as a standalone program

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Expt(None)  # Pass None for the device in standalone mode
    window.show()
    sys.exit(app.exec_()) 