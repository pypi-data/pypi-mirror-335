import platform
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget

from ..layouts.gauge import Gauge
from ..layouts import ui_miniInputSelector
from functools import partial
from .devThread import Command, SCOPESTATES

class MINIINPUT(QtWidgets.QDialog, ui_miniInputSelector.Ui_Form):
    SLIDER_SCALING = 1000.

    def __init__(self, parent, device, name, **kwargs):
        super(MINIINPUT, self).__init__(parent)
        self.setupUi(self)
        self.p = device
        self.scope_thread = kwargs.get('scope_thread',None)
        self.name = name
        self.needs_update = True
        if self.scope_thread:
            if name in ['A1','A2']:
                self.scope_thread.add_command(Command('select_range',{'channel':name, 'value':8}))
            if name in ['A1','A2','A3']:
                self.scope_thread.voltage_ready.connect(self.voltage_ready)
        else:
            if name in ['A1','A2']:
                self.p.select_range(name,8)

        widgets={ # [Input, min, max, read_function]
            'RES':[True,0,100e3,Command('get_resistance',{}) if self.scope_thread else self.p.get_resistance],
            'A1':[True,-5,5,Command('get_average_voltage',{'channel':'A1'}) if self.scope_thread else partial(self.p.get_average_voltage,'A1')],
            'A2':[True,-5,5,Command('get_average_voltage',{'channel':'A2'}) if self.scope_thread else partial(self.p.get_average_voltage,'A2')],
            'A3':[True,-3,3,Command('get_average_voltage',{'channel':'A3'}) if self.scope_thread else partial(self.p.get_average_voltage,'A3')],
            'PV1':[False,-5,5,Command('set_pv1',{'voltage':0}) if self.scope_thread else self.p.set_pv1],
            'PV2':[False,-3,3,Command('set_pv2',{'voltage':0}) if self.scope_thread else self.p.set_pv2],
            'WG':[False,5,5000,Command('set_sine',{'frequency':0}) if self.scope_thread else self.p.set_sine],
            'SQ1':[False,1,5000,Command('set_sqr1',{'frequency':0,'duty_cycle':50}) if self.scope_thread else self.p.set_sqr1],
            'SQ2':[False,1,5000,Command('set_sqr2',{'frequency':0,'duty_cycle':50}) if self.scope_thread else self.p.set_sqr2],
        }

        self.gauge_widget = Gauge(self, name)
        self.gauge_widget.title_fontsize = 28
        self.gauge_widget.setMinimumWidth(200)
        self.readFunction = None
        self.writeFunction = None
        self.last_value = 0
        self.needs_update = False
        if name in widgets:
            prop = widgets[name]
            self.gauge_widget.setObjectName(name)
            self.gauge_widget.set_MinValue(widgets[name][1])
            self.max_value = widgets[name][2]
            self.gauge_widget.set_MaxValue(widgets[name][2])
            if prop[0]:
                self.readFunction = prop[3]
            else:
                self.writeFunction = prop[3]
                self.gauge_widget.value_needle_snapzone = 1
                self.gauge_widget.valueChanged.connect(self.update_write_value)
                self.gauge_widget.wheel_enabled = True

        self.gaugeLayout.addWidget(self.gauge_widget)

    def update_write_value(self, value):
        if self.writeFunction:
            self.gauge_widget.value = value
            self.gauge_widget.update()
            self.last_value = value
            self.needs_update = True

    def voltage_ready(self, channel, value):
            if self.name == channel:
                self.last_value = value
                self.gauge_widget.update_value(value)

    def update_vals(self):
        if self.scope_thread:
            if self.readFunction:
                self.scope_thread.add_command(self.readFunction)
            elif self.writeFunction:
                if not (self.last_value == self.gauge_widget.realvalue):
                    self.needs_update = True
                #print(self.last_value, self.gauge_widget.realvalue, needs_update)
                self.writeFunction.args['voltage'] = self.last_value
                self.writeFunction.args['frequency'] = self.last_value #such a hack.
                if self.needs_update:
                    #print('written')
                    self.scope_thread.add_command(self.writeFunction)
                    self.needs_update = False
                self.gauge_widget.realvalue = self.last_value

        else:
            if self.readFunction:
                value = self.readFunction()
                self.last_value = value
                self.gauge_widget.update_value(value)
            elif self.writeFunction:
                self.writeFunction(self.last_value)
                self.gauge_widget.realvalue = self.last_value


    def reconnect(self, device):
        self.p = device


