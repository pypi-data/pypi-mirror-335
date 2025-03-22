import sys
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QLabel, QTableWidgetItem, QHeaderView, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt

from .utilities.IOWidget import MINIINPUT
from .layouts.gauge import Gauge
from .layouts import ui_calibrator
from .interactive.myUtils import CustomGraphicsView
from .utilities.devThread import Command, SCOPESTATES
import numpy as np
import json

class Expt(QtWidgets.QWidget, ui_calibrator.Ui_Form):
    def __init__(self, device, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.device = device  # Device handler passed to the Expt class.
        
        # Set up UI elements that aren't in the .ui file
        self.setupAdditionalUI()
        
        if not hasattr(self.device, 'aboutArray') or not self.device.calibrated:
            self.calibrationTitle.setText('Device not calibrated')
            self.calibrationTitle.setStyleSheet('color:red;')
            # Display default or empty calibration table
            self.createEmptyCalibrationTable()
        else:
            self.calibrationTitle.setText('Device Calibration Data')
            self.calibrationTitle.setStyleSheet('color:green;')
            # Format and display the calibration data
            print(self.device.aboutArray)
            self.formatAndDisplayCalibration(self.device.aboutArray)
        
        # Connect buttons to functions
        self.saveFileButton.clicked.connect(self.saveCalibrationFile)
        self.loadFileButton.clicked.connect(self.readCalibrationFile)
        self.readDeviceButton.clicked.connect(self.readCalibrationDevice)
        self.saveDeviceButton.clicked.connect(self.saveCalibrationDevice)

    def setupAdditionalUI(self):
        """Set up additional UI elements"""
        # Create button row for file operations
        buttonLayout = QtWidgets.QHBoxLayout()
        
        self.saveFileButton = QPushButton("Save to File")
        self.loadFileButton = QPushButton("Load from File")
        self.readDeviceButton = QPushButton("Read from Device")
        self.saveDeviceButton = QPushButton("Save to Device")
        
        buttonLayout.addWidget(self.saveFileButton)
        buttonLayout.addWidget(self.loadFileButton)
        buttonLayout.addWidget(self.readDeviceButton)
        buttonLayout.addWidget(self.saveDeviceButton)
        
        # Add explanatory text
        helpText = QLabel("Calibration coefficients are used to convert ADC readings to physical units.")
        helpText.setWordWrap(True)
        helpText.setStyleSheet("color: #555; font-style: italic;")
        
        # Add to the main layout - assuming there's a verticalLayout in the UI file
        self.verticalLayout.addWidget(helpText)
        self.verticalLayout.addLayout(buttonLayout)

    def createEmptyCalibrationTable(self):
        """Create an empty table with appropriate headers"""
        headers = ["Channel", "Slope", "Intercept", "Unit"]
        self.calibrationTable.setRowCount(0)
        self.calibrationTable.setColumnCount(len(headers))
        self.calibrationTable.setHorizontalHeaderLabels(headers)
        self.calibrationTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def formatAndDisplayCalibration(self, calibration_data):
        """Format calibration data into a user-friendly table with proper sections for ADC channels"""
        # Use clear headers
        headers = ["Parameter", "Value", "Description"]
        self.calibrationTable.setColumnCount(len(headers))
        self.calibrationTable.setHorizontalHeaderLabels(headers)
        
        # Create structured data for display
        display_data = []
        current_channel = None
        current_section = None
        
        # Process the calibration data structure
        for i, row in enumerate(calibration_data):
            if not row:  # Skip empty rows
                continue
            
            # Create section headers for different ADC channels
            if isinstance(row, list) and len(row) >= 1:
                if isinstance(row[0], str) and row[0] == 'ADC Channel':
                    current_channel = row[1] if len(row) > 1 else "Unknown"
                    display_data.append([f"--- ADC Channel {current_channel} ---", "", "Analog-Digital Converter Settings"])
                    current_section = "ADC"
                    continue
                
                if isinstance(row[0], str) and row[0] == 'Gain':
                    display_data.append(["Gain", "Coefficients", "Polynomial terms for calibration"])
                    current_section = "Gain"
                    continue
                
                if isinstance(row[0], str) and row[0] == 'Calibrated :':
                    calibrated_item = row[1] if len(row) > 1 else "Unknown"
                    display_data.append([f"--- Calibrated: {calibrated_item} ---", "", f"Calibration parameters for {calibrated_item}"])
                    current_section = "Calibrated"
                    continue
                
                if isinstance(row[0], str) and row[0] == 'Calibration Found':
                    display_data.append(["Calibration Status", "Valid", "Device has valid calibration data"])
                    continue
                
                # Process coefficient rows for ADC calibration
                if current_section == "ADC" and current_channel and len(row) >= 4 and isinstance(row[0], int):
                    gain_level = row[0]
                    quadratic = row[1] if len(row) > 1 else "0"
                    linear = row[2] if len(row) > 2 else "0"
                    constant = row[3] if len(row) > 3 else "0"
                    
                    # Format with complete polynomial equation
                    polynomial = f"V = {quadratic}x² + {linear}x + {constant}"
                    description = f"Gain level {gain_level} calibration polynomial"
                    
                    display_data.append([
                        f"{current_channel} Gain {gain_level}", 
                        polynomial,
                        description
                    ])
                    continue
                
                # Handle the specific entries at the beginning
                if i < 3 and isinstance(row[0], str):  # First few rows have special formats
                    if row[0] == 'Current Source Value':
                        value = row[1] if len(row) > 1 else "N/A"
                        display_data.append(["Current Source", value, "Base current source value"])
                    
                    elif row[0].startswith('Capacitance'):
                        # Handle the capacitance row which has multiple values
                        capacitance_values = row[1:] if len(row) > 1 else ["N/A"]
                        value_str = ", ".join([str(val) for val in capacitance_values])
                        display_data.append(["Capacitance Cal. Factors", value_str, "Correction factors for different ranges"])
                    
                    elif row[0] == 'SEN':
                        value = row[1] if len(row) > 1 else "N/A"
                        display_data.append(["SEN Coefficient", value, "Correction factor for resistance sensor"])
                    
                    continue
                
                # Default handling for any other rows
                if len(row) >= 2:
                    param = str(row[0])  # Convert to string to ensure we can display it properly
                    value = row[1] if len(row) > 1 else ""
                    desc = self.getCalibrationDescription(param) if isinstance(param, str) else ""
                    display_data.append([param, value, desc])
        
        # Populate the table with processed data
        self.calibrationTable.setRowCount(len(display_data))
        
        # Alternating section colors for better readability
        section_colors = [QColor("#e3f2fd"), QColor("#f1f8e9")]  # Light blue, light green
        current_section_color = 0
        current_section_name = None
        
        for row_idx, row_data in enumerate(display_data):
            # Check if this is a section header (they start with ---)
            is_section_header = False
            if isinstance(row_data[0], str) and row_data[0].startswith("---"):
                current_section_name = row_data[0]
                current_section_color = (current_section_color + 1) % len(section_colors)
                is_section_header = True
            
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                
                # Style based on item type
                if is_section_header:  # Section headers
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                    item.setBackground(section_colors[current_section_color])
                elif col_idx == 0:  # Parameter names
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                    
                    # Use subtle background for alternating rows
                    if row_idx % 2 == 0 and not is_section_header:
                        item.setBackground(QColor("#f9f9f9"))
                
                self.calibrationTable.setItem(row_idx, col_idx, item)
        
        # Set up the table appearance
        self.calibrationTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.calibrationTable.verticalHeader().setVisible(False)  # Hide vertical header
        self.calibrationTable.setAlternatingRowColors(True)

    def getCalibrationDescription(self, param_name):
        """Return descriptive text for known calibration parameters"""
        descriptions = {
            "PV1": "Programmable Voltage Source 1",
            "PV2": "Programmable Voltage Source 2",
            "PV3": "Programmable Voltage Source 3",
            "CH1": "Analog Channel 1",
            "CH2": "Analog Channel 2",
            "CH3": "Analog Channel 3",
            "RESISTANCE": "Resistance measurement",
            "CAPACITANCE": "Capacitance measurement",
            "PCS": "Current source",
            # Add more as needed
        }
        return descriptions.get(param_name, "Calibration parameter")

    def saveCalibrationFile(self):
        """Save calibration data to a JSON file"""
        if not hasattr(self.device, 'aboutArray') or not self.device.calibrated:
            QMessageBox.warning(self, "No Calibration Data", "No calibration data available to save.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Calibration Data", "", "JSON Files (*.json);;All Files (*)")
        if not file_path:
            return
            
        try:
            # Get calibration data from device
            calibration_data = {
                "aboutArray": self.device.aboutArray,
            }
            
            # Add CAL dictionary if it exists
            if hasattr(self.device, 'CAL'):
                calibration_data["CAL"] = self.device.CAL
                
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(calibration_data, f, indent=4)
                
            QMessageBox.information(self, "Success", f"Calibration data saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save calibration data: {str(e)}")

    def readCalibrationFile(self):
        """Load calibration data from a JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Calibration Data", "", "JSON Files (*.json);;All Files (*)")
        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as f:
                calibration_data = json.load(f)
                
            # Display the loaded data
            if "aboutArray" in calibration_data:
                self.formatAndDisplayCalibration(calibration_data["aboutArray"])
                self.calibrationTitle.setText(f'Calibration Data (from file: {os.path.basename(file_path)})')
                self.calibrationTitle.setStyleSheet('color:blue;')
            else:
                QMessageBox.warning(self, "Invalid Format", "The selected file does not contain valid calibration data.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load calibration data: {str(e)}")

    def readCalibrationDevice(self):
        """Read calibration data from connected device"""
        if not self.device or not self.device.connected:
            QMessageBox.warning(self, "No Device", "No device connected or device not available.")
            return
            
        try:
            # Request fresh calibration data from device
            if hasattr(self.device, 'get_calibration'):
                calibration_data = self.device.get_calibration()
                self.formatAndDisplayCalibration(calibration_data)
                self.calibrationTitle.setText('Device Calibration Data (refreshed)')
                self.calibrationTitle.setStyleSheet('color:green;')
            else:
                QMessageBox.information(self, "Not Supported", "This device does not support reading calibration data directly.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read calibration from device: {str(e)}")

    def saveCalibrationDevice(self):
        """Save current calibration data to device"""
        if not self.device or not self.device.connected:
            QMessageBox.warning(self, "No Device", "No device connected or device not available.")
            return
            
        # Confirm before writing to device
        reply = QMessageBox.question(self, "Confirm Write", 
                                    "Are you sure you want to write calibration data to the device? This may overwrite existing calibration.",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
            
        try:
            # Extract calibration data from the table
            rows = self.calibrationTable.rowCount()
            calibration_data = []
            
            for row in range(rows):
                row_data = []
                for col in range(self.calibrationTable.columnCount()):
                    item = self.calibrationTable.item(row, col)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                calibration_data.append(row_data)
                
            # Call device method to save calibration if available
            if hasattr(self.device, 'save_calibration'):
                self.device.save_calibration(calibration_data)
                QMessageBox.information(self, "Success", "Calibration data saved to device.")
            else:
                QMessageBox.information(self, "Not Supported", "This device does not support writing calibration data directly.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save calibration to device: {str(e)}")


# This section is necessary for running calibrator.py as a standalone program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Expt(None)  # Pass None for the device in standalone mode
    window.show()
    sys.exit(app.exec_()) 