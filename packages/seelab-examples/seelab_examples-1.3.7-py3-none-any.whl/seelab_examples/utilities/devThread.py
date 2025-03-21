import time
from PyQt5 import QtCore
from queue import Queue
from dataclasses import dataclass
from enum import Enum, auto
import numpy as np

@dataclass
class Command:
    type: str
    args: dict

class SCOPESTATES(Enum):
    FREE = 1
    CAPTURING = 2
    COMPLETED = 3
    FETCHING = 4
    CAPTURING_FULLSPEED = 5

class DeviceThread(QtCore.QThread):
    data_ready = QtCore.pyqtSignal(object, object)
    voltage_ready = QtCore.pyqtSignal(str, float)
    resistance_ready = QtCore.pyqtSignal(float)
    capacitance_ready = QtCore.pyqtSignal(float)
    timing_ready = QtCore.pyqtSignal(float)
    frequency_ready = QtCore.pyqtSignal(str, float, float)
    duty_cycle_ready = QtCore.pyqtSignal(float,float)
    counts_ready = QtCore.pyqtSignal(int)
    progress_ready = QtCore.pyqtSignal(bool, bool, float)
    trace_ready = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()
    connErrorSignal = QtCore.pyqtSignal()
    execute_function_signal = QtCore.pyqtSignal(str, object, dict)
    
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.timeData = {}
        self.voltData = {}
        self.running = True
        self.fetchTime = 0
        self.startTime = 0
        self.paused = False
        self.polling = False
        self.paused = False
        self.enabled_channels = [True] * 4  # All channels enabled by default
        self.trigger_enabled = True
        self.command_queue = Queue()
        self.scope_conflict_command_queue = Queue()
        self.timebase_value = 2  # Initialize timebase_value with a default value
        self.NP = 1000
        self.state = SCOPESTATES.FREE
        self.start_time = time.time()
        self.pv2_tp = 0.1

    def disconnectSignals(self):
        try:
            self.voltage_ready.disconnect()
        except:
            pass
        try:
            self.resistance_ready.disconnect()
        except:
            pass
        try:
            self.capacitance_ready.disconnect()
        except:
            pass
        try:
            self.frequency_ready.disconnect()
        except:
            pass
        try:
            self.duty_cycle_ready.disconnect()
        except:
            pass
        try:
            self.trace_ready.disconnect()   
        except:
            pass
        try:
            self.progress_ready.disconnect()
        except:
            pass
        try:
            self.counts_ready.disconnect()
        except:
            pass
        try:
            self.execute_function_signal.disconnect()
        except:
            pass
        try:
            self.timing_ready.disconnect()
        except:
            pass
        try:
            self.finished.disconnect()
        except:
            pass
        try:
            self.data_ready.disconnect()
        except:
            pass
        self.state = SCOPESTATES.FREE

    def updateDevice(self, device):
        self.device = device
        self.state = SCOPESTATES.FREE

    def run(self):
        while self.running:
            if self.device is None or self.paused:
                time.sleep(0.1)
                continue

            if not self.device.H.connected:
                time.sleep(0.1)
                continue



            try:
                if self.state != SCOPESTATES.CAPTURING:
                    self.process_noscope_commands()
                self.process_commands()
            except Exception as e:
                pass
            time.sleep(0.001)
            #print('alive',time.time())
        print('thread is finished!!!!!!!!!!!!!!!!!!!!!!', self.running)


    def add_raw_command(self, cmd, args):
        cmd = Command(cmd, args)
        if cmd.type in ['get_voltage','get_resistance','get_capacitance','get_freq']:
            self.scope_conflict_command_queue.put(cmd)
        else:
            self.command_queue.put(cmd)

    def add_command(self, cmd: Command):
        if cmd.type in ['get_voltage','get_resistance','get_capacitance','get_freq']:
            self.scope_conflict_command_queue.put(cmd)
        else:
            self.command_queue.put(cmd)

    def process_commands(self):
        """Process all pending commands in the queue"""

        while not self.command_queue.empty():
            try:
                cmd = self.command_queue.get_nowait()
                self.execute_command(cmd)
                self.command_queue.task_done()
            except Exception as e:
                self.connErrorSignal.emit()
                print(f'Error processing command: {e}',cmd)
                break
    
    def process_noscope_commands(self):
        """Process all pending commands in the queue"""
        while not self.scope_conflict_command_queue.empty():
            try:
                cmd = self.scope_conflict_command_queue.get_nowait()
                self.execute_command(cmd)
                self.scope_conflict_command_queue.task_done()
            except Exception as e:
                print(f'Error processing command: {e}')
                break

    def isQueueEmpty(self):
        return self.command_queue.empty() and self.scope_conflict_command_queue.empty()
    
    def clearQueue(self):
        self.command_queue.queue.clear()
        self.scope_conflict_command_queue.queue.clear()

    def execute_command(self, cmd: Command):
        """Execute a single command"""
        resp = None
        if cmd.type == 'configure_trigger':
            resp=   self.device.configure_trigger(
                cmd.args['channel'],
                cmd.args['source'],
                cmd.args['level'],
                resolution = cmd.args.get('resolution', 10),
                prescaler = cmd.args.get('prescaler', 5)
            )
        elif cmd.type == 'capture_traces':
            self.state = SCOPESTATES.CAPTURING
            resp= self.device.capture_traces(
                cmd.args['num_channels'],
                cmd.args['samples'],
                cmd.args['timebase'],
                cmd.args['channel_input'],
                trigger=cmd.args['trigger']
            )
            dt = 1e-6 * cmd.args['samples'] * cmd.args['timebase'] + .01
            self.startTime = time.time()
            self.fetchTime = self.startTime + 1e-6 * cmd.args['samples'] * cmd.args['timebase'] + .01
            self.polling = dt>0.5
        elif cmd.type == 'capture_hr':
            self.state = SCOPESTATES.CAPTURING
            resp= self.device.capture_highres_traces(
                cmd.args['channel_input'],
                cmd.args['samples'],
                cmd.args['timebase'],
                trigger=cmd.args['trigger']
            )
            dt = 1e-6 * cmd.args['samples'] * cmd.args['timebase'] + .01
            self.polling = dt>0.03
        elif cmd.type == 'capture_action':
            print('capture_action',cmd.args['channel_input'],
                cmd.args['samples'],
                cmd.args['timebase'],
                cmd.args['action'])
            resp= self.device.__capture_fullspeed_hr__(
                cmd.args['channel_input'],
                cmd.args['samples'],
                cmd.args['timebase'],
                cmd.args['action']
            )
            self.state = SCOPESTATES.CAPTURING_FULLSPEED
            self.startTime = time.time()
            self.fetchTime = self.startTime + 1e-6 * cmd.args['samples'] * cmd.args['timebase'] + .01

        elif cmd.type == 'oscilloscope_progress':
            status, trigwait, resp = self.device.oscilloscope_progress()
            if status: #conversion complete
                self.state = SCOPESTATES.COMPLETED
            self.progress_ready.emit(status, trigwait,  resp)

        elif cmd.type == 'fetch_trace':
            ch = cmd.args['channel_num']
            print(f'######### Fetching trace {cmd.args["channel_num"]}')
            self.device.__fetch_channel__(ch)
            self.trace_ready.emit(cmd.args['channel_num'])

        elif cmd.type == 'fetch_partial_trace':
            ch = cmd.args['channel_num']
            self.device.__fetch_incremental_channel__(int(ch),int(cmd.args["progress"]))

            self.trace_ready.emit(cmd.args['channel_num'])

        elif cmd.type == 'enable_trigger':
            resp= self.trigger_enabled = cmd.args['enabled']
        elif cmd.type == 'set_sine':
            resp= self.device.set_sine(cmd.args['frequency'])
        elif cmd.type == 'set_wave':
            resp= self.device.set_wave(cmd.args['frequency'],cmd.args['type'])
        elif cmd.type == 'set_sine_amp':
            resp= self.device.set_sine_amp(cmd.args['index'])
        elif cmd.type == 'set_sqr1':
            resp= self.device.set_sqr1(cmd.args['frequency'],cmd.args['duty_cycle'])
        elif cmd.type == 'set_sqr2':
            resp= self.device.set_sqr2(cmd.args['frequency'],cmd.args['duty_cycle'])
        elif cmd.type == 'set_pv1':
            resp= self.device.set_pv1(cmd.args['voltage'])
        elif cmd.type == 'set_pv2':
            resp= self.device.set_pv2(cmd.args['voltage'])
        elif cmd.type == 'set_multiplexer':
            resp= self.device.set_multiplexer(cmd.args['pos'])
        elif cmd.type == 'set_pv2':
            resp= self.device.set_pv2(cmd.args['voltage'])
        elif cmd.type == 'select_range':
            resp= self.device.select_range(cmd.args['channel'],cmd.args['value'])
        elif cmd.type == 'set_state':
            resp= self.device.set_state(**cmd.args)
        elif cmd.type == 'timing':
            res= self.device.tim_helper(cmd.args['command'],cmd.args['src'],cmd.args['dst'],cmd.args['timeout'])
            if res is not None:
                self.timing_ready.emit(res)
            else:
                self.timing_ready.emit(-1)
        elif cmd.type == 'get_voltage':
            resp= self.device.get_voltage(cmd.args['channel'])
            self.voltage_ready.emit(cmd.args['channel'], resp)
        elif cmd.type == 'get_average_voltage':
            resp= self.device.get_average_voltage(cmd.args['channel'])
            self.voltage_ready.emit(cmd.args['channel'], resp)
        elif cmd.type == 'get_resistance':
            resp= self.device.get_resistance()
            self.resistance_ready.emit(resp)
        elif cmd.type == 'get_capacitance':
            resp= self.device.get_capacitance()
            self.capacitance_ready.emit(resp)
        elif cmd.type == 'get_freq':
            resp= self.device.get_freq(cmd.args['channel'],timeout = cmd.args.get('timeout',2))
            hi= 0#self.device.r2ftime(cmd.args['channel'], cmd.args['channel'])
            self.frequency_ready.emit(cmd.args['channel'], resp, hi)
        elif cmd.type == 'get_duty_cycle':
            pin = cmd.args['channel']
            timeout = cmd.args.get('timeout',2)
            resp = -1
            hi = 0
            T1, T2 = self.device.DoublePinEdges(pin, pin, 'rising', 'falling', 2, 3, timeout, sequential=True)
            if T1 is not None and T2 is not None:
                if T2[1]:
                    hi = 100 * (T2[1]) / (T1[1] - T1[0])  # T2[0] will always equal 0 because sequential mode is enabled, but one falling edge must occur between two rising edges.
                elif T2[2]:
                    hi = 100 * (T2[2]) / (T1[1] - T1[0])  # T2[1] can be zero on rare occassions if input frequency is too high causing a falling edge to be recorded before the T2 timer is active
                resp = 1./(T1[1] - T1[0])
            self.duty_cycle_ready.emit(resp, hi)
        elif cmd.type == 'start_counter':
            resp= self.device.startCounter(cmd.args['channel'])
        elif cmd.type == 'pause_counter':
            resp= self.device.pauseCounter()
        elif cmd.type == 'resume_counter':
            resp= self.device.resumeCounter()
        elif cmd.type == 'get_counts':
            resp= self.device.getCounts()
            self.counts_ready.emit(resp)
        # Add more command handlers as needed
        if 'callback' in cmd.args and cmd.args['callback'] is not None:
            cmd.args['callback'](resp)
    
    def pause(self):
        """Pause data acquisition"""
        self.paused = True
    
    def resume(self):
        """Resume data acquisition"""
        self.paused = False
    
    def stop(self):
        """Stop the thread"""
        self.running = False
        self.wait()
    
    def update_channels(self, enabled_list):
        """Update which channels are enabled"""
        self.enabled_channels = enabled_list
