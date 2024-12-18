import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm
import random
import time
import threading

class DilutionRefrigeratorVisualizer:
    def __init__(self, master):
        self.master = master
        self.master.title("Dilution Refrigerator Visualizer - Optimized Edition")
        self.master.geometry("1600x900")
        self.master.configure(bg='black')

        # Create a matplotlib figure
        self.fig = Figure(figsize=(10, 8), facecolor='black')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('black')
        self.ax.grid(False)
        self.ax.axis('off')

        # Initialize parameters
        self.current_stage = 0
        self.is_running = False
        self.stages = [
            {'name': 'Pre-cool', 'duration': 5, 'color': 'cyan', 'temp': 77},
            {'name': 'Cooldown', 'duration': 5, 'color': 'blue', 'temp': 4},
            {'name': 'Circulation', 'duration': 5, 'color': 'purple', 'temp': 0.9},
            {'name': 'Condensation', 'duration': 5, 'color': 'green', 'temp': 0.5},
            {'name': 'Mixing Chamber', 'duration': 5, 'color': 'yellow', 'temp': 0.02},
            {'name': 'Base Temperature', 'duration': 5, 'color': 'red', 'temp': 0.01},
            {'name': 'Axion Detection', 'duration': 10, 'color': 'magenta', 'temp': 0.001}
        ]

        # Simulated temperature data
        self.temperature = 300  # Start at room temperature (K)
        self.temperature_data = []
        self.time_data = []
        self.dark_matter_events = []

        # Create GUI components
        self.create_widgets()
        self.create_visualization()
        self.init_plot()

    def create_widgets(self):
        # Control frame
        control_frame = tk.Frame(self.master, bg='black')
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)

        # Title label
        title_label = tk.Label(
            control_frame, text="Dilution Refrigerator Simulator",
            fg='white', bg='black', font=('Helvetica', 24, 'bold')
        )
        title_label.pack(pady=20)

        # Start button
        self.start_button = tk.Button(
            control_frame, text="Start Simulation", command=self.start_sequence,
            fg='white', bg='green', font=('Helvetica', 16), width=20
        )
        self.start_button.pack(pady=20)

        # Temperature display
        self.temp_label = tk.Label(
            control_frame, text=f"Temperature: {self.temperature:.3f} K",
            fg='white', bg='black', font=('Helvetica', 18)
        )
        self.temp_label.pack(pady=10)

        # Stage labels
        self.stage_labels = []
        for stage in self.stages:
            label = tk.Label(
                control_frame, text=f"{stage['name']}: Pending",
                fg='white', bg='black', font=('Helvetica', 14), anchor='w'
            )
            label.pack(pady=5, fill=tk.X)
            self.stage_labels.append(label)

        # Progress bar
        self.progress = ttk.Progressbar(
            control_frame, orient='horizontal', length=250, mode='determinate'
        )
        self.progress.pack(pady=20)
        self.progress['maximum'] = len(self.stages)

        # Canvas for matplotlib figure
        canvas_frame = tk.Frame(self.master, bg='black')
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Plot frame
        plot_frame = tk.Frame(self.master, bg='black')
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Temperature plot
        self.figure_plot = Figure(figsize=(5, 4), facecolor='black')
        self.ax_plot = self.figure_plot.add_subplot(111)
        self.ax_plot.set_facecolor('black')
        self.ax_plot.tick_params(colors='white')
        self.ax_plot.spines['bottom'].set_color('white')
        self.ax_plot.spines['top'].set_color('white')
        self.ax_plot.spines['left'].set_color('white')
        self.ax_plot.spines['right'].set_color('white')
        self.ax_plot.set_xlabel('Time (s)', color='white')
        self.ax_plot.set_ylabel('Temperature (K)', color='white')
        self.line_plot, = self.ax_plot.plot([], [], color='cyan', linewidth=2)
        self.ax_plot.grid(True, color='gray')

        self.canvas_plot = FigureCanvasTkAgg(self.figure_plot, master=plot_frame)
        self.canvas_plot.draw()
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Event log
        self.log_frame = tk.Frame(plot_frame, bg='black')
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_label = tk.Label(
            self.log_frame, text="Event Log:",
            fg='white', bg='black', font=('Helvetica', 16)
        )
        self.log_label.pack(pady=5)
        self.log_text = tk.Text(
            self.log_frame, height=10, fg='white', bg='black',
            font=('Helvetica', 12), wrap='word', state='disabled'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def create_visualization(self):
        # Create a 3D model of a dilution refrigerator
        self.draw_refrigerator()

        # Initialize animation with blitting
        self.ani = animation.FuncAnimation(
            self.fig, self.animate, frames=360, interval=100, blit=True, cache_frame_data=False
        )

    def draw_refrigerator(self):
        # Clear the axes
        self.ax.clear()
        self.ax.set_facecolor('black')
        self.ax.axis('off')

        # Define stages with positions and radii
        self.stage_params = [
            {'z': 9, 'h': 1.5, 'r': 0.5},
            {'z': 7.5, 'h': 1.5, 'r': 0.45},
            {'z': 6, 'h': 1.5, 'r': 0.4},
            {'z': 4.5, 'h': 1.5, 'r': 0.35},
            {'z': 3, 'h': 1.5, 'r': 0.3},
            {'z': 1.5, 'h': 1.5, 'r': 0.25},
            {'z': 0, 'h': 1.5, 'r': 0.2}
        ]

        # Draw outer vacuum chamber
        self.vacuum_chamber = self.draw_cylinder(z_start=0, height=12, radius=0.6, color='silver', alpha=0.1)

        # Draw stages
        self.stage_artists = []
        for i, params in enumerate(self.stage_params):
            color = self.stages[i]['color']
            artist = self.draw_cylinder(
                z_start=params['z'], height=params['h'], radius=params['r'],
                color=color, alpha=0.3
            )
            self.stage_artists.append(artist)

        # Add labels to stages
        for i, params in enumerate(self.stage_params):
            self.ax.text(
                0, 0, params['z'] + params['h'] / 2,
                self.stages[i]['name'], color='white', fontsize=10,
                ha='center', va='center'
            )

        # Set limits and view angle
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(0, 12)
        self.ax.view_init(elev=20., azim=30)

    def draw_cylinder(self, z_start, height, radius, color, alpha):
        # Use a lower resolution for the mesh to improve performance
        z = np.linspace(z_start, z_start + height, 20)
        theta = np.linspace(0, 2 * np.pi, 20)
        theta_grid, z_grid = np.meshgrid(theta, z)
        x_grid = radius * np.cos(theta_grid)
        y_grid = radius * np.sin(theta_grid)
        surface = self.ax.plot_surface(
            x_grid, y_grid, z_grid, color=color, alpha=alpha, linewidth=0, antialiased=False
        )
        return surface

    def start_sequence(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(text="Stop Simulation", bg='red')
            self.current_stage = 0
            self.reset_stages()
            self.run_stage()
        else:
            self.is_running = False
            self.start_button.config(text="Start Simulation", bg='green')
            self.reset_stages()

    def run_stage(self):
        if self.is_running and self.current_stage < len(self.stages):
            stage = self.stages[self.current_stage]
            # Update stage label
            self.stage_labels[self.current_stage].config(
                text=f"{stage['name']}: Running", fg=stage['color']
            )
            # Update visualization
            self.highlight_stage(self.current_stage)
            # Simulate temperature change
            self.simulate_temperature(stage)
            # For the "Dark Matter Detection" stage, start event simulation
            if stage['name'] == 'Dark Matter Detection':
                self.simulate_dark_matter_events(stage['duration'])
            # Schedule next stage
            self.master.after(
                stage['duration'] * 1000, self.finish_stage
            )
        else:
            self.is_running = False
            self.start_button.config(text="Start Simulation", bg='green')

    def finish_stage(self):
        # Update stage label
        stage = self.stages[self.current_stage]
        self.stage_labels[self.current_stage].config(
            text=f"{stage['name']}: Completed", fg='white'
        )
        # Update progress bar
        self.current_stage += 1
        self.progress['value'] = self.current_stage
        self.run_stage()

    def reset_stages(self):
        for label in self.stage_labels:
            label.config(text=label.cget('text').split(':')[0] + ": Pending", fg='white')
        self.progress['value'] = 0
        self.temperature = 300  # Reset temperature
        self.temperature_data = []
        self.time_data = []
        self.dark_matter_events = []
        self.update_temperature_display()
        self.draw_refrigerator()
        self.canvas.draw()
        self.init_plot()
        self.clear_log()

    def highlight_stage(self, stage_index):
        # Redraw refrigerator with highlighted stage
        self.draw_refrigerator()
        # Highlight current stage
        artist = self.stage_artists[stage_index]
        artist.remove()
        params = self.stage_params[stage_index]
        color = self.stages[stage_index]['color']
        artist = self.draw_cylinder(
            z_start=params['z'], height=params['h'], radius=params['r'],
            color=color, alpha=0.9
        )
        self.stage_artists[stage_index] = artist
        self.canvas.draw()

    def animate(self, i):
        # Rotate the view
        self.ax.view_init(elev=20., azim=(30 + i) % 360)
        # Return a list of artists that have changed
        return [self.ax]

    def simulate_temperature(self, stage):
        # Simulate temperature change during the stage
        duration = stage['duration']
        temp_target = stage['temp']
        temp_start = self.temperature
        temp_diff = temp_target - temp_start
        steps = duration * 10  # Update 10 times per second
        temp_step = temp_diff / steps

        def update_temp(step=0):
            if step <= steps and self.is_running and self.current_stage < len(self.stages):
                self.temperature += temp_step
                self.temperature_data.append(self.temperature)
                self.time_data.append(len(self.temperature_data) / 10)
                self.update_temperature_display()
                self.update_plot()
                self.master.after(100, update_temp, step + 1)

        update_temp()

    def update_temperature_display(self):
        self.temp_label.config(text=f"Temperature: {self.temperature:.3f} K")

    def init_plot(self):
        self.ax_plot.clear()
        self.ax_plot.set_facecolor('black')
        self.ax_plot.tick_params(colors='white')
        self.ax_plot.spines['bottom'].set_color('white')
        self.ax_plot.spines['top'].set_color('white')
        self.ax_plot.spines['left'].set_color('white')
        self.ax_plot.spines['right'].set_color('white')
        self.ax_plot.set_xlabel('Time (s)', color='white')
        self.ax_plot.set_ylabel('Temperature (K)', color='white')
        self.line_plot, = self.ax_plot.plot([], [], color='cyan', linewidth=2)
        self.ax_plot.grid(True, color='gray')
        self.canvas_plot.draw()

    def update_plot(self):
        if self.time_data:
            self.line_plot.set_data(self.time_data, self.temperature_data)
            self.ax_plot.relim()
            self.ax_plot.autoscale_view()
            self.canvas_plot.draw()

    def simulate_dark_matter_events(self, duration):
        # Simulate random dark matter detection events
        self.event_running = True
        def generate_events():
            start_time = time.time()
            while time.time() - start_time < duration and self.event_running:
                time.sleep(random.uniform(1.0, 2.0))  # Less frequent events
                event_energy = random.uniform(1, 10)  # Energy in keV
                event_time = time.time() - start_time
                self.dark_matter_events.append((event_time, event_energy))
                self.log_event(event_time, event_energy)
                self.draw_event()
        threading.Thread(target=generate_events).start()

    def draw_event(self):
        # Visual representation of a dark matter event
        x = random.uniform(-0.1, 0.1)
        y = random.uniform(-0.1, 0.1)
        z = random.uniform(0, 1.5)
        self.ax.scatter(x, y, z, color='magenta', s=50, marker='*')
        self.canvas.draw()

    def log_event(self, event_time, event_energy):
        # Log the event in the text widget
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, f"Time: {event_time:.2f}s, Energy: {event_energy:.2f} keV\n")
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)

    def clear_log(self):
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = DilutionRefrigeratorVisualizer(root)
    root.mainloop()
