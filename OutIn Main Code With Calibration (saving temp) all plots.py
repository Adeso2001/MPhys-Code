import tkinter as tk
from tkinter import messagebox, filedialog
from ttkbootstrap import Style
from mcculw import ul
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo
from ui_examples_util import UIExample, show_ul_error
import numpy as np
import csv
import time
from mcculw.enums import DigitalIODirection
from digital_out import set_digital_bit
from console_examples_util import config_first_detected_device
import tkinter.font as tkFont
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Meter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime
import seaborn as sns

class CombinedInOut(UIExample):
    def __init__(self, master=None):
        super(CombinedInOut, self).__init__(master)
        self.board_num = 0
        self.running = False
        self.calibration_applied = (False, False, False, False, False, False, False, False)
        self.input_data = {i: [] for i in range(8)}  # Store data for all channels
        self.output_data = []
        self.recording = False
        self.record_data = []
        self.digital_port = None
        self.digital_input_port = None
        self.theme = 'flatly'
        self.themes = ['flatly', 'darkly', 'cosmo', 'journal', 'solar', 'superhero', 'united', 'yeti', 'cyborg', 'pulse', 'sandstone', 'minty', 'lumen', 'simplex', 'morph']
        self.ac_mode = False
        self.ac_frequency = 1.0  # Hz
        self.ac_amplitude = 2.5  # V
        self.ac_offset = 2.5     # V
        self.last_ac_update = time.time()
        self.start_time = None  # Initialize start_time
        self.ac_output_channels = []  # List to store selected AO channels for AC output
        self.ac_phase_shifts = {0: 0.0, 1: 0.0}  # Phase shifts for AO0 and AO1 in degrees
        self.calibration_data = (None, None, None, None, None, None, None, None) #raw data for calibration
        self.calibration_info = (None, None, None, None, None, None, None, None) #data headers from calibration file
        self.interpolation_options = ("linear",)
        self.previous_temperature = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.previous_voltage = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.calibration_extremes = (None, None, None, None, None, None, None, None)
        self.show_line_1 = False
        self.show_line_2 = False
        self.show_line_3 = False
        self.show_line_4 = False
        self.show_line_5 = False
        self.show_line_6 = False
        self.show_line_7 = False
        self.show_line_8 = False
        self.show_line_9 = False
        self.show_line_10 = False
        self.show_line_11 = False
        self.show_line_12 = False
        self.show_line_13 = False
        self.show_line_14 = False
        self.show_line_15 = False
        self.show_line_16 = False




        try:
            config_first_detected_device(self.board_num)
            self.device_info = DaqDeviceInfo(self.board_num)
            self.ai_info = self.device_info.get_ai_info()
            self.ao_info = self.device_info.get_ao_info()
            self.setup_digital_ports()
            self.create_widgets()
            self.initialize_input_range()
            self.initialize_all_outputs()  # Initialize all outputs to off
        except ULError as e:
            show_ul_error(e)
            self.create_unsupported_widgets()

        # Lock-in Amplifier Variables
        self.lockin_enabled = False
        self.lockin_freq = 1000  # Default reference frequency in Hz
        self.lockin_phase = 45    # Default reference phase in degrees
        self.lockin_amplitude = 0
        self.lockin_phase_deg = 0

        # Initialize Lock-in Amplifier
        self.initialize_lockin()

    def setup_digital_ports(self):
        dio_info = self.device_info.get_dio_info()
        do_port = next((p for p in dio_info.port_info if p.supports_output), None)
        if do_port:
            if do_port.is_port_configurable:
                ul.d_config_port(self.board_num, do_port.type, DigitalIODirection.OUT)
            self.digital_port = do_port.type

        di_port = next((p for p in dio_info.port_info if p.supports_input), None)
        if di_port:
            if di_port.is_port_configurable:
                ul.d_config_port(self.board_num, di_port.type, DigitalIODirection.IN)
            self.digital_input_port = di_port.type

    def create_widgets(self):
        self.style = Style(self.theme)
        self.master.title("Advanced I/O Interface")
        self.master.geometry("1200x900")

        # Set default font
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)
        self.master.option_add("*Font", default_font)

        self.create_menu()

        # Create a Canvas with scrollbars
        canvas = tk.Canvas(self.master)
        h_scrollbar = ttk.Scrollbar(self.master, orient="horizontal", command=canvas.xview)
        v_scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        main_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=main_frame, anchor="nw")

        main_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Enable scrolling with two fingers
        canvas.bind('<Enter>', lambda e: canvas.bind_all('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units")))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all('<MouseWheel>'))

        # Create frames for layout
        self.create_device_info(main_frame)

        left_frame = ttk.Frame(main_frame, padding=10)
        left_frame.grid(row=1, column=0, sticky=NSEW)

        middle_frame = ttk.Frame(main_frame, padding=10)
        middle_frame.grid(row=1, column=1, sticky=NSEW)

        right_frame = ttk.Frame(main_frame, padding=10)
        right_frame.grid(row=1, column=2, sticky=NSEW)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        self.create_digital_output_controls(left_frame)
        self.create_analog_output_controls(left_frame)
        self.create_ac_controls(left_frame)  # Add AC controls
        self.create_analog_input_indicators(middle_frame)
        self.create_temperature_indicators(middle_frame)
        self.create_calibration_frame(right_frame)
        self.create_log_area(main_frame)
        # Create a new frame for the start button and plotting controls
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=3, column=0, columnspan=2, sticky=NSEW)
        main_frame.rowconfigure(3, weight=0)

        # Center align the buttons
        for i in range(6):
            bottom_frame.columnconfigure(i, weight=1)

        # Add the start button
        self.start_button = ttk.Button(
            bottom_frame,
            text="Start",
            command=self.toggle_ai_update,
            bootstyle="success-outline"
        )
        self.start_button.grid(row=0, column=0, pady=10, padx=5)

        # Add a record button
        self.record_button = ttk.Button(
            bottom_frame,
            text="Start Recording",
            command=self.toggle_recording,
            bootstyle="warning-outline"
        )
        self.record_button.grid(row=0, column=1, pady=10, padx=5)

        # Add a theme selector
        ttk.Label(bottom_frame, text="Theme:").grid(row=0, column=2, padx=5, sticky=E)
        self.theme_combobox = ttk.Combobox(
            bottom_frame,
            values=self.themes,
            state="readonly",
            width=15,
            bootstyle="info"
        )
        self.theme_combobox.set(self.theme)
        self.theme_combobox.grid(row=0, column=3, padx=5, sticky=W)
        self.theme_combobox.bind("<<ComboboxSelected>>", self.change_theme)

        # Add a clear log button
        self.clear_log_button = ttk.Button(
            bottom_frame,
            text="Clear Log",
            command=self.clear_log,
            bootstyle="secondary-outline"
        )
        self.clear_log_button.grid(row=0, column=4, pady=10, padx=5)

        # Add a channel selector for the plot
        ttk.Label(bottom_frame, text="Plot Channel:").grid(row=0, column=5, padx=5, sticky=E)
        self.plot_channel_var = tk.IntVar(value=0)
        self.plot_channel_combobox = ttk.Combobox(
            bottom_frame,
            textvariable=self.plot_channel_var,
            values=list(range(8)),
            state="readonly",
            width=5,
            bootstyle="success"
        )
        self.plot_channel_combobox.grid(row=0, column=6, padx=5, sticky=W)
        self.plot_channel_combobox.bind("<<ComboboxSelected>>", self.update_plot_channel)

        # Add a placeholder for the plot
        self.create_plot_area(main_frame)

        main_frame.rowconfigure(2, weight=1)

        # Add advanced features
        self.create_additional_features(main_frame)
    def create_ac_controls(self, parent):
        ac_frame = ttk.Labelframe(parent, text="AC Output Controls", padding=10, bootstyle="info")
        ac_frame.grid(row=2, column=0, sticky=NSEW, pady=5)
        ac_frame.columnconfigure(1, weight=1)

        # AC Mode Toggle
        self.ac_mode_var = tk.BooleanVar(value=False)
        ac_toggle = ttk.Checkbutton(
            ac_frame,
            text="AC Mode",
            variable=self.ac_mode_var,
            command=self.toggle_ac_mode,
            bootstyle="success-round-toggle"
        )
        ac_toggle.grid(row=0, column=0, columnspan=3, sticky=EW, padx=5, pady=5)

        # Frequency Control
        ttk.Label(ac_frame, text="Frequency (Hz):").grid(row=1, column=0, sticky=E, padx=5, pady=5)
        self.freq_entry = ttk.Entry(ac_frame, width=10)
        self.freq_entry.insert(0, "1.0")
        self.freq_entry.grid(row=1, column=1, sticky=W, padx=5, pady=5)
        self.freq_entry.bind('<Return>', self.update_ac_params)

        # Amplitude Control
        ttk.Label(ac_frame, text="Amplitude (V):").grid(row=2, column=0, sticky=E, padx=5, pady=5)
        self.amp_entry = ttk.Entry(ac_frame, width=10)
        self.amp_entry.insert(0, "2.5")
        self.amp_entry.grid(row=2, column=1, sticky=W, padx=5, pady=5)
        self.amp_entry.bind('<Return>', self.update_ac_params)

        # DC Offset Control
        ttk.Label(ac_frame, text="DC Offset (V):").grid(row=3, column=0, sticky=E, padx=5, pady=5)
        self.offset_entry = ttk.Entry(ac_frame, width=10)
        self.offset_entry.insert(0, "2.5")
        self.offset_entry.grid(row=3, column=1, sticky=W, padx=5, pady=5)
        self.offset_entry.bind('<Return>', self.update_ac_params)

        # Apply to AO0 and AO1 checkboxes
        ttk.Label(ac_frame, text="Apply to:").grid(row=4, column=0, sticky=E, padx=5, pady=5)
        self.ac_output_ao0_var = tk.BooleanVar(value=False)
        self.ac_output_ao1_var = tk.BooleanVar(value=False)
        ao0_checkbox = ttk.Checkbutton(
            ac_frame,
            text="AO0",
            variable=self.ac_output_ao0_var,
            command=self.update_ac_channels,
            bootstyle="success-round-toggle"
        )
        ao0_checkbox.grid(row=4, column=1, sticky=W, padx=5, pady=5)
        ao1_checkbox = ttk.Checkbutton(
            ac_frame,
            text="AO1",
            variable=self.ac_output_ao1_var,
            command=self.update_ac_channels,
            bootstyle="success-round-toggle"
        )
        ao1_checkbox.grid(row=4, column=2, sticky=W, padx=5, pady=5)

        # Phase Shift Controls
        ttk.Label(ac_frame, text="Phase Shifts:").grid(row=5, column=0, sticky=E, padx=5, pady=5)
        
        # AO0 Phase Shift
        ao0_phase_frame = ttk.Frame(ac_frame)
        ao0_phase_frame.grid(row=5, column=1, sticky=W, padx=5, pady=5)
        
        ttk.Label(ao0_phase_frame, text="AO0:").pack(side=tk.LEFT)
        self.ao0_phase_entry = ttk.Entry(ao0_phase_frame, width=8)
        self.ao0_phase_entry.insert(0, "0.0")
        self.ao0_phase_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(ao0_phase_frame, text="°").pack(side=tk.LEFT)
        
        # AO1 Phase Shift  
        ao1_phase_frame = ttk.Frame(ac_frame)
        ao1_phase_frame.grid(row=5, column=2, sticky=W, padx=5, pady=5)
        
        ttk.Label(ao1_phase_frame, text="AO1:").pack(side=tk.LEFT)
        self.ao1_phase_entry = ttk.Entry(ao1_phase_frame, width=8)
        self.ao1_phase_entry.insert(0, "0.0")
        self.ao1_phase_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(ao1_phase_frame, text="°").pack(side=tk.LEFT)

        # Bind phase shift entries to update function
        self.ao0_phase_entry.bind('<Return>', self.update_ac_params)
        self.ao1_phase_entry.bind('<Return>', self.update_ac_params)
    def toggle_ac_mode(self):
        self.ac_mode = self.ac_mode_var.get()
        
        if self.ac_mode:
            # Check if any channels are selected before enabling
            if not (self.ac_output_ao0_var.get() or self.ac_output_ao1_var.get()):
                messagebox.showwarning("No Channels Selected", "Please select at least one output channel (AO0 or AO1) before enabling AC mode.")
                self.ac_mode = False
                self.ac_mode_var.set(False)
                return
            
            # Validate parameters before starting
            try:
                self.update_ac_params()
                self.start_time = time.time()
                self.update_ac_channels()  # Update channels after setting start_time
                self.log(f"AC mode enabled - Freq: {self.ac_frequency}Hz, Amp: {self.ac_amplitude}V, Offset: {self.ac_offset}V")
                self.log(f"Active channels: {self.ac_output_channels}")
                self.update_ac_output()
            except ValueError as e:
                self.ac_mode = False
                self.ac_mode_var.set(False)
                messagebox.showerror("Invalid Parameters", str(e))
        else:
            self.start_time = None
            # Reset outputs to DC offset when disabled
            for channel in self.ac_output_channels:
                try:
                    ao_range = self.ao_info.supported_ranges[0]
                    ul.v_out(self.board_num, channel, ao_range, self.ac_offset)
                except Exception as e:
                    self.log(f"Error resetting channel {channel}: {str(e)}")
            self.update_ac_channels()  # Update channel states
            self.log("AC mode disabled")

    def update_ac_params(self, event=None):
        try:
            self.ac_frequency = float(self.freq_entry.get())
            self.ac_amplitude = float(self.amp_entry.get())
            self.ac_offset = float(self.offset_entry.get())
            
            # Update phase shifts
            ao0_phase = float(self.ao0_phase_entry.get())
            ao1_phase = float(self.ao1_phase_entry.get())
            
            # Validate phase values (keep within 0-360 degrees)
            self.ac_phase_shifts[0] = ao0_phase % 360
            self.ac_phase_shifts[1] = ao1_phase % 360

            # Validate other values
            if self.ac_frequency <= 0:
                raise ValueError("Frequency must be positive")
            if self.ac_amplitude < 0:
                raise ValueError("Amplitude must be non-negative")
            if self.ac_offset < 0 or self.ac_offset > 5:
                raise ValueError("DC offset must be between 0 and 5V")
            if (self.ac_offset + self.ac_amplitude) > 5 or (self.ac_offset - self.ac_amplitude) < 0:
                raise ValueError("Signal would exceed output range (0-5V)")

            self.log(f"AC parameters updated - Freq: {self.ac_frequency}Hz, Amp: {self.ac_amplitude}V, " +
                     f"Offset: {self.ac_offset}V, AO0 Phase: {self.ac_phase_shifts[0]}°, AO1 Phase: {self.ac_phase_shifts[1]}°")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def update_ac_channels(self):
        previous_channels = self.ac_output_channels.copy()
        self.ac_output_channels = []
        
        # Add debug logging for checkbox states
        self.log(f"AO0 checkbox: {self.ac_output_ao0_var.get()}, AO1 checkbox: {self.ac_output_ao1_var.get()}")
        
        if self.ac_output_ao0_var.get():
            self.ac_output_channels.append(0)
        if self.ac_output_ao1_var.get():
            self.ac_output_channels.append(1)
        
        # Debug logging for channel updates
        self.log(f"Updated AC channels list: {self.ac_output_channels}")
        
        # Enable or disable controls and initialize channels
        for channel in [0, 1]:
            try:
                scale = getattr(self, f"ao_scale_{channel}")
                entry = getattr(self, f"ao_entry_{channel}")
                
                if channel in self.ac_output_channels and self.ac_mode:
                    scale.config(state='disabled')
                    entry.config(state='disabled')
                    
                    # Initialize channel with offset voltage
                    ao_range = self.ao_info.supported_ranges[0]
                    ul.v_out(self.board_num, channel, ao_range, self.ac_offset)
                    self.log(f"Initialized AC channel {channel} with offset {self.ac_offset}V")
                else:
                    scale.config(state='normal')
                    entry.config(state='normal')
            except Exception as e:
                self.log(f"Error configuring channel {channel}: {str(e)}")
    def update_ac_output(self):
        if self.ac_mode:
            # Instead of processing channels here, call individual channel updates
            if 0 in self.ac_output_channels:
                self.update_ac_output_ao0()
            if 1 in self.ac_output_channels:
                self.update_ac_output_ao1()
                
            # Schedule next update
            self.master.after(50, self.update_ac_output)

    def update_ac_output_ao0(self):
        try:
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            phase_shift_rad = np.deg2rad(self.ac_phase_shifts.get(0, 0))
            angular_frequency = 2 * np.pi * self.ac_frequency
            
            # Calculate value for AO0
            value = self.ac_offset + self.ac_amplitude * np.sin(angular_frequency * elapsed_time - phase_shift_rad)
            value = max(0, min(5, value))
            
            # Only update if the change is significant or if it's been too long since last update
            if not hasattr(self, 'last_ao0_value') or abs(value - getattr(self, 'last_ao0_value', 0)) > 0.001:
                # Output the voltage
                ao_range = self.ao_info.supported_ranges[0]
                ul.v_out(self.board_num, 0, ao_range, value)
                self.last_ao0_value = value
                
                # Update UI elements
                self.ao_value_label_0.config(text=f"{value:.2f} V")
                self.ao_entry_0.delete(0, tk.END)
                self.ao_entry_0.insert(0, f"{value:.2f}")
            
        except Exception as e:
            self.log(f"Error updating AC output for AO0: {str(e)}")
            
    def update_ac_output_ao1(self):
        try:
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            phase_shift_rad = np.deg2rad(self.ac_phase_shifts.get(1, 0))
            angular_frequency = 2 * np.pi * self.ac_frequency
            
            # Calculate value for AO1
            value = self.ac_offset + self.ac_amplitude * np.sin(angular_frequency * elapsed_time - phase_shift_rad)
            value = max(0, min(5, value))
            
            # Only update if the change is significant or if it's been too long since last update
            if not hasattr(self, 'last_ao1_value') or abs(value - getattr(self, 'last_ao1_value', 0)) > 0.001:
                # Output the voltage
                ao_range = self.ao_info.supported_ranges[0]
                ul.v_out(self.board_num, 1, ao_range, value)
                self.last_ao1_value = value
                
                # Update UI elements
                self.ao_value_label_1.config(text=f"{value:.2f} V")
                self.ao_entry_1.delete(0, tk.END)
                self.ao_entry_1.insert(0, f"{value:.2f}")
            
        except Exception as e:
            self.log(f"Error updating AC output for AO1: {str(e)}")

    def update_analog_output(self, channel, value):
        if self.ac_mode and channel in self.ac_output_channels:
            self.log(f"Cannot manually update AO{channel} while AC mode is enabled on this channel.")
            return
        
        try:
            value = float(value)
            if not (0 <= value <= 5):
                return  # Silently ignore out-of-range values
            
            # Get current value before update
            current_value = float(getattr(self, f"ao_entry_{channel}").get())
            
            # Only update if there's a significant change
            if abs(current_value - value) > 0.001:
                ao_range = self.ao_info.supported_ranges[0]
                ul.v_out(self.board_num, channel, ao_range, value)

                # Update the value label and entry
                value_label = getattr(self, f"ao_value_label_{channel}")
                value_label.config(text=f"{value:.2f} V")
                entry = getattr(self, f"ao_entry_{channel}")
                entry.delete(0, tk.END)
                entry.insert(0, f"{value:.2f}")

                self.log(f"Analog Output A{channel} set to {value:.2f} V")
        except ValueError:
            pass  # Ignore invalid values

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Data", command=self.save_data, accelerator="Ctrl+S")
        file_menu.add_command(label="Load Data", command=self.load_data, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        # Bind keyboard shortcuts
        self.master.bind_all("<Control-s>", lambda event: self.save_data())
        self.master.bind_all("<Control-o>", lambda event: self.load_data())
        self.master.bind_all("<Control-q>", lambda event: self.master.quit())

    def create_device_info(self, parent):
        info_frame = ttk.Frame(parent)
        info_frame.grid(row=0, column=0, columnspan=2, sticky=EW, pady=5)
        info_frame.columnconfigure(0, weight=1)

        device_label = ttk.Label(
            info_frame,
            text=f"Board Number {self.board_num}: {self.device_info.product_name} ({self.device_info.unique_id})",
            font=('Segoe UI', 14, 'bold')
        )
        device_label.grid(row=0, column=0, sticky=NSEW)

    def create_digital_output_controls(self, parent):
        do_frame = ttk.Labelframe(parent, text="Digital Outputs", padding=10, bootstyle="info")
        do_frame.grid(row=0, column=0, sticky=NSEW, pady=5)
        do_frame.columnconfigure(0, weight=1)

        self.do_vars = []

        for i in range(6):
            var = tk.IntVar()
            switch = ttk.Checkbutton(
                do_frame,
                text=f"D{i}",
                variable=var,
                command=lambda x=i, v=var: self.set_digital_output(x, v),
                bootstyle="success-switch"
            )
            switch.grid(row=i, column=0, sticky=EW, padx=5, pady=5)
            self.do_vars.append(var)

    def set_digital_output(self, channel, var):
        value = var.get()
        set_digital_bit(self.board_num, self.digital_port, channel, value)
        self.log(f"Digital Output D{channel} set to {value}")

    def create_analog_output_controls(self, parent):
        ao_frame = ttk.Labelframe(parent, text="Analog Outputs", padding=10, bootstyle="info")
        ao_frame.grid(row=1, column=0, sticky=NSEW, pady=5)
        ao_frame.columnconfigure(1, weight=1)

        for i in range(2):
            ttk.Label(ao_frame, text=f"A{i}:").grid(row=i, column=0, sticky=E, padx=5, pady=5)
            scale = ttk.Scale(
                ao_frame,
                from_=0,
                to=5,
                orient=tk.HORIZONTAL,
                length=200,
                command=lambda value, channel=i: self.update_analog_output(channel, value),
                bootstyle="success"
            )
            scale.grid(row=i, column=1, sticky=EW, padx=5, pady=5)
            setattr(self, f"ao_scale_{i}", scale)

            # Add an entry widget for manual input
            entry = ttk.Entry(ao_frame, width=10)
            entry.grid(row=i, column=2, sticky=EW, padx=5, pady=5)
            entry.bind('<Return>', lambda event, channel=i: self.update_analog_output_from_entry(channel, event.widget))
            setattr(self, f"ao_entry_{i}", entry)

            # Add a label to show the current value
            value_label = ttk.Label(ao_frame, text="0.00 V")
            value_label.grid(row=i, column=3, sticky=W, padx=5, pady=5)
            setattr(self, f"ao_value_label_{i}", value_label)

    def update_analog_output_from_entry(self, channel, entry):
        try:
            value = float(entry.get())
            if 0 <= value <= 5:
                # Update the scale without triggering its callback
                scale = getattr(self, f"ao_scale_{channel}")
                scale.set(value)
                
                # Directly update the output
                ao_range = self.ao_info.supported_ranges[0]
                ul.v_out(self.board_num, channel, ao_range, value)
                
                # Update the value label
                value_label = getattr(self, f"ao_value_label_{channel}")
                value_label.config(text=f"{value:.2f} V")
                
                self.log(f"Analog Output A{channel} set to {value:.2f} V")
            else:
                raise ValueError("Value must be between 0 and 5")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            # Restore previous valid value
            current_value = getattr(self, f"ao_value_label_{channel}").cget("text").split()[0]
            entry.delete(0, tk.END)
            entry.insert(0, current_value)

    def initialize_all_outputs(self):
        # Initialize digital outputs
        for i in range(6):
            set_digital_bit(self.board_num, self.digital_port, i, 0)
            self.do_vars[i].set(0)

        # Initialize analog outputs
        ao_range = self.ao_info.supported_ranges[0]
        for i in range(2):
            ul.v_out(self.board_num, i, ao_range, 0.0)
            scale = getattr(self, f"ao_scale_{i}")
            scale.set(0)
            entry = getattr(self, f"ao_entry_{i}")
            entry.delete(0, tk.END)
            entry.insert(0, "0.00")
            value_label = getattr(self, f"ao_value_label_{i}")
            value_label.config(text="0.00 V")

        self.log("All outputs initialized to off")

    def create_analog_input_indicators(self, parent):
        ai_frame = ttk.Labelframe(parent, text="Analog Inputs", padding=10, bootstyle="primary")
        ai_frame.grid(row=0, column=0, sticky=NSEW, pady=5)
        ai_frame.columnconfigure((0, 1, 2, 3), weight=1)

        ttk.Label(ai_frame, text="Range:").grid(row=0, column=0, sticky=E, padx=5, pady=5)
        self.input_range_combobox = ttk.Combobox(
            ai_frame,
            values=[x.name for x in self.ai_info.supported_ranges],
            state="readonly",
            width=15,
            bootstyle="success"
        )
        self.input_range_combobox.grid(row=0, column=1, sticky=W, padx=5, pady=5, columnspan=3)
        self.input_range_combobox.current(0)

        for i in range(8):
            row = i // 4 + 1
            col = i % 4
            ttk.Label(ai_frame, text=f"CH{i}:").grid(row=row*2-1, column=col, sticky=NSEW, padx=5, pady=5)
            value_label = ttk.Label(ai_frame, text="0.00 V", font=("Segoe UI", 13, "bold"))
            value_label.grid(row=row*2, column=col, padx=5, pady=5, sticky=NSEW)
            setattr(self, f"ai_value_label_{i}", value_label)

    def create_temperature_indicators(self, parent):
        temp_frame = ttk.Labelframe(parent, text="Temperature", padding=10, bootstyle="primary")
        temp_frame.grid(row=5, column=0, sticky=NSEW, pady=5)
        temp_frame.columnconfigure((0, 1, 2, 3), weight=2)

        for i in range(8):
            row = i // 4 
            col = i % 4
            ttk.Label(temp_frame, text=f"CH{i}:").grid(row=row*2, column=col, sticky=NSEW, padx=5, pady=5)
            value_label = ttk.Label(temp_frame, text="N/A °K", font=("Segoe UI", 13, "bold"), width=10)
            value_label.grid(row=row*2+1, column=col, padx=5, pady=5, sticky=NSEW)
            setattr(self, f"temp_value_label_{i}", value_label)

    def create_calibration_frame(self, parent):
        calibration_frame = ttk.Labelframe(parent, text="Calibration Selection", padding=10, bootstyle="primary")
        calibration_frame.grid(row=10, column=0, sticky=NSEW, pady=5)
        calibration_frame.columnconfigure((0, 1, 2, 3), weight=2)

        for i in range(8):
            row = i 
            value_label = ttk.Label(calibration_frame, text=(("CH{0}:").format((i))), font=("Segoe UI", 13, "bold"))
            value_label.grid(row=row, column=0, padx=5, pady=5, sticky=NSEW)

            value_label = ttk.Label(calibration_frame, text="Awaiting Calibration", font=("Segoe UI", 10))
            value_label.grid(row=row, column=1, padx=5, pady=5, sticky=NSEW)
            setattr(self, f"calibration_label_{i}", value_label)

            calibration_button = ttk.Button(calibration_frame,
                                          text="Select File", 
                                          bootstyle="primary-outline",
                                          command = lambda i=i: self.choose_calibration_file(i))
            calibration_button.grid(row=row, column=2, padx=5, pady=5, sticky=NSEW)
            setattr(self, f"calibration_button_{i}", calibration_button)

            apply_cal_button = ttk.Button(calibration_frame,
                                        text="Apply", 
                                        bootstyle="primary-outline",
                                        command = lambda i=i: self.apply_calibration(i))
            apply_cal_button.grid(row=row, column=3, padx=5, pady=5, sticky=NSEW)
            setattr(self, f"apply_cal_button_{i}", apply_cal_button)

            clear_cal_button = ttk.Button(calibration_frame,
                                        text="Clear", 
                                        bootstyle="primary-outline",
                                        command = lambda i=i: self.clear_calibration(i))
            clear_cal_button.grid(row=row, column=4, padx=5, pady=5, sticky=NSEW)
            setattr(self, f"clear_cal_button_{i}", clear_cal_button)

            ttk.Label(calibration_frame, text="interpolation:").grid(row=row, column=5, sticky=E, padx=5, pady=5)
            interpolation_combobox = ttk.Combobox(
                calibration_frame,
                values=("linear",),
                state="readonly",
                width=15,
                bootstyle="success"
            )
            interpolation_combobox.grid(row=row, column=6, sticky=W, padx=5, pady=5, columnspan=3)
            interpolation_combobox.current(0)
            setattr(self, f"interpolation_combobox_{i}", interpolation_combobox)

    def create_plot_controls(self, parent):
        plot_frame = ttk.Labelframe(parent, text="Plot Controls", padding=10, bootstyle="primary")

    def choose_calibration_file(self, channel):
        file_path = filedialog.askopenfilename(title="Select a file")
        if file_path:
            try:
                data = np.genfromtxt(file_path, dtype='str', delimiter=',')
                def string_to_numpy_array(input_string):
                    # Split the string by whitespace and filter out empty strings
                    number_strings = input_string.split()
                    
                    # Convert the list of strings to a numpy array of floats (or ints)
                    numbers_array = np.array([float(num) for num in number_strings])
                    
                    return numbers_array

                def get_info_after_colon_trimmed(input_string):
                    # Find the index of the first colon
                    colon_index = input_string.find(':')
                    
                    # Check if a colon was found
                    if colon_index != -1:
                        # Extract everything after the colon
                        info_after_colon = input_string[colon_index + 1:]
                        # Remove spaces immediately after the colon
                        return info_after_colon.lstrip()  # This removes leading spaces only
                    else:
                        return "No colon found in the string."

                number_strings = data[7:]

                data_array = np.zeros((0,3),dtype = 'float')

                for data_entry in number_strings:
                    temp_data_array = np.array([[0.,0.,0.]] )
                    temp_numpy_array = string_to_numpy_array(data_entry)
                    temp_data_array[0] = temp_numpy_array
                    data_array = np.vstack((data_array,temp_data_array))

                sensor_model = get_info_after_colon_trimmed(data[0])
                serial_number = get_info_after_colon_trimmed(data[1])
                interpolation_method = get_info_after_colon_trimmed(data[2])
                setpoint_limit = get_info_after_colon_trimmed(data[3])
                data_format = get_info_after_colon_trimmed(data[4])
                no_breakpoints = get_info_after_colon_trimmed(data[5])
                units = str(data[6])

                header_tuple = (sensor_model,serial_number,interpolation_method,
                                setpoint_limit,data_format,no_breakpoints,units)
                
                calibration_extremes = np.array([float(data_array[0,1]),float(data_array[-1,1])])
                list_calibration_extremes = list(self.calibration_extremes)
                list_calibration_extremes[channel] = calibration_extremes
                self.calibration_extremes = tuple(list_calibration_extremes)

                list_calibration_data = list(self.calibration_data)
                list_calibration_data[channel] = data_array
                self.calibration_data = tuple(list_calibration_data)
                
                list_calibration_info = list(self.calibration_info)
                list_calibration_info[channel] = header_tuple
                self.calibration_info = tuple(list_calibration_info)
                
                button = getattr(self, f"calibration_button_{channel}")
                file_path_segmented = file_path.split("/")
                file_name = file_path_segmented[-1]
                button.config(text=file_name)


            except Exception as e:
                messagebox.showerror("Error", f"Error loading calibration file: {e}")
            return None       

    def apply_calibration(self, channel):

        if not self.calibration_applied[channel] and self.calibration_data[channel] is not None:

            calibration_label = getattr(self, f"calibration_label_{channel}")
            calibration_label.config(text="Calibration Applied")

            list_calibration_applied = list(self.calibration_applied)
            list_calibration_applied[channel] = True
            self.calibration_applied = tuple(list_calibration_applied)

        elif self.calibration_data[channel] is None:
            messagebox.showerror("Error", "No calibration file selected")

    def clear_calibration(self, channel):
        button = getattr(self, f"calibration_button_{channel}")
        button.config(text="Select File")
        label = getattr(self, f"calibration_label_{channel}")
        label.config(text="Awaiting Calibration")
        label_temp = getattr(self, f"temp_value_label_{channel}")
        label_temp.config(text="N/A °K")
        
        list_calibration_data = list(self.calibration_data)
        list_calibration_data[channel] = None
        self.calibration_data = tuple(list_calibration_data)
        
        list_calibration_info = list(self.calibration_info)
        list_calibration_info[channel] = None
        self.calibration_info = tuple(list_calibration_info)

        list_calibration_applied = list(self.calibration_applied)
        list_calibration_applied[channel] = False
        self.calibration_applied = tuple(list_calibration_applied)

    def initialize_input_range(self):
        if hasattr(self, 'input_range_combobox'):
            self.input_range_combobox.current(0)

    def toggle_ai_update(self):
        if not self.running:
            self.running = True
            self.start_button["text"] = "Stop"
            self.update_analog_inputs()
        else:
            self.running = False
            self.start_button["text"] = "Start"

    def update_analog_inputs(self):
        if self.running:
            ai_range = self.get_input_range()
            timestamp = time.time()
            for i in range(8):
                value = self.read_analog_input(i, ai_range)
                value_label = getattr(self, f"ai_value_label_{i}")
                value_label.config(text=f"{value:.2f} V")

                # displays temperature if calibration is applied
                if self.calibration_applied[i]:
                    #gets interpolation method from combobox
                    interpolation_combobox = getattr(self, f"interpolation_combobox_{i}")
                    interpolation_index = interpolation_combobox.current()
                    interpolation_method = self.interpolation_options[interpolation_index]

                    #calculates temperature based on calibration data and interpolation method
                    temperature = self.calculate_temperature(i, interpolation_method, value)

                    #applies temperature to label
                    temp_label = getattr(self, f"temp_value_label_{i}")
                    temp_label.config(text=f"{temperature:.2f} °K")
                else:
                    temperature = 0.0
                # Record data if recording
                if self.recording:
                    self.record_data.append((timestamp, i, value, temperature))
                # Update plot data
                self.input_data[i].append((timestamp, value))
            self.update_plot()
            if self.lockin_enabled:
                self.process_lockin()
            self.master.after(50, self.update_analog_inputs)

    def calculate_temperature(self, channel, interpolation_method, voltage):
        
        #grabs calibration data for channel
        calibration_data_current = self.calibration_data[channel]
        
        #if voltage hasnt changed, returns previous temperature to save computation power
        if self.previous_voltage[channel] == voltage:
            return self.previous_temperature[channel]
        
        if interpolation_method == "linear":
            i = 0
            dummy_voltage = 0.0

            try:
            #finds index of breakpoint below voltage
                while dummy_voltage < voltage and i < len(calibration_data_current):
                    dummy_voltage = calibration_data_current[i,1]
                    i += 1
                if i ==1:
                    warning_label = getattr(self, f"temp_value_label_{channel}")
                    warning_label.config(foreground="red") # Changed color to foreground
                elif i >= len(calibration_data_current):
                    i -= 1
                    warning_label = getattr(self, f"temp_value_label_{channel}")
                    warning_label.config(foreground="red") # Changed color to foreground
                else:
                    warning_label = getattr(self, f"temp_value_label_{channel}")
                    warning_label.config(foreground="black") # Changed color to foreground
                    
                #interpolates between breakpoints to find temperature
                temperature = calibration_data_current[i-1,2] + (calibration_data_current[i,2] - calibration_data_current[i-1,2]) * (voltage - calibration_data_current[i-1,1]) / (calibration_data_current[i,1] - calibration_data_current[i-1,1])

                #updates previous voltage and temperature
                self.previous_voltage[channel] = voltage
                self.previous_temperature[channel] = temperature

                return temperature
            except:
                return 0.0


    def read_analog_input(self, channel, ai_range):
        try:
            if self.ai_info.resolution <= 16:
                value = ul.v_in(self.board_num, channel, ai_range)
            else:
                value = ul.v_in_32(self.board_num, channel, ai_range)
            return value
        except ULError as e:
            show_ul_error(e)
            return 0

    def get_input_range(self):
        if hasattr(self, 'input_range_combobox'):
            selected_index = self.input_range_combobox.current()
            return self.ai_info.supported_ranges[selected_index]
        else:
            return self.ai_info.supported_ranges[0]

    def show_about(self):
        messagebox.showinfo(
            "About",
            "Advanced Analog I/O Interface\nVersion 2.2\n\nCreated with ❤️ by Leo Feasby\n\n and Ollie did a thing"
        )

    def save_data(self):
        if not self.record_data:
            messagebox.showwarning("No Data", "No data to save. Please record some data first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Timestamp", "Channel", "Value", "Temperature"])
                writer.writerows(self.record_data)
            self.log(f"Data saved to {file_path}")

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                self.record_data = []
                self.input_data = {i: [] for i in range(8)}
                for row in reader:
                    timestamp, channel, value, temperature = float(row[0]), int(row[1]), float(row[2]), float(row[3])
                    self.record_data.append((timestamp, channel, value, temperature))
                    self.input_data[channel].append((timestamp, value))
            self.log(f"Data loaded from {file_path}")
            self.update_plot()

    def log(self, message):
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)

    def create_log_area(self, parent):
        log_frame = ttk.Labelframe(parent, text="Log", padding=10)
        log_frame.grid(row=2, column=0, columnspan=2, sticky=NSEW, pady=5)
        parent.rowconfigure(2, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        self.log_text = ttk.ScrolledText(
            log_frame,
            height=5,
            font=('Segoe UI', 10),
            wrap='word'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.record_button["text"] = "Stop Recording"
            self.record_data = []
            self.input_data = {i: [] for i in range(8)}
            self.log("Recording started")
        else:
            self.recording = False
            self.record_button["text"] = "Start Recording"
            self.log("Recording stopped")

    def create_plot_area(self, parent):
        plot_frame = ttk.Labelframe(parent, text="Real-time Plot", padding=10)
        plot_frame.grid(row=4, column=0, columnspan=2, sticky=NSEW, pady=5)
        parent.rowconfigure(4, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        # Use seaborn style for modern scientific look
        sns.set_style("darkgrid")
        self.figure = plt.Figure(figsize=(8, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)

        # Get colors from the current theme
        colors = self.style.colors
        primary_color = colors.primary
        background_color = colors.bg
        foreground_color = colors.border
        text_color = colors.fg

        self.ax.set_title(f"Analog Input CH{self.plot_channel_var.get()}", fontsize=14, color=text_color)
        self.ax.set_xlabel("Time", fontsize=12, color=text_color)
        self.ax.set_ylabel("Voltage (V)", fontsize=12, color=text_color)

        # Customize the plot to look more scientific
        self.line, = self.ax.plot([], [], '-', linewidth=2, color=primary_color)
        self.line2, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line3, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line4, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line5, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line6, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line7, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line8, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line9, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line10, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line11, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line12, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line13, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line14, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line15, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)
        self.line16, = self.ax.plot([], [], '-', linewidth=2, alpha = 0)


        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, color=foreground_color)
        self.ax.minorticks_on()
        self.figure.tight_layout()

        # Set background color
        self.ax.set_facecolor(background_color)
        self.figure.patch.set_facecolor(background_color)

        # Set tick label colors
        self.ax.tick_params(colors=text_color, which='both')

        # Update spine colors
        for spine in self.ax.spines.values():
            spine.set_edgecolor(foreground_color)

        self.canvas = FigureCanvasTkAgg(self.figure, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add navigation toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()
        self.canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)

    def update_plot(self):
        selected_channel = self.plot_channel_var.get()
        if self.input_data[selected_channel]:
            times, values = zip(*self.input_data[selected_channel])
            # Convert timestamps to datetime objects for better formatting
            times = [datetime.fromtimestamp(t) for t in times]

            # Get colors from the current theme
            colors = self.style.colors
            primary_color = colors.primary
            background_color = colors.bg
            foreground_color = colors.border
            text_color = colors.fg

            # Set line color to primary color
            self.line.set_color(primary_color)
            self.line.set_data(times, values)

            # Set title color to text color
            self.ax.set_title(f"Analog Input CH{selected_channel}", fontsize=14, color=text_color)
            self.ax.set_facecolor(background_color)
            self.ax.tick_params(colors=text_color, which='both')  # Update tick label colors

            self.ax.relim()
            self.ax.autoscale_view()
            self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            self.figure.autofmt_xdate()

            # Update spine colors
            for spine in self.ax.spines.values():
                spine.set_edgecolor(foreground_color)

            self.canvas.draw()

    def change_theme(self, event=None):
        selected_theme = self.theme_combobox.get()
        self.style.theme_use(selected_theme)
        self.theme = selected_theme
        self.log(f"Theme changed to {selected_theme}")
        self.update_plot()  # Update the plot colors

    def update_plot_channel(self, event=None):
        # Clear the current line data
        self.line.set_data([], [])
        self.ax.set_title(f"Analog Input CH{self.plot_channel_var.get()}", fontsize=14)
        self.update_plot()

    def create_additional_features(self, parent):
        # Create a new frame for additional features
        features_frame = ttk.Labelframe(parent, text="Additional Features", padding=10, bootstyle="info")
        features_frame.grid(row=5, column=0, columnspan=2, sticky=NSEW, pady=5)
        parent.rowconfigure(5, weight=1)

        # Center align the buttons
        features_frame.columnconfigure(0, weight=1)
        features_frame.columnconfigure(1, weight=1)

        # Add a 3D plot
        ttk.Label(features_frame, text="3D Visualization:").grid(row=0, column=0, sticky=E, padx=5, pady=5)
        plot3d_button = ttk.Button(
            features_frame,
            text="Show 3D Plot",
            command=self.show_3d_plot,
            bootstyle="primary-outline"
        )
        plot3d_button.grid(row=0, column=1, sticky=W, padx=5, pady=5)

        # Add data analysis options
        ttk.Label(features_frame, text="Data Analysis:").grid(row=1, column=0, sticky=E, padx=5, pady=5)
        analyze_button = ttk.Button(
            features_frame,
            text="Analyze Data",
            command=self.analyze_data,
            bootstyle="primary-outline"
        )
        analyze_button.grid(row=1, column=1, sticky=W, padx=5, pady=5)

        # Add export options
        ttk.Label(features_frame, text="Export Options:").grid(row=2, column=0, sticky=E, padx=5, pady=5)
        export_button = ttk.Button(
            features_frame,
            text="Export Plot",
            command=self.export_plot,
            bootstyle="primary-outline"
        )
        export_button.grid(row=2, column=1, sticky=W, padx=5, pady=5)

    def show_3d_plot(self):
        if not self.record_data:
            messagebox.showwarning("No Data", "No data to display. Please record some data first.")
            return

        # Create a new window for the 3D plot
        window = tk.Toplevel(self.master)
        window.title("3D Visualization")
        figure = plt.Figure(figsize=(6,5), dpi=100)
        ax = figure.add_subplot(111, projection='3d')

        # Prepare data
        timestamps = [data[0] for data in self.record_data]
        channels = [data[1] for data in self.record_data]
        values = [data[2] for data in self.record_data]
        temperatures = [data[3] for data in self.record_data]
        # Convert timestamps to datetime for labels
        times_formatted = [datetime.fromtimestamp(t) for t in timestamps]

        # Create scatter plot
        scatter = ax.scatter(channels, timestamps, values, c=values, cmap='plasma', marker='o')

        ax.set_xlabel('Channel')
        ax.set_ylabel('Time')
        ax.set_zlabel('Voltage')
        ax.set_title('3D Visualization of Recorded Data')

        # Add color bar
        figure.colorbar(scatter, ax=ax, shrink=0.5, aspect=10)

        canvas = FigureCanvasTkAgg(figure, window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()


        # Add color bar
        figure.colorbar(scatter, ax=ax, shrink=0.5, aspect=10)

        canvas = FigureCanvasTkAgg(figure, window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def analyze_data(self):
        if not self.record_data:
            messagebox.showwarning("No Data", "No data to analyze. Please record some data first.")
            return

        selected_channel = self.plot_channel_var.get()
        # Perform analysis for the selected channel
        values = [data[2] for data in self.record_data if data[1] == selected_channel]
        if not values:
            messagebox.showinfo("Data Analysis", f"No data recorded for Channel {selected_channel}.")
            return

        mean_val = np.mean(values)
        max_val = np.max(values)
        min_val = np.min(values)
        std_val = np.std(values)

        message = f"Data Analysis for Channel {selected_channel}:\nMean Voltage: {mean_val:.2f} V\nMax Voltage: {max_val:.2f} V\nMin Voltage: {min_val:.2f} V\nStandard Deviation: {std_val:.2f} V"
        messagebox.showinfo("Data Analysis", message)

    def export_plot(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All Files", "*.*")]
        )
        if file_path:
            self.figure.savefig(file_path)
            self.log(f"Plot exported to {file_path}")

    # Additions for Lock-in Amplifier Feature in CombinedInOut Class
    def initialize_lockin(self):
        # Create Lock-in Amplifier Controls
        lockin_frame = ttk.Labelframe(self.master, text="Lock-in Amplifier", padding=10, bootstyle="warning")
        lockin_frame.grid(row=6, column=0, columnspan=2, sticky=NSEW, pady=10)

        # Enable Lock-in Amplifier Checkbox
        self.lockin_var = tk.BooleanVar(value=False)
        lockin_toggle = ttk.Checkbutton(
            lockin_frame,
            text="Enable Lock-in Amplifier",
            variable=self.lockin_var,
            command=self.toggle_lockin,
            bootstyle="success-round-toggle"
        )
        lockin_toggle.grid(row=0, column=0, columnspan=2, sticky=EW, padx=5, pady=5)

        # Reference Frequency Input
        ttk.Label(lockin_frame, text="Reference Frequency (Hz):").grid(row=1, column=0, sticky=E, padx=5, pady=5)
        self.lockin_freq_entry = ttk.Entry(lockin_frame, width=10)
        self.lockin_freq_entry.insert(0, str(self.lockin_freq))
        self.lockin_freq_entry.grid(row=1, column=1, sticky=W, padx=5, pady=5)
        self.lockin_freq_entry.bind('<Return>', self.update_lockin_params)

        # Reference Phase Input
        ttk.Label(lockin_frame, text="Reference Phase (°):").grid(row=2, column=0, sticky=E, padx=5, pady=5)
        self.lockin_phase_entry = ttk.Entry(lockin_frame, width=10)
        self.lockin_phase_entry.insert(0, str(self.lockin_phase))
        self.lockin_phase_entry.grid(row=2, column=1, sticky=W, padx=5, pady=5)
        self.lockin_phase_entry.bind('<Return>', self.update_lockin_params)

        # Lock-in Amplifier Results
        ttk.Label(lockin_frame, text="Amplitude:").grid(row=3, column=0, sticky=E, padx=5, pady=5)
        self.lockin_amplitude_label = ttk.Label(lockin_frame, text="0.00 V")
        self.lockin_amplitude_label.grid(row=3, column=1, sticky=W, padx=5, pady=5)

        ttk.Label(lockin_frame, text="Phase:").grid(row=4, column=0, sticky=E, padx=5, pady=5)
        self.lockin_phase_label = ttk.Label(lockin_frame, text="0.00°")
        self.lockin_phase_label.grid(row=4, column=1, sticky=W, padx=5, pady=5)

    def toggle_lockin(self):
        self.lockin_enabled = self.lockin_var.get()
        if self.lockin_enabled:
            self.log("Lock-in Amplifier enabled")
            self.process_lockin()
        else:
            self.log("Lock-in Amplifier disabled")
            self.lockin_amplitude = 0
            self.lockin_phase_deg = 0
            self.lockin_amplitude_label.config(text="0.00 V")
            self.lockin_phase_label.config(text="0.00°")

    def update_lockin_params(self, event=None):
        try:
            freq = float(self.lockin_freq_entry.get())
            phase = float(self.lockin_phase_entry.get())
            if freq <= 0:
                raise ValueError("Frequency must be positive")
            if not (0 <= phase < 360):
                raise ValueError("Phase must be between 0° and 360°")
            self.lockin_freq = freq
            self.lockin_phase = phase
            self.log(f"Lock-in parameters updated - Frequency: {self.lockin_freq} Hz, Phase: {self.lockin_phase}°")
            if self.lockin_enabled:
                self.process_lockin()
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            # Reset to previous valid values
            self.lockin_freq_entry.delete(0, tk.END)
            self.lockin_freq_entry.insert(0, str(self.lockin_freq))
            self.lockin_phase_entry.delete(0, tk.END)
            self.lockin_phase_entry.insert(0, str(self.lockin_phase))

    def process_lockin(self):
        if self.lockin_enabled and self.record_data:
            # Get the latest recorded data for the selected channel
            selected_channel = self.plot_channel_var.get()
            data = [
                (data[0], data[2])
                for data in self.record_data
                if data[1] == selected_channel
            ]
            if not data:
                self.log("No data available for Lock-in Amplifier processing.")
                return

            timestamps, values = zip(*data)
            t = np.array(timestamps)
            input_signal = np.array(values)

            # Generate Reference Signals
            ref_phase_rad = np.deg2rad(self.lockin_phase)
            ref_signal_x = np.sin(2 * np.pi * self.lockin_freq * t + ref_phase_rad)
            ref_signal_y = np.cos(2 * np.pi * self.lockin_freq * t + ref_phase_rad)

            # Multiply Input with Reference Signals
            mixed_x = input_signal * ref_signal_x
            mixed_y = input_signal * ref_signal_y

            # Low-Pass Filter (Simple Averaging)
            filtered_x = np.mean(mixed_x)
            filtered_y = np.mean(mixed_y)

            # Calculate Amplitude and Phase
            amplitude = np.sqrt(filtered_x**2 + filtered_y**2) * 2
            phase = np.arctan2(filtered_y, filtered_x)
            phase_deg = (np.rad2deg(phase)) % 360

            # Update Labels
            self.lockin_amplitude = amplitude
            self.lockin_phase_deg = phase_deg
            self.lockin_amplitude_label.config(text=f"{self.lockin_amplitude:.2f} V")
            self.lockin_phase_label.config(text=f"{self.lockin_phase_deg:.2f}°")

            self.log(f"Lock-in Amplifier - Amplitude: {self.lockin_amplitude:.2f} V, Phase: {self.lockin_phase_deg:.2f}°")

        # Schedule next lock-in processing
        if self.lockin_enabled:
            self.master.after(1000, self.process_lockin)  # Update every second

if __name__ == "__main__":
    root = tk.Tk()
    app = CombinedInOut(root)
    root.mainloop()