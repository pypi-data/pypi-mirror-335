import os, time
import sys, json, inspect
import tempfile,importlib
import pyqtgraph as pg
from functools import partial
from PyQt5 import QtWidgets, QtGui, QtCore
import shelve

try:
    from .utilities.syntax import PythonHighlighter
except:
    from utilities.syntax import PythonHighlighter

from eyes17.eyes import open as eyes17_open

import importlib.util  # Added import for importlib
from serial.tools import list_ports
from .utilities.devThread import Command, DeviceThread, SCOPESTATES
import shelve

class HoverToolbar(QtWidgets.QToolBar):
    def __init__(self, text, hideFunc, parent=None):
        super().__init__(text, parent)
        self.hideFunc = hideFunc
        self.timer = QtCore.QTimer(self)  # Create a timer
        self.timer.setSingleShot(True)  # Set the timer to be single shot
        self.timer.timeout.connect(self.hideFunc)  # Connect the timer to hideFunc

    def leaveEvent(self, event):
        self.timer.start(2000)  # Start the timer

    def enterEvent(self, event):
        self.timer.stop()  # Stop the timer if the user re-enters


class ZoomableTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFontPointSize(12)  # Set an initial font size

    def wheelEvent(self, event):
        # Check if the Ctrl key is pressed
        if event.modifiers() == QtCore.Qt.ControlModifier:
            # Zoom in or out based on the scroll direction
            delta = event.angleDelta().y()
            if delta > 0:
                self.setFontPointSize(self.fontPointSize() + 1)  # Zoom in
            else:
                self.setFontPointSize(self.fontPointSize() - 1)  # Zoom out
            event.accept()  # Accept the event
        else:
            super().wheelEvent(event)  # Call the base class implementation

    def fontPointSize(self):
        # Get the current font point size
        return self.font().pointSize()

    def setFontPointSize(self, size):
        # Set the font point size
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)



