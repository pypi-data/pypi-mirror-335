# seelab_examples/__init__.py

import sys,os, json, time
from .layouts import QtVersion,utils  # Added import for QtVersion
from PyQt5 import QtWidgets, QtGui, QtCore
import argparse  # Added import for argparse

from .script_runner import ScriptRunner  # Adjust the import based on your actual script structure


import sys as _sys

class MyArgumentParser(argparse.ArgumentParser):

    def print_help(self, file=None):
        if file is None:
            file = _sys.stdout
        message = "-h : show this help\n--list : List all experiments\n\nVisit http://csparkresearch.in/seelab3 to learn more about the software"
        file.write(message+"\n")

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
    progressBar.setMaximum(20)
    progressBar.setGeometry(0, splash_pix.height() - 50, splash_pix.width(), 20)
    progressBar.setRange(0,20)

    splash.show()
    splash.pbar = progressBar
    splash.show()
    return splash


def main():
    """Main entry point for the app_examples module."""
    # Load experiments from experiments.json
    experiments_file = os.path.join(os.path.dirname(__file__), 'experiments.json')
    experiments = load_experiments(experiments_file)

    # Create a list of choices for the argument parser
    choices = []
    for category, items in experiments.items():
        for item in items:
            if item['module_name']:  # Ensure module_name is not empty
                choices.append((item['module_name'], item['title']))

    parser = MyArgumentParser(description='Run a specific script from seelab_examples.')

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


    os.chdir(os.path.dirname(__file__))
    app = QtWidgets.QApplication(sys.argv)
    splash = showSplash()
    splash.showMessage("<h2><font color='Black'>Initializing...</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)

    for a in range(5):
        app.processEvents()
        time.sleep(0.01)

    #IMPORT LIBRARIES
    splash.showMessage("<h2><font color='Black'>Importing libraries...</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)
    splash.pbar.setValue(1)
    from .utilities.devThread import Command, DeviceThread, SCOPESTATES
    try:
        from .utilities.syntax import PythonHighlighter
    except:
        from utilities.syntax import PythonHighlighter


    splash.showMessage("<h2><font color='Black'>Importing communication library...</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)
    splash.pbar.setValue(2)
    from eyes17 import eyes

    splash.showMessage("<h2><font color='Black'>Importing Numpy...</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)
    splash.pbar.setValue(3)
    import pyqtgraph as pg
    import numpy as np

    splash.showMessage("<h2><font color='Black'>Importing Scipy...</font></h2>", QtCore.Qt.AlignLeft, QtCore.Qt.black)
    splash.pbar.setValue(5)
    import scipy


    window = ScriptRunner(args,splash)
    window.show()
    sys.exit(app.exec_())

# No need for the if __name__ == "__main__": block here anymore
