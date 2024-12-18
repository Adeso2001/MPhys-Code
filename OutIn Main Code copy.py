import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from mcculw import ul
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo
from ui_examples_util import UIExample, show_ul_error, validate_float_entry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import csv
import time
from mcculw.enums import DigitalIODirection, DigitalPortType
from digital_out import set_digital_port, set_digital_bit
from digital_in import read_digital_port, read_digital_bit
from console_examples_util import config_first_detected_device


class CombinedInOut(UIExample):
    def __init__(self, master=None):
        super(CombinedInOut, self).__init__(master)
        self.board_num = 0
        self.running = False
        self.input_data = []
        self.output_data = []
        self.recording = False
        self.record_data = []
        self.digital_port = None
        self.digital_input_port = None

        try:
            config_first_detected_device(self.board_num)
            self.device_info = DaqDeviceInfo(self.board_num)
            self.ai_info = self.device_info.get_ai_info()
            self.ao_info = self.device_info.get_ao_info()
            self.setup_digital_ports()
            self.create_widgets()
        except ULError as e:
            show_ul_error(e)
            self.create_unsupported_widgets()

    def setup_digital_ports(self):
        dio_info = self.device_info.get_dio_info()
        # Setup Digital Output Port
        do_port = next((p for p in dio_info.port_info if p.supports_output), None)
        if do_port:
            if do_port.is_port_configurable:
                ul.d_config_port(self.board_num, do_port.type, DigitalIODirection.OUT)
            self.digital_port = do_port.type

        # Setup Digital Input Port
        di_port = next((p for p in dio_info.port_info if p.supports_input), None)
        if di_port:
            if di_port.is_port_configurable:
                ul.d_config_port(self.board_num, di_port.type, DigitalIODirection.IN)
            self.digital_input_port = di_port.type

    def create_widgets(self):
        # Set up the main window
        self.master.title("Advanced Analog I/O Interface")
        self.master.geometry("1000x800")
        self.master.configure(bg='#f0f0f0')

        # Configure the style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Create the main frame
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Create various UI components
        self.create_menu()
        self.create_device_info(main_frame)
        self.create_input_frame(main_frame)
        self.create_output_frame(main_frame)
        self.create_graph(main_frame)
        self.create_control_buttons(main_frame)
        self.create_data_logging_frame(main_frame)

        # Digital Output Controls
        self.create_digital_output_controls()

        # Digital Input Indicators
        self.create_digital_input_indicators()

        # Logging Area
        self.create_log_area()

    def create_menu(self):
        # Create the menu bar
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # Create File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Data", command=self.save_data)
        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Create Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    def create_device_info(self, parent):
        # Create a frame to display device information
        info_frame = ttk.LabelFrame(parent, text="Device Information", padding="5")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        device_label = ttk.Label(info_frame, text=f"Board Number {self.board_num}: {self.device_info.product_name} ({self.device_info.unique_id})")
        device_label.grid(row=0, column=0, sticky=tk.W)

    def create_input_frame(self, parent):
        # Create a frame for analog input controls
        input_frame = ttk.LabelFrame(parent, text="Analog Input", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5), pady=5)

        # Add input channel selection
        ttk.Label(input_frame, text="Channel:").grid(row=0, column=0, sticky=tk.W)
        self.input_channel_entry = ttk.Spinbox(input_frame, from_=0, to=self.ai_info.num_chans - 1, width=5)
        self.input_channel_entry.grid(row=0, column=1, sticky=tk.W)

        # Add input range selection
        ttk.Label(input_frame, text="Range:").grid(row=1, column=0, sticky=tk.W)
        self.input_range_combobox = ttk.Combobox(input_frame, values=[x.name for x in self.ai_info.supported_ranges], state="readonly", width=15)
        self.input_range_combobox.current(0)
        self.input_range_combobox.grid(row=1, column=1, sticky=tk.W)

        # Add input value display
        ttk.Label(input_frame, text="Value (V):").grid(row=2, column=0, sticky=tk.W)
        self.input_value_label = ttk.Label(input_frame, text="0.000")
        self.input_value_label.grid(row=2, column=1, sticky=tk.W)

        # Add sample rate input
        ttk.Label(input_frame, text="Sample Rate (Hz):").grid(row=3, column=0, sticky=tk.W)
        self.sample_rate_entry = ttk.Entry(input_frame, validate='key', validatecommand=(self.register(validate_float_entry), '%P'), width=10)
        self.sample_rate_entry.insert(0, "10")
        self.sample_rate_entry.grid(row=3, column=1, sticky=tk.W)

    def create_output_frame(self, parent):
        # Create a frame for analog output controls
        output_frame = ttk.LabelFrame(parent, text="Analog Output", padding="10")
        output_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0), pady=5)

        # Add output channel selection
        ttk.Label(output_frame, text="Channel:").grid(row=0, column=0, sticky=tk.W)
        self.output_channel_entry = ttk.Spinbox(output_frame, from_=0, to=self.ao_info.num_chans - 1, width=5)
        self.output_channel_entry.grid(row=0, column=1, sticky=tk.W)

        # Add output value input
        ttk.Label(output_frame, text="Value (V):").grid(row=1, column=0, sticky=tk.W)
        self.output_data_value_entry = ttk.Entry(output_frame, validate='key', validatecommand=(self.register(validate_float_entry), '%P'), width=10)
        self.output_data_value_entry.insert(0, "0")
        self.output_data_value_entry.grid(row=1, column=1, sticky=tk.W)

        # Add update button
        update_button = ttk.Button(output_frame, text="Update", command=self.update_output_value)
        update_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Add waveform generation controls
        ttk.Label(output_frame, text="Waveform:").grid(row=3, column=0, sticky=tk.W)
        self.waveform_combobox = ttk.Combobox(output_frame, values=["Sine", "Square", "Triangle"], state="readonly", width=15)
        self.waveform_combobox.current(0)
        self.waveform_combobox.grid(row=3, column=1, sticky=tk.W)

        ttk.Label(output_frame, text="Frequency (Hz):").grid(row=4, column=0, sticky=tk.W)
        self.frequency_entry = ttk.Entry(output_frame, validate='key', validatecommand=(self.register(validate_float_entry), '%P'), width=10)
        self.frequency_entry.insert(0, "1")
        self.frequency_entry.grid(row=4, column=1, sticky=tk.W)

        generate_button = ttk.Button(output_frame, text="Generate Waveform", command=self.generate_waveform)
        generate_button.grid(row=5, column=0, columnspan=2, pady=(10, 0))

    def create_graph(self, parent):
        # Create a frame for the graph
        graph_frame = ttk.Frame(parent)
        graph_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        parent.rowconfigure(2, weight=1)

        # Set up the matplotlib figure and axes
        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Configure the axes
        self.ax1.set_title("Input Signal")
        self.ax2.set_title("Output Signal")
        self.line1, = self.ax1.plot([], [])
        self.line2, = self.ax2.plot([], [])

        # Add toolbar
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(self.canvas, graph_frame)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def create_control_buttons(self, parent):
        # Create a frame for control buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=tk.E, pady=(0, 10))

        # Add Start/Stop button
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Add Record button
        self.record_button = ttk.Button(button_frame, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(side=tk.LEFT, padx=5)

        # Add Quit button
        quit_button = ttk.Button(button_frame, text="Quit", command=self.master.destroy)
        quit_button.pack(side=tk.LEFT)

    def create_data_logging_frame(self, parent):
        # Create a frame for data logging
        log_frame = ttk.LabelFrame(parent, text="Data Logging", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Add text widget for logging
        self.log_text = tk.Text(log_frame, height=5, width=80)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar to the text widget
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text.configure(yscrollcommand=scrollbar.set)

    def update_input_value(self):
        # Get the current input channel and range
        channel = self.get_input_channel_num()
        ai_range = self.get_input_range()

        try:
            # Read the input value from the device
            if self.ai_info.resolution <= 16:
                value = ul.v_in(self.board_num, channel, ai_range)
            else:
                value = ul.v_in_32(self.board_num, channel, ai_range)

            # Update the display and store the value
            self.input_value_label["text"] = '{:.3f}'.format(value)
            self.input_data.append(value)
            if len(self.input_data) > 100:
                self.input_data.pop(0)

            # Update the graph
            self.update_graph()

            # Record the data if recording is active
            if self.recording:
                self.record_data.append((time.time(), value))

            # Schedule the next update if running
            if self.running:
                self.master.after(int(1000 / float(self.sample_rate_entry.get())), self.update_input_value)
        except ULError as e:
            self.stop()
            show_ul_error(e)

    def update_output_value(self):
        # Get the current output channel and value
        channel = self.get_output_channel_num()
        ao_range = self.ao_info.supported_ranges[0]
        data_value = self.get_output_data_value()

        try:
            # Write the output value to the device
            ul.v_out(self.board_num, channel, ao_range, data_value)
            self.output_data.append(data_value)
            if len(self.output_data) > 100:
                self.output_data.pop(0)
            self.update_graph()
        except ULError as e:
            show_ul_error(e)

    def update_graph(self):
        # Update the data for both input and output graphs
        self.line1.set_data(range(len(self.input_data)), self.input_data)
        self.line2.set_data(range(len(self.output_data)), self.output_data)
        
        # Adjust the graph limits and redraw
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        
        self.canvas.draw()

    def start(self):
        if not self.running:
            self.running = True
            self.start_button["text"] = "Stop"
            self.update_input_value()
        else:
            self.stop()

    def stop(self):
        self.running = False
        self.start_button["text"] = "Start"

    def get_input_channel_num(self):
        try:
            return int(self.input_channel_entry.get())
        except ValueError:
            return 0

    def get_output_channel_num(self):
        try:
            return int(self.output_channel_entry.get())
        except ValueError:
            return 0

    def get_input_range(self):
        selected_index = self.input_range_combobox.current()
        return self.ai_info.supported_ranges[selected_index]

    def get_output_data_value(self):
        try:
            return float(self.output_data_value_entry.get())
        except ValueError:
            return 0

    def show_about(self):
        messagebox.showinfo("About", "Advanced Analog I/O Interface\nVersion 1.1\n\nCreated with ❤️ by Leo Feasby")

    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.record_button["text"] = "Stop Recording"
            self.record_data = []
            self.log("Recording started.")
        else:
            self.recording = False
            self.record_button["text"] = "Start Recording"
            self.log(f"Recording stopped. {len(self.record_data)} samples collected.")

    def generate_waveform(self):
        # Get waveform parameters
        waveform = self.waveform_combobox.get()
        frequency = float(self.frequency_entry.get())
        duration = 5  # Generate 5 seconds of data
        sample_rate = 1000  # 1000 Hz sample rate

        # Generate time array
        t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
        
        # Generate waveform based on selected type
        if waveform == "Sine":
            y = np.sin(2 * np.pi * frequency * t)
        elif waveform == "Square":
            y = np.sign(np.sin(2 * np.pi * frequency * t))
        elif waveform == "Triangle":
            y = 2 * np.abs(2 * (t * frequency - np.floor(0.5 + t * frequency))) - 1

        # Update output data and graph
        self.output_data = list(y)
        self.update_graph()
        self.log(f"Generated {waveform} waveform at {frequency} Hz.")

    def save_data(self):
        if not self.record_data:
            messagebox.showwarning("No Data", "No data to save. Please record some data first.")
            return

        # Open file dialog to choose save location
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            # Write data to CSV file
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Timestamp", "Value"])
                writer.writerows(self.record_data)
            self.log(f"Data saved to {file_path}")

    def load_data(self):
        # Open file dialog to choose file to load
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            # Read data from CSV file
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                self.record_data = [(float(row[0]), float(row[1])) for row in reader]
            self.log(f"Data loaded from {file_path}")
            self.update_graph()

    def log(self, message):
        # Add timestamped message to log
        self.log_text.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)

    def create_digital_output_controls(self):
        do_frame = ttk.LabelFrame(self.master, text="Digital Output", padding="10")
        do_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Set Port Value
        ttk.Label(do_frame, text="Port Value (Hex):").grid(row=0, column=0, sticky=tk.W)
        self.port_value_var = tk.StringVar()
        self.port_value_entry = ttk.Entry(do_frame, textvariable=self.port_value_var)
        self.port_value_entry.grid(row=0, column=1, sticky=tk.W)
        self.port_value_var.set("FF")  # Default value

        set_port_button = ttk.Button(do_frame, text="Set Port", command=self.set_port)
        set_port_button.grid(row=0, column=2, padx=5)

        # Set Bit Value
        ttk.Label(do_frame, text="Bit Number:").grid(row=1, column=0, sticky=tk.W)
        self.bit_num_var = tk.IntVar(value=0)
        self.bit_num_spinbox = ttk.Spinbox(do_frame, from_=0, to=7, textvariable=self.bit_num_var, width=5)
        self.bit_num_spinbox.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(do_frame, text="Bit Value:").grid(row=2, column=0, sticky=tk.W)
        self.bit_value_var = tk.IntVar(value=0)
        self.bit_value_checkbox = ttk.Checkbutton(do_frame, variable=self.bit_value_var, command=self.set_bit)
        self.bit_value_checkbox.grid(row=2, column=1, sticky=tk.W)

    def set_port(self):
        if self.digital_port is None:
            self.log("Digital port not configured.")
            return
        try:
            value = int(self.port_value_var.get(), 16)
            set_digital_port(self.board_num, self.digital_port, value)
            self.log(f"Set port {self.digital_port.name} to {value:#04x}")
        except ValueError:
            self.log("Invalid hex value entered.")
        except Exception as e:
            self.log(f"Error: {e}")

    def set_bit(self):
        if self.digital_port is None:
            self.log("Digital port not configured.")
            return
        bit_num = self.bit_num_var.get()
        bit_value = self.bit_value_var.get()
        set_digital_bit(self.board_num, self.digital_port, bit_num, bit_value)
        self.log(f"Set bit {bit_num} of port {self.digital_port.name} to {bit_value}")

    def create_digital_input_indicators(self):
        di_frame = ttk.LabelFrame(self.master, text="Digital Input", padding="10")
        di_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Read Port Value
        read_port_button = ttk.Button(di_frame, text="Read Port", command=self.read_port)
        read_port_button.grid(row=0, column=0, padx=5, pady=5)

        self.port_value_label = ttk.Label(di_frame, text="Port Value: 00")
        self.port_value_label.grid(row=0, column=1, padx=5, pady=5)

        # Read Bit Value
        ttk.Label(di_frame, text="Bit Number:").grid(row=1, column=0, sticky=tk.W)
        self.read_bit_num_var = tk.IntVar(value=0)
        self.read_bit_spinbox = ttk.Spinbox(di_frame, from_=0, to=7, textvariable=self.read_bit_num_var, width=5)
        self.read_bit_spinbox.grid(row=1, column=1, sticky=tk.W)

        read_bit_button = ttk.Button(di_frame, text="Read Bit", command=self.read_bit)
        read_bit_button.grid(row=1, column=2, padx=5, pady=5)

        self.bit_value_label = ttk.Label(di_frame, text="Bit Value: 0")
        self.bit_value_label.grid(row=1, column=3, padx=5, pady=5)

    def read_port(self):
        if self.digital_input_port is None:
            self.log("Digital input port not configured.")
            return
        value = read_digital_port(self.board_num, self.digital_input_port)
        if value is not None:
            self.port_value_label.config(text=f"Port Value: {value:#04x}")
            self.log(f"Read port {self.digital_input_port.name}: {value:#04x}")

    def read_bit(self):
        if self.digital_input_port is None:
            self.log("Digital input port not configured.")
            return
        bit_num = self.read_bit_num_var.get()
        bit_value = read_digital_bit(self.board_num, self.digital_input_port, bit_num)
        if bit_value is not None:
            self.bit_value_label.config(text=f"Bit Value: {bit_value}")
            self.log(f"Read bit {bit_num} of port {self.digital_input_port.name}: {bit_value}")

    def create_log_area(self):
        log_frame = ttk.LabelFrame(self.master, text="Log", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        self.log_text = tk.Text(log_frame, height=10, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = CombinedInOut(root)
    root.mainloop()