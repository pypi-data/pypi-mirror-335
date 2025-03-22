import os
import socket
import sys
import time
import webbrowser
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtGui import QPixmap, QFont, QIcon

class Expt(QtWidgets.QMainWindow):
    logThis = QtCore.pyqtSignal(str)
    showStatusSignal = QtCore.pyqtSignal(str, bool)
    serverSignal = QtCore.pyqtSignal(str)

    def __init__(self, device):
        super().__init__()
        self.device = device  # Device handler passed to the Expt class.
        self.serverActive = False
        self.external = None
        
        # Set window properties
        self.setWindowTitle("Visual Programming Environment")
        self.resize(800, 600)
        
        # Create a central widget
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        
        # Create a main layout
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create a header with logo and title
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add logo if available
        logo_path = os.path.join(os.path.dirname(__file__), "icons", "visual_coding.png")
        if os.path.exists(logo_path):
            logo_label = QtWidgets.QLabel()
            logo_pixmap = QPixmap(logo_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            header_layout.addWidget(logo_label)
        
        # Add title
        title_label = QtWidgets.QLabel("Visual Programming Environment (Under active development)...")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        
        # Status indicator for server
        self.server_status = QtWidgets.QLabel()
        self.server_status.setStyleSheet("QLabel { color: gray; }")
        header_layout.addWidget(self.server_status)
        
        main_layout.addWidget(header_widget)
        
        # Add description
        description = QtWidgets.QLabel(
            "Create code visually by dragging and connecting blocks. "
            "Perfect for beginners and rapid prototyping with ExpEYES hardware."
        )
        description.setWordWrap(True)
        description.setStyleSheet("QLabel { color: #555; font-size: 14px; }")
        main_layout.addWidget(description)
        
        # Create a card layout for buttons and controls
        card_widget = QtWidgets.QWidget()
        card_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
            QPushButton:pressed {
                background-color: #004e8c;
            }
        """)
        card_layout = QtWidgets.QVBoxLayout(card_widget)
        card_layout.setSpacing(15)
        
        # IP Address display
        self.ip_display = QtWidgets.QLabel("Server: Not started")
        self.ip_display.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        card_layout.addWidget(self.ip_display)
        
        # Connection status
        self.connection_status = QtWidgets.QLabel()
        self.update_connection_status()
        card_layout.addWidget(self.connection_status)
        
        # Buttons area
        buttons_widget = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main button - make prominent and fluid width
        self.browser_button = QtWidgets.QPushButton("Open Visual Editor")
        self.browser_button.setIcon(QIcon(os.path.join("icons", "browser.png")))
        self.browser_button.clicked.connect(self.openBrowser)
        # No specific width constraints on the main button
        buttons_layout.addWidget(self.browser_button)
        
        # Spacer to push the pip button to the right
        buttons_layout.addStretch(1)
        
        # Create a less prominent utility button
        self.pip_button = QtWidgets.QPushButton("Install Packages")
        self.pip_button.setIcon(QIcon(os.path.join("icons", "package.png")))
        self.pip_button.clicked.connect(self.launchPipInstaller)
        self.pip_button.setFixedWidth(180)  # Fixed width instead of max-width
        self.pip_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #505050;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: normal;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #aaa;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        buttons_layout.addWidget(self.pip_button)
        
        card_layout.addWidget(buttons_widget)
        main_layout.addWidget(card_widget)
        
        # Create a log section
        log_group = QtWidgets.QGroupBox("Activity Log")
        log_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 6px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        log_layout = QtWidgets.QVBoxLayout(log_group)
        
        # Create a text browser for displaying debug messages
        self.debug_text_browser = QtWidgets.QTextBrowser()
        self.debug_text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: monospace;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.debug_text_browser)
        
        # Add a clear log button
        clear_button = QtWidgets.QPushButton("Clear Log")
        clear_button.setMaximumWidth(120)
        clear_button.clicked.connect(self.debug_text_browser.clear)
        log_layout.addWidget(clear_button, 0, Qt.AlignRight)
        
        main_layout.addWidget(log_group)
        
        # Connect signals
        self.showStatusSignal.connect(self.showStatus)
        self.serverSignal.connect(self.showServerStatus)
        
        # Start the server
        self.activateCompileServer()

    def update_connection_status(self):
        if hasattr(self.device, 'connected') and self.device.connected:
            self.connection_status.setText("ExpEYES device: Connected")
            self.connection_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.connection_status.setText("ExpEYES device: Not connected")
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")

    def activateCompileServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)  # Set a timeout to avoid blocking indefinitely
        try:
            s.connect(("8.8.8.8", 80))  # Connect to a public IP address
            self.local_ip = s.getsockname()[0]
        except:
            self.local_ip = 'localhost'
        
        from .online.compile_server import create_server
        self.compile_thread = create_server(self.showStatusSignal, self.serverSignal, os.path.join(os.path.dirname(__file__), 'online', 'static' ), self.local_ip, self.device)
        
        s.close()
        self.serverActive = True
        self.server_status.setText("● SERVER ACTIVE")
        self.server_status.setStyleSheet("QLabel { color: green; font-weight: bold; }")
        self.ip_display.setText(f"Server running at: http://{self.local_ip}:8888/visual")
        self.showStatus(f"Visual Coding environment active at {self.local_ip}:8888", False)

    def closeEvent(self, event):
        """Ensure the thread is stopped when the dialog is closed."""
        event.ignore()
        self.showStatus('Shutting down server...', False)
        if self.external is not None:
            self.showStatus('Terminating external process...', False)
            self.external.terminate()
            self.external.waitForFinished(1000)
        
        event.accept()

    def openBrowser(self):
        url = f"http://localhost:8888/visual?connected={str(self.device.connected)}"
        self.showStatus(f"Opening browser at {url}", False)
        webbrowser.open(url)

    def showStatus(self, msg, error=None):
        # Track the last command to avoid repetition
        if not hasattr(self, '_last_command'):
            self._last_command = None
            self._last_command_count = 0
        
        command = None
        is_get_request = False
        
        # Process HTTP API calls
        if "HTTP/1.1" in msg:
            # Extract the command part
            if "GET /" in msg or "POST /" in msg:
                command_start = msg.find("/") + 1
                command_end = msg.find(" HTTP")
                if command_end > command_start:
                    command = msg[command_start:command_end]
                    is_get_request = "GET /" in msg
                    
                    # Format as a cleaner message
                    msg = f"Command: {command}"
        
        # Check if this is a repeated command (only for GET requests)
        if is_get_request and command == self._last_command:
            self._last_command_count += 1
            # Only show every 10th repetition to reduce noise but still show activity
            if self._last_command_count % 10 != 0:
                return
        else:
            # Reset counter for new commands
            self._last_command = command
            self._last_command_count = 1
        
        # If it's a repeated command that we're showing, add the count
        if is_get_request and self._last_command_count > 1 and self._last_command_count % 10 == 0:
            msg += f" (repeated x{self._last_command_count})"
        
        timestamp = time.strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {msg}"
        
        if error:
            formatted_msg += " (ERROR)"
            self.debug_text_browser.append(f"<span style='color:red'>{formatted_msg}</span>")
        else:
            self.debug_text_browser.append(formatted_msg)
        
        # Auto-scroll to the bottom
        self.debug_text_browser.verticalScrollBar().setValue(
            self.debug_text_browser.verticalScrollBar().maximum()
        )

    def showServerStatus(self, msg):
        self.showStatus("Compiler: Error Launching Server (Restart app)", True)
        self.server_status.setText("● SERVER ERROR")
        self.server_status.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        QtWidgets.QMessageBox.warning(self, 'Server Error', msg)

    def showPipInstaller(self, name):
        from .utilities.pipinstallerMP import PipInstallDialog
        self.pipdialog = PipInstallDialog(name, self)
        self.pipdialog.show()

    def launchPipInstaller(self):
        self.showPipInstaller("blockly bottle cherrypy")
        
# This section is necessary for running new.py as a standalone program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Expt(None)  # Pass None for the device in standalone mode
    window.show()
    sys.exit(app.exec_()) 