class ScriptRunner(QtWidgets.QMainWindow):
    def __init__(self, args, splash):
        super().__init__()
        self.showMaximized()
        layouts_path = os.path.join(os.path.dirname(__file__), 'layouts')
        sys.path.append(layouts_path)  # Add layouts directory to sys.path
        self.sbar = self.statusBar()

        self.createFileMenu()
        self.createPipMenu()
        self.createThemeMenu()

        self.device = None
        self.setWindowTitle("SEELab3/ExpEYES Sample Programs")
        self.setGeometry(50, 50, 1200, 600)
        self.editMode = True
        self.module = None
        self.ipyConsole = None
        self.selected_script = None
        self.recent_image = None
        self.help_file = '3.1:Oscilloscope.html'
        self.help_server = None
        self.spreadsheet_dock = None
        self.child_toolbar = None

        self.first_time = True
        try:
            self.shelf = shelve.open('seelab.shelf', 'c')
            try:
                self.theme = self.shelf['theme']
            except:
                self.theme = 'default2'

            try:
                self.first_time = self.shelf['first_time']
            except:
                self.shelf['first_time'] = False

            self.shelf.close()
        except:
            self.theme = 'default2'
            print('shelf did not work')

        self.shortcutActions = {}
        self.shortcuts = {"o": self.selectDevice,"s":self.add_spreadsheet, "Ctrl+P":self.takeScreenshot}
        for a in self.shortcuts:
            shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(a), self)
            shortcut.activated.connect(self.shortcuts[a])
            self.shortcutActions[a] = shortcut

        # Create a central widget
        self.central_widget = QtWidgets.QStackedWidget(self)
        self.setCentralWidget(self.central_widget)


        # Add a button to run/edit the code
        self.run_code_button = QtWidgets.QPushButton("Run Code", self)
        self.run_code_button.setIcon(QtGui.QIcon(os.path.join("icons","play_icon.png")))  # Set play icon
        self.run_code_button.clicked.connect(self.run_code)
        
        self.sbar.addPermanentWidget(self.run_code_button)


        self.help_button = QtWidgets.QPushButton("Show Help", self)
        self.help_button.setIcon(QtGui.QIcon(os.path.join("icons","help.svg")))  # Set play icon
        self.help_button.clicked.connect(self.show_help)
        self.sbar.addPermanentWidget(self.help_button)


        #self.toolbar.addWidget(self.run_code_button)

        self.createExperimentsToolbar()

        # Store the currently loaded script
        self.current_script = None

        # Add the QTextEdit to the central widget
        self.source_code_edit = QtWidgets.QTextEdit(self)
        self.central_widget.addWidget(self.source_code_edit)
        self.central_widget.setCurrentWidget(self.source_code_edit)  # Show the source code editor


        # Load available scripts
        #self.create_experiments_menu()


        # Remove tmp.py
        try:
            tmp_file_path = os.path.join(os.path.dirname(__file__), 'tmp.py')
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
        except:
            pass
        self.setTheme(self.theme)

        self.selected_script = args.script if args.script else 'oscilloscope'
        self.scope_thread = DeviceThread(self.device)
        self.scope_thread.start()

        splash.showMessage(f"<h2><font color='Red'>Initializing communications...</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)
        self.initializeCommunications()


        if self.first_time:
            for a in range(5,20):
                splash.showMessage(f"<h2><font color='Green'>Welcome to SEELab!...{'.'*a}</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)
                splash.pbar.setValue(a)
                QtCore.QCoreApplication.processEvents()
                time.sleep(0.2)
            #self.showCredits()

        #Auto-Detector
        self.deviceSelector = self.portSelectionDialog()
        self.shortlist=[]

        self.startTime = time.time()
        self.timer = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.locateDevices)
        self.timer.start(500)
        
        splash.finish(self)
        
        # Ensure window gets focus after splash screen is dismissed
        self.activateWindow()
        self.raise_()
        
        # Additional focus fix - slight delay to ensure OS processes the window activation
        QtCore.QTimer.singleShot(100, self.forceFocus)

    def forceFocus(self):
        """Force the window to take focus after a slight delay"""
        self.activateWindow()
        self.raise_()
        # On some systems, this additional step helps
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)

    def selectDevice(self):
        self.locateDevices(True)        
        if self.deviceSelector.exec_():
            if self.device.H.portname != self.deviceSelector.getSelection():
                if self.current_script:
                    try:
                        self.current_script.timer.stop()  # Stop the timer loop of current widget
                    except:
                        pass
                self.current_script.close()  # Close the current script if it's open

                self.initializeCommunications(port = self.deviceSelector.getSelection())
            else:
                self.showStatus('Device already connected',False)

    def initializeCommunications(self,port=False):
        if self.device:
            self.scope_thread.updateDevice(None)
            self.device.H.disconnect()
            self.device.H.portname=None
        if port:
            self.device = eyes17_open(port = port)
        else:
            self.device = eyes17_open()
        
        if self.device.connected:
            self.showStatus('Device Connected',False)
            self.scope_thread.updateDevice(self.device)

            #self.device.H.fd.set_low_latency_mode(True)
        if self.current_script is None and self.ipyConsole:
            self.ipyConsole.pushVariables({'p':self.device})
        else:
            self.load_script(self.selected_script if self.selected_script is not None else 'oscilloscope')


    def locateDevices(self, force = False):
        openports = {a.device:a.description for a in  list_ports.comports() if ('ttyACM' in a.device or 'cu' in a.device or 'ttyUSB' in a.device or 'COM' in a.device) and ('Bluetooth' not in a.description)}
        if self.device.H.portname not in openports:
            if self.device.H.connected:
                self.setWindowTitle('Error : Device Disconnected')
                QtWidgets.QMessageBox.warning(self, 'Connection Error',
                                                'Device Disconnected. Please check the connections')

            self.scope_thread.updateDevice(None)
            self.device.H.disconnect()
            self.device.H.portname = None
            self.device.H.connected = False

        if self.device and not force:
            if self.device.H.connected:
                return


        L = {a:[openports[a],True] for a in openports}
        if self.device.H.portname in openports:
            L[self.device.H.portname] = [openports[self.device.H.portname],False]
            #openports.remove(self.device.H.portname)
        total = len(L)
        menuChanged = False
        if L != self.shortlist:
            menuChanged = True
            newdevavailable = False
            newdev = None
            newdevname = None
            for a in L:
                if L[a][1]:
                    newdevavailable = True
                    newdev = a
                    newdevname = L[a][0]
                    break
            self.deviceSelector.setList(L,self.device.H)
            if newdevavailable:
                reply = QtWidgets.QMessageBox.question(self, 'Connection', f'Device {newdev} at {newdevname} Available. Connect?', QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.initializeCommunications()

            #update the shortlist
            self.shortlist=L


    class portSelectionDialog(QtWidgets.QDialog):
        def __init__(self,parent=None):
            super(ScriptRunner.portSelectionDialog, self).__init__(parent)
            self.button_layout = QtWidgets.QVBoxLayout()
            self.setLayout(self.button_layout)
            self.btns=[]
            self.doneButton = QtWidgets.QPushButton("Done")
            self.button_layout.addWidget(self.doneButton)
            self.doneButton.clicked.connect(self.finished)


        def setList(self,L,handler):
            for a in self.btns:
                a.setParent(None)
                del a
            self.btns=[]

            self.button_group = QtWidgets.QButtonGroup()

            #moods[0].setChecked(True)
            pos=0
            for i in L:
                # Add each radio button to the button layout
                btn = QtWidgets.QRadioButton(f'{i}||{L[i][0]}')
                self.button_layout.addWidget(btn)
                self.btns.append(btn)
                if handler:
                    if handler.connected:
                        if handler.portname == i:
                            btn.setStyleSheet("color:green;")
                if not L[i][1]: #Port in use
                    btn.setEnabled(False)
                    btn.setChecked(True)

                self.button_group.addButton(btn, pos)
                pos+=1

            # Set the layout of the group box to the button layout

        #Print out the ID & text of the checked radio button
        def finished(self):
            if self.button_group.checkedId()!= -1:
                self.done(QtWidgets.QDialog.Accepted)
        def getSelection(self):
            if self.button_group.checkedId()!= -1:
                return self.button_group.checkedButton().text().split('||')[0]
            else:
                return False

    def checkConnectionStatus(self,dialog=False):
        if self.device.connected:return True
        else:
            if dialog: QtWidgets.QMessageBox.warning(self, 'Connection Error', 'Device not connected. Please connect an MCA to the USB port')
            return False

    def showStatus(self,msg,error=None):
        if error: self.sbar.setStyleSheet("color:#F77")
        else: self.sbar.setStyleSheet("color:#000000")
        self.sbar.showMessage(msg)

    def createExperimentsToolbar(self):
        BW = 20
        BH = 20
        H = 30

        # Create a toolbar for script selection
        self.toolbar = QtWidgets.QToolBar("ExptMenus")
        self.toolbar.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolbar)

        # Add square icon buttons to the toolbar
        with open(os.path.join(os.path.dirname(__file__),'experiments.json'), 'r') as file:
            data = json.load(file)  # Load the JSON data
        #print(data)
        for name in data:
            #button = HoverOpenBtn(f"{name}",partial(self.updateExperimentsSubmenuToolbar,data[name]),self)
            button = QtWidgets.QToolButton(self)
            button.setText(f"{name}")
            button.setStyleSheet("QToolButton { padding-right: 10px; }; QToolButton::menu-indicator { max-width: 5px; }")
            button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
            #Automatically show the menu when hovering over the button  
            button.setPopupMode(QtWidgets.QToolButton.InstantPopup)   


            self.updateExperimentsSubmenu(button,data[name])
            button.setIcon(QtGui.QIcon(os.path.join("icons", name+'.png')))  # Set icon
            button.setFixedHeight(H)  # Set fixed height
            
            #button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)  # Allow width to expand
            button.setIconSize(QtCore.QSize(BW, BH))
            self.toolbar.addWidget(button)  # Add button to the toolbar

        self.insertToolBarBreak(self.toolbar)
        self.addToolBarBreak()
        self.coding_toolbar = HoverToolbar("CodingMenu",self.hideExperimentsSubmenuToolbar)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.coding_toolbar)
        self.coding_toolbar.hide()


        # Create a button to open the IPython console with a Python logo icon
        self.console_button = QtWidgets.QPushButton("Write Code!",self)
        self.console_button.setIcon(QtGui.QIcon(os.path.join("icons","python_logo.png")))  # Set Python logo icon
        self.console_button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)  # Allow width to expand
        self.console_button.setFixedHeight(H)  # Set fixed height
        self.console_button.setIconSize(QtCore.QSize(BW, BH))
        self.console_button.clicked.connect(self.add_ipython_console)


        # Create a button to open the IPython console with a Python logo icon
        self.sheet_button = QtWidgets.QPushButton("Spreadsheet",self)
        self.sheet_button.setIcon(QtGui.QIcon(os.path.join("icons","spreadsheet.png")))
        self.sheet_button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)  # Allow width to expand
        self.sheet_button.setFixedHeight(H)  # Set fixed height
        self.sheet_button.setIconSize(QtCore.QSize(BW, BH))
        self.sheet_button.clicked.connect(self.add_spreadsheet)


        self.toolbar.addSeparator()
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.console_button)
        self.toolbar.addWidget(self.sheet_button)
        self.toolbar.adjustSize()



    def add_spreadsheet(self, columns=None):
        from .utilities import spreadsheetWidget

        if self.spreadsheet_dock is not None:
            self.spreadsheet_dock.close()
            self.spreadsheet_dock = None
            return

        self.spreadsheet_dock = QtWidgets.QDockWidget("Spreadsheet",self)
        self.spreadsheet_dock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.spreadsheet_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable|QtWidgets.QDockWidget.DockWidgetClosable|QtWidgets.QDockWidget.DockWidgetFloatable)  # Enable move button
        self.spreadsheet_dock.setMinimumWidth(340)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,self.spreadsheet_dock)
        self.spreadsheet_widget = spreadsheetWidget.MySpreadsheet(self)
        if columns:
            self.spreadsheet_widget.tableWidget.setHorizontalHeaderLabels(columns)
        self.spreadsheet_dock.setWidget(self.spreadsheet_widget)


    def plot_data(self):
        #get the data from the table
        data = self.spreadsheet_widget.toPlainText()
        #Plot with pyqtgraph in a popup window
        self.plot_widget = pg.PlotWidget(self)
        self.plot_widget.plot(data)
        self.plot_dock = QtWidgets.QDockWidget("Plot",self)
        self.plot_dock.setWidget(self.plot_widget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,self.plot_dock)

    
    def updateExperimentsSubmenu(self,btn, items):
        experiment_menu = QtWidgets.QMenu(self)
        for a in items:

            mod = a['module_name']
            if mod == 'separator':
                experiment_menu.addSeparator()
                continue

            action = experiment_menu.addAction(a['title'])
            modname = mod

            if mod.startswith('extra:'): # Device configuration
                opt = mod.split(':')[1]
                if opt == 'simulator':
                    action.triggered.connect(self.launchsimulator)
                elif opt == 'simulator_samples':
                    action.triggered.connect(self.launchsimulatorsamples)
                elif opt == 'ProgrammersManual':
                    action.triggered.connect(self.launchProgrammersManual)
                elif opt == 'device_selector':
                    action.triggered.connect(self.selectDevice)
                elif opt == 'credits':
                    action.triggered.connect(self.showCredits)
                elif opt == 'screenshot':
                    action.triggered.connect(self.takeScreenshot)
                elif opt == 'dark_mode':
                    action.setCheckable(True)
                    action.setChecked(self.theme == 'material')
                    action.triggered.connect(self.setDarkMode)

            else:
                if mod.startswith('scope:'): #OldOscilloscope  
                    mod = 'scope'
                elif mod.startswith('oscilloscope:'): #SimpleOscilloscope
                    mod = 'oscilloscope'

                if 'http' in a['helpname']:
                    helpname = a['helpname']
                else:
                    helpname = a['helpname']+':'+a['title']

                action.triggered.connect(partial(self.load_script,mod,a['title'], helpname,calc=a.get('spreadsheet',False),image=a.get('image',None)))

            if ':' in mod:
                opt = mod.split(':')[1]
            else:
                opt = mod

            if os.path.exists(os.path.join(os.path.dirname('__file__'),"icons",modname.replace(':','_')+".png")):
                action.setIcon(QtGui.QIcon(os.path.join(os.path.dirname('__file__'),"icons",modname.replace(':','_')+".png")))  # Set icon
                #action.setIconSize(QtCore.QSize(20, 20))
            elif os.path.exists(os.path.join(os.path.dirname('__file__'),"icons",mod+".png")):
                action.setIcon(QtGui.QIcon(os.path.join(os.path.dirname('__file__'),"icons",mod+".png")))  # Set icon
                #action.setIconSize(QtCore.QSize(20, 20))
            elif os.path.exists(os.path.join(os.path.dirname('__file__'),"icons",opt+".png")):
                action.setIcon(QtGui.QIcon(os.path.join(os.path.dirname('__file__'),"icons",opt+".png")))  # Set icon
                #action.setIconSize(QtCore.QSize(20, 20))


            experiment_menu.addAction(action)  # Add button to the toolbar

        btn.setMenu(experiment_menu)
        #btn.setPopupMode(QtWidgets.QPushButton.InstantPopup)




    def createWebserver(self):
        if self.help_server is not None:
            return

        port = 8001
        server_address = ('0.0.0.0', port)
        self.sbar.showMessage('Starting help web server',2000)
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        import threading
        #Start the server

        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory='online', **kwargs)

        # Set up the HTTP server

        httpd = HTTPServer(server_address, Handler)

        # Create a thread to run the server
        self.help_server = threading.Thread(target=httpd.serve_forever)
        self.help_server.daemon = True  # Allows the thread to exit when the main program does
        self.help_server.start()            

    def show_help(self):
        import webbrowser
        if self.help_file is not None and 'http' in self.help_file:
            webbrowser.open(self.help_file)
            return
        self.createWebserver()

        if self.help_file is None:
            self.sbar.showMessage('No Help Specified',2000)
        else:
            self.sbar.showMessage('Load Help>>  '+self.help_file,2000)
            url = 'helpFiles/en/'+self.help_file.split(':')[0]+'.html'
            webbrowser.open(f"http://localhost:8001/"+url)  # Adjust the URL as needed

    def launchsimulator(self):
        import webbrowser
        self.createWebserver()
        self.sbar.showMessage('Launching Simulator...',2000)
        webbrowser.open(f"http://localhost:8001/site/circuitjs.html")  # Adjust the URL as needed

    def launchsimulatorsamples(self):
        import webbrowser
        self.createWebserver()
        self.sbar.showMessage('View Simulator samples...',2000)
        webbrowser.open(f"http://localhost:8001/site/circuits.html")  # Adjust the URL as needed

    def launchProgrammersManual(self):
        import webbrowser
        self.createWebserver()
        self.sbar.showMessage('Opening Programmers Manual...',2000)
        webbrowser.open(f"https://eyes17lib.readthedocs.io/en/latest/")  # Adjust the URL as needed

    def showCredits(self):
        self.sbar.showMessage('Credits...', 2000)
        self.credits_dialog = QtWidgets.QDialog(self)
        self.credits_dialog.setWindowTitle('Credits')
        self.credits_dialog.setMinimumSize(600, 400)

        # Add a QTextBrowser to display random content
        self.credits_text_browser = QtWidgets.QTextBrowser(self.credits_dialog)
        self.credits_text_browser.setHtml("""
            <h2>Credits</h2>
            <ul>
                <li><strong>hardware & Firmware</strong> : Jithin B P  (<a href="https://csparkresearch.in/expeyes-dev">https://csparkresearch.in/expeyes-dev</a>)</li>
                <li><strong>Software</strong> : Jithin B P, Georges Khaznadar, Ajith Kumar B P</li>
                <li><strong>Translations</strong>
                    <ul>
                        <li>Malayalam : Amal M., Ajith Kumar B P</li>
                        <li>French : Georges Khaznadar</li>
                        <li>Spanish : Bibiana Boccolini</li>
                    </ul>
                </li>
                <li><strong>Documentation</strong> : Georges Khaznadar, Ajith Kumar B P, V V V Satyanarayana</li>
            </ul>
        """)        
        # Set layout for the dialog
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.credits_text_browser)
        self.credits_dialog.setLayout(layout)

        # Connect mouse press event to close the dialog
        self.credits_dialog.mousePressEvent = self.close_dialog

        self.credits_dialog.show()

    def takeScreenshot(self):
        """Save the current content of the editor to a script file."""
        self.sbar.showMessage('Taking Screenshot...', 2000)
        
        # Create a QFileDialog
        dialog = QtWidgets.QFileDialog(self)
        dialog.setDirectory(os.path.expanduser("~/"))  # Set the initial directory to the user's home directory
        dialog.setWindowTitle("Save Screenshot")
        dialog.setNameFilter("Images (*.png);;All Files (*)")
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)

        # Show the dialog and get the selected file name
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_name = dialog.selectedFiles()[0]  # Get the selected file name
            self.central_widget.grab().save(file_name)  # Save the screenshot


    def close_dialog(self, event):
        print("close_dialog", event)
        self.credits_dialog.close()


    def hideExperimentsSubmenuToolbar(self):
        if self.child_toolbar:#remove the toolbar
            self.removeToolBar(self.child_toolbar)

    def createFileMenu(self):
        self.file_button = QtWidgets.QPushButton("Files", self)
        self.sbar.addPermanentWidget(self.file_button)

        self.file_menu = QtWidgets.QMenu()
        self.open_action = QtWidgets.QAction("Open Script", self)
        self.open_action.triggered.connect(self.open_script)
        self.file_menu.addAction(self.open_action)

        self.save_action = QtWidgets.QAction("Save Script", self)
        self.save_action.triggered.connect(self.save_script)
        self.file_menu.addAction(self.save_action)

        self.file_button.setMenu(self.file_menu)


    def createThemeMenu(self):
        theme_button = QtWidgets.QPushButton("Themes", self)
        self.sbar.addPermanentWidget(theme_button)

        self.theme_menu = QtWidgets.QMenu()
        theme_files = [f for f in os.listdir('themes') if f.endswith('.qss')]
        for theme_file in theme_files:
            theme_action = QtWidgets.QAction(theme_file, self)
            theme_action.triggered.connect(partial(self.setTheme,theme_file[:-4]))
            self.theme_menu.addAction(theme_action)

        theme_button.setMenu(self.theme_menu)

    def createPipMenu(self):
        pip_button = QtWidgets.QPushButton("Install Packages", self)
        self.sbar.addPermanentWidget(pip_button)

        self.pip_menu = QtWidgets.QMenu()
        for a in [("PyQt5 GUI",'pyqt5'),('NumPy','numpy'),('SciPy','scipy'),('pyqtgraph','pyqtgraph'),('pyserial','pyserial'),('matplotlib','matplotlib'),('qtconsole','qtconsole'),('webserver','webserver'),('All of these','numpy scipy pyqtgraph pyqt5 pyserial matplotlib qtconsole webserver')]:
            action = QtWidgets.QAction(a[0], self)
            action.triggered.connect(partial(self.showPipInstaller,a[1] ))
            self.pip_menu.addAction(action)

        pip_button.setMenu(self.pip_menu)

    def showPipInstaller(self, name):
        from .utilities.pipinstaller import PipInstallDialog
        self.pipdialog = PipInstallDialog(name, self)
        self.pipdialog.show()

    def open_script(self):
        """Open a script file and load its content into the editor."""
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Script File", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r',encoding='utf-8') as file:
                self.source_code_edit.setPlainText(file.read())

    def save_script(self):
        """Save the current content of the editor to a script file."""
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Script File", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w',encoding='utf-8') as file:
                file.write(self.source_code_edit.toPlainText())


    def create_experiments_menu(self):
        """Load Python scripts from the current directory."""
        script_dir = os.path.dirname(__file__)
        scripts = [f[:-3] for f in os.listdir(script_dir) if f.endswith('.py') and f not in ['script_runner.py', 'tmp.py', '__main__.py','__init__.py','utils.py','mycode.py','ipy.py']]

        self.script_menu = self.menuBar().addMenu("Launch Apps")
        for a in scripts:
            action = QtWidgets.QAction(a, self)
            action.triggered.connect(partial(self.load_script,a))
            self.script_menu.addAction(action)



    def load_available_baremetal_scripts(self):
        """Load Python scripts from the current directory."""
        script_dir = os.path.join(os.path.dirname(__file__),'examples')
        scripts = [f[:-3] for f in sorted(os.listdir(script_dir)) if f.endswith('.py') and f not in ['__init__.py']]
        self.simple_script_selector.addItems(scripts)



    def load_simple_script(self, opt=None):
        with open(os.path.join( os.path.dirname(__file__), 'examples', opt+'.py'), 'r') as file:
            self.text_editor.setText(file.read())

    def execute_simple_script(self):
        source_code = self.text_editor.toPlainText()
        source_code = '\n'.join([line for line in source_code.split('\n') if 'import eyes17' not in line])
        source_code = '\n'.join([line for line in source_code.split('\n') if 'open()' not in line])

        temp_file_path = os.path.join(os.path.dirname(__file__), 'mycode.py')
        with open(temp_file_path, 'w',encoding='utf-8') as temp_file:
            temp_file.write(source_code)  # Save the edited code

        #self.ipyConsole.execute(source_code)
        self.ipyConsole.execute('%run -i mycode.py')


    def run_code(self):
        """Replace the source code editor with the Expt class of the selected script."""
        if self.editMode:
            if self.selected_script:
                self.stop_current_script()

                self.editMode = False

                # Save the edited source code to a temporary file
                temp_file_path = os.path.join(os.path.dirname(__file__), 'tmp.py')
                with open(temp_file_path, 'w',encoding='utf-8') as temp_file:
                    temp_file.write(self.source_code_edit.toPlainText())  # Save the edited code
                # Remove tmp* from the __pycache__ directory before import
                pycache_dir = os.path.join(os.path.dirname(__file__), '__pycache__')
                for file in os.listdir(pycache_dir):
                    if file.startswith('tmp'):
                        os.remove(os.path.join(pycache_dir, file))
                importlib.invalidate_caches()
                if self.module:
                    self.module = importlib.reload(self.module)
                if __name__ == '__main__':
                    self.module = importlib.import_module('tmp')  # Import the temporary module with explicit import
                else:
                    self.module = importlib.import_module('.tmp',package='seelab_examples')  

                
                arg_spec = inspect.getfullargspec(self.module.Expt.__init__)
                if arg_spec.varkw: #kwargs specified in the Expt class init
                    self.scope_thread.paused = False
                    kwargs = {'scope_thread':self.scope_thread,'ipy':self.prefilled_ipy_console}
                    if self.replacement_image is not None:
                        kwargs['image'] = self.replacement_image
                    self.current_script = self.module.Expt(self.device, **kwargs)  # Create an instance of the Expt class
                else:
                    self.current_script = self.module.Expt(self.device)  # Create an instance of the Expt class

                if hasattr(self.current_script,'set_status_function'):
                    self.current_script.set_status_function(self.sbar.showMessage)

                self.central_widget.addWidget(self.current_script)  # Add the new script's window to the central widget
                self.central_widget.setCurrentWidget(self.current_script)  # Show the new script's window

                # Change button to "Edit Code" with edit icon
                self.run_code_button.setText("Edit Code")
                self.run_code_button.setIcon(QtGui.QIcon(os.path.join("icons","edit_icon.png")))  # Set edit icon

        else:
            self.load_script('tmp')
            self.setEditMode()


    def load_script(self, opt, title=None, helpname=None,calc=False, **kwargs):
        """Load and display the selected script's source code."""
        self.coding_toolbar.hide()
        self.selected_script = opt
        if helpname is not None:
            self.help_file = helpname
        self.replacement_image = kwargs.get('image',None)
        if title is None:
            title = opt
        self.setWindowTitle(f"SEELab3/ExpEYES Sample : {title}")

        if opt == 'scope':
            self.setTheme("style")
        else:
            self.setTheme(self.theme)

        script_path = os.path.join(os.path.dirname(__file__), f"{self.selected_script}.py")
        self.setEditMode()


        with open(script_path, 'r',encoding='utf-8') as file:
            source_code = file.read()

        self.central_widget.setCurrentWidget(self.source_code_edit)  # Show the source code editor

        self.source_code_edit.setPlainText(source_code)
        self.source_code_edit.setReadOnly(False)  # Allow editing
        self.highlight = PythonHighlighter(self.source_code_edit.document())  # Syntax highlighting
        if self.selected_script != 'tmp':
            self.run_code()

        if calc:
            if self.spreadsheet_dock is None:
                self.add_spreadsheet(calc['columns'])
        elif self.spreadsheet_dock is not None:
            self.spreadsheet_dock.close()
            self.spreadsheet_dock = None
            return

    def stop_current_script(self):
        self.scope_thread.disconnectSignals()
        self.scope_thread.paused = True
        if self.current_script:
            if hasattr(self.current_script,'set_scope_thread'):
                self.current_script.set_scope_thread(None)
            try:
                self.current_script.timer.stop()  # Stop the timer loop of current widget
            except:
                pass
            self.current_script.close()  # Close the current script if it's open


    def prefilled_ipy_console(self, title, vars):
        self.add_ipython_console(title, True, **vars)

    def add_ipython_console(self, title=None, standalone = False,**kwargs):
        """Create and add an IPython console widget to the main window."""
        from qtconsole.rich_jupyter_widget import RichJupyterWidget
        from qtconsole.inprocess import QtInProcessKernelManager

        class myConsole(RichJupyterWidget):
            def __init__(self,customBanner=None):
                """Start a kernel, connect to it, and create a RichJupyterWidget to use it
                """
                super(myConsole, self).__init__()
                if customBanner is not None:
                    self.banner=customBanner
                self.kernel_manager = QtInProcessKernelManager(kernel_name='python3')

                self.kernel_manager.start_kernel()
                self.kernel = self.kernel_manager.kernel

                self.kernel_manager.kernel.gui = 'qt'
                self.font_size = 8

                self.kernel_client = self.kernel_manager.client()
                self.kernel_client.start_channels()

                def stop():
                    self.kernel_client.stop_channels()
                    self.kernel_manager.shutdown_kernel()
                    #guisupport.get_app_qt().exit()

                self.exit_requested.connect(stop)

            def pushVariables(self,variableDict):
                """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
                self.kernel.shell.push(variableDict)
            def clearTerminal(self):
                """ Clears the terminal """
                self._control.clear()    

            def printText(self,text):
                """ Prints some plain text to the console """
                self._append_plain_text(text)

            def executeCommand(self,command,hidden=False):
                """ Execute a command in the frame of the console widget """
                self._execute(command,hidden)

        if not standalone:            
            self.setTheme("default2")
            if self.current_script:
                try:
                    self.current_script.timer.stop()  # Stop the timer loop of current widget
                except:
                    pass
                self.current_script.close()  # Close the current script if it's open
                self.current_script = None

        self.coding_toolbar.show()

        try:
            #--------instantiate the iPython class-------
            if self.ipyConsole is None or standalone:
                msg = '''Access hardware using the Instance 'p'.  e.g.  p.get_voltage('A2')'''

                if standalone:
                    msg = kwargs.get('msg','')
                self.ipyConsole = myConsole(f"### Interactive Console ###\n{msg}\n\n")
                self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

                self.splitter.addWidget(self.ipyConsole)
                if not standalone:
                    self.text_editor = ZoomableTextEdit()
                    try:
                        self.text_editor.setFont(QtGui.QFont("Consolas", 12))
                    except: #better to ask for forgiveness than permission
                        pass    
                    self.text_editor_highlighter = PythonHighlighter(self.text_editor.document())  # Syntax highlighting
                    # Add default code into the text editor
                    self.text_editor.setText("from eyes17 import eyes\np=eyes.open()\n\n#Your Code here\n\n")
                    
                    msg = kwargs.get('msg','')
                    self.splitter.addWidget(self.text_editor)
                    self.splitter.setSizes([4,2])

                cmdDict = {}
                #cmdDict = {"analytics":self.analytics}
                if self.device and not standalone:
                    cmdDict["p"]=self.device
                    import matplotlib.pyplot as plt
                    cmdDict["plt"]=plt
                cmdDict['me'] = self.ipyConsole
                if kwargs:
                    cmdDict.update(kwargs)
                self.ipyConsole.pushVariables(cmdDict)
                self.console_enabled=True
                self.createPythonCodeOptionsMenu()

                # Create a toolbar for script selection
                #self.toolbar = self.addToolBar("Simple Scripts")
                self.simple_script_selector = QtWidgets.QComboBox(self)

                self.coding_toolbar.addWidget(self.simple_script_selector)
                self.load_available_baremetal_scripts()
                self.simple_script_selector.currentTextChanged.connect(self.load_simple_script)

                self.execute_button = QtWidgets.QPushButton()
                self.execute_button.setText("Run Script")
                self.execute_button.setIcon(QtGui.QIcon(os.path.join("icons","play_icon.png")))
                self.execute_button.clicked.connect(self.execute_simple_script)
                self.coding_toolbar.addWidget(self.execute_button)
                
                # Add a spacer to push the programming manual button to the right
                spacer = QtWidgets.QWidget()
                spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                self.coding_toolbar.addWidget(spacer)
                
                # Add a button for the Programming Manual reference
                self.manual_button = QtWidgets.QPushButton("Programming Reference")
                self.manual_button.setIcon(QtGui.QIcon(os.path.join("icons","ProgrammersManual.png"))) # Assuming icon exists
                self.manual_button.clicked.connect(self.launchProgrammersManual)
                self.coding_toolbar.addWidget(self.manual_button)
                
            else:
                self.ipyConsole.pushVariables({'p':self.device})

            if standalone:
                self.ipyDialog = QtWidgets.QDialog()
                self.ipyDialog.setWindowTitle(title)
                self.ipyDialog.setWindowIcon(QtGui.QIcon(os.path.join("icons","python_logo.png")))
                self.ipyDialog.setGeometry(100,100,800,600)
                self.ipyDialog.setLayout(QtWidgets.QVBoxLayout())
                self.ipyDialog.layout().addWidget(self.splitter)
                self.ipyDialog.show()
            else:
                self.central_widget.addWidget(self.splitter)
                self.central_widget.setCurrentWidget(self.splitter)  # Show the source code editor

        except Exception as e:
            print ("failed to launch iPython. Is it installed?", e)
            self.close()
            
    def createPythonCodeOptionsMenu(self):
        # Instead of creating a menu in the menubar, create a button with dropdown in the coding toolbar
        self.code_options_button = QtWidgets.QToolButton(self)
        self.code_options_button.setText("")
        self.code_options_button.setIcon(QtGui.QIcon(os.path.join("icons","python_logo.png")))
        self.code_options_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.code_options_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        
        # Create a menu for the button
        options_menu = QtWidgets.QMenu(self)
        
        # Add actions to the menu
        inline_plots_action = options_menu.addAction("Inline Plots")
        inline_plots_action.triggered.connect(partial(self.ipyConsole.execute,'%matplotlib inline'))
        
        import_numpy_action = options_menu.addAction("Import Numpy")
        import_numpy_action.triggered.connect(partial(self.ipyConsole.execute,'import numpy as np'))
        
        # Set the menu to the button
        self.code_options_button.setMenu(options_menu)
        
        # Add the button to the coding toolbar after the simple_script_selector but before execute_button
        self.coding_toolbar.addWidget(self.code_options_button)

    def setEditMode(self):
        self.run_code_button.setText("Run Code")
        self.run_code_button.setIcon(QtGui.QIcon(os.path.join("icons","play_icon.png")))  # Set play icon
        self.editMode = True
        self.stop_current_script()

    ##############################
    def setDarkMode(self, state):
        self.setTheme('material' if state else 'default2')
        if self.current_script is not None:
            if hasattr(self.current_script,'plot'):
                if self.current_script.plot.__class__.__name__ == 'PlotWidget':
                    if state:
                        self.current_script.plot.setBackground('k')
                    else:
                        self.current_script.plot.setBackground('w')
                elif self.current_script.plot.__class__.__name__ == 'PlotItem':
                    if state:
                        self.current_script.plot.mywin.setBackground('k')
                    else:
                        self.current_script.plot.mywin.setBackground('w') 


    def setTheme(self, theme):
        self.theme = theme
        self.setStyleSheet("")
        self.setStyleSheet(open(os.path.join(os.path.dirname(__file__),'themes', theme + ".qss"), "r").read())
        try:
            self.shelf = shelve.open('seelab.shelf', 'c')
            self.shelf['theme'] = theme
            self.shelf.close()
        except Exception as e:
            print('saving to shelf failed',e)

def load_experiments(file_path):
    """Load experiments from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def showSplash():
    # Create and display the splash screen
    splash = os.path.join(os.path.dirname(__file__),'interactive/splash.jpg')
    splash_pix = QtGui.QPixmap(splash)
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())

    progressBar = QtWidgets.QProgressBar(splash)
    progressBar.setStyleSheet('''

    QProgressBar {
        border: 2px solid grey;
        border-radius: 5px;	
        border: 2px solid grey;
        border-radius: 5px;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: #012748;
        width: 10px;
        margin: 0.5px;
    }
    ''')
    progressBar.setMaximum(10)
    progressBar.setGeometry(0, splash_pix.height() - 50, splash_pix.width(), 20)
    progressBar.setRange(0,8)

    splash.show()
    splash.pbar = progressBar
    splash.show()
    return splash


if __name__ == "__main__":
    import argparse
    import os, sys
    # Add the parent directory to sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    __package__ = 'seelab_examples'

    # Load experiments from experiments.json
    experiments_file = os.path.join(os.path.dirname(__file__), 'experiments.json')
    experiments = load_experiments(experiments_file)

    # Create a list of choices for the argument parser
    choices = []
    for category, items in experiments.items():
        for item in items:
            if item['module_name']:  # Ensure module_name is not empty
                choices.append((item['module_name'], item['title']))

    parser = argparse.ArgumentParser(description='Run a specific script from seelab_examples.')

    # Add a custom help message to show the table of names and titles
    parser.add_argument('--list', action='store_true', help='Show available experiments')

    # Now add the script argument after checking for --list
    parser.add_argument('script', nargs='?', choices=[name for name, title in choices], help='The name of the script to run')

    # Parse the arguments
    args = parser.parse_args()

    if args.list:
        print("Available Experiments:")
        print(f"{'Module Name':<30} {'Title'}")
        print("-" * 50)
        for name, title in choices:
            if title:
                print(f"{name:<30} {title}")
        sys.exit()

    app = QtWidgets.QApplication(sys.argv)




    window = ScriptRunner(args)
    window.show()
    sys.exit(app.exec_())


