## jithinbp@gmail.com
## Email for corrections. 

import eyes17.eyes
p = eyes17.eyes.open()

import time
from matplotlib import pyplot as plt
from scipy.signal import butter, filtfilt, hilbert
import numpy as np

from matplotlib.widgets import Button


maxamp = 4
signal_freq = 2500  # Frequency of the reference signal (Hz)
# Generate a sine wave
p.set_sine_amp(2)  # 1V amplitude. 0=80mV , 1=1V , 2 = 3V
p.set_sine(signal_freq)
p.select_range('A1', maxamp)
p.select_range('A2', maxamp)

TG = 20
time.sleep(1)
# Function to acquire data and process it
def acquire_and_process():


    # Capture data from A1 and A2
    t, v, tt, vv = p.capture2(5000, TG)  # t and tt are in milliseconds

    # Convert time from milliseconds to seconds
    t = t / 1000  # Convert to seconds
    tt = tt / 1000  # Convert to seconds

    # Parameters
    sampling_rate = 1 / (TG * 1e-6)  # Calculate sampling rate from time array

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

    return t, v, vv, in_phase_filtered, quadrature_filtered, amplitude, phase, dc_amplitude, dc_phase

# Function to update the plot
def update_plot(event):
    global t, v, vv, in_phase_filtered, quadrature_filtered, amplitude, phase, dc_amplitude, dc_phase

    # Reacquire and process data
    t, v, vv, in_phase_filtered, quadrature_filtered, amplitude, phase, dc_amplitude, dc_phase = acquire_and_process()

    # Update the plots
    fullsignal.clear()
    fullsignal.plot(t, v, label='Reference Signal', color='blue')
    fullsignal.plot(t, vv, label='Output Signal', color='red')
    fullsignal.set_xlabel('Time (s)')
    fullsignal.set_ylabel('Voltage (V)')
    fullsignal.set_ylim([-1*maxamp, maxamp])
    fullsignal.legend()
    # Update the zoomed plot
    zoomsignal.clear()
    lenbyfifty = int(len(t)/50)
    zoomsignal.plot(t[:lenbyfifty], v[:lenbyfifty], label='Ref', color='blue')
    zoomsignal.plot(t[:lenbyfifty], vv[:lenbyfifty], label='Out', color='red')
    zoomsignal.set_xlabel('Time (s)')
    zoomsignal.set_ylabel('Voltage (V)')
    zoomsignal.set_ylim([-1*maxamp, maxamp])
    zoomsignal.legend()

    components.clear()
    components.plot(t, in_phase_filtered, label='In-Phase Component', color='green')
    components.plot(t, quadrature_filtered, label='Quadrature Component', color='orange')
    components.set_xlabel('Time (s)')
    components.set_ylabel('Voltage (V)')
    components.legend()

    results.clear()
    results.plot(t, amplitude, label='Amplitude', color='purple')
    results.plot(t, phase, label='Phase', color='brown')
    results.set_xlabel('Time (s)')
    results.set_ylabel('Amplitude (V) / Phase (rad)')
    results.set_title(f'Amplitude: {dc_amplitude:.4f} V, Phase: {180*dc_phase/np.pi:.4f} °')
    results.legend()

    plt.draw()

# Create the plot
# fig, (fullsignal, components, results) = plt.subplots(3, 1, figsize=(12, 8))
fig = plt.figure(figsize=(10, 8))

gs = fig.add_gridspec(3,2)
fullsignal = fig.add_subplot(gs[0, 0])
zoomsignal = fig.add_subplot(gs[0, 1])
components = fig.add_subplot(gs[1, :])
results = fig.add_subplot(gs[2, :])

# Add a refresh button
ax_button = plt.axes([0.8, 0.02, 0.1, 0.05])
button = Button(ax_button, 'Refresh')
button.on_clicked(update_plot)
font1 = {'family':'serif','color':'blue','size':20}
fig.canvas.manager.set_window_title('Digital Lock-In Amplifier Demo. WG->A1 , Output->A2') 

# Initial plot
update_plot(None)

plt.tight_layout()
plt.show()



