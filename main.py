import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Combobox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# Scheduling functions
def fcfs(processes):
    processes.sort(key=lambda x: x['arrival_time'])
    timeline = []
    current_time = 0

    for process in processes:
        if current_time < process['arrival_time']:
            current_time = process['arrival_time']
        start_time = current_time
        end_time = current_time + process['cpu_cycle']
        timeline.append({'name': process['name'], 'start': start_time, 'end': end_time})
        current_time = end_time
    return timeline


# Gantt chart display
def display_gantt_chart(timeline, canvas_frame):
    # Clear any existing chart
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    # Create a new matplotlib figure
    fig, ax = plt.subplots(figsize=(8, 3))

    # Use different colors for each process
    colors = list(mcolors.TABLEAU_COLORS.values())
    max_time = max(job['end'] for job in timeline)  # Dynamic max time

    for i, job in enumerate(timeline):
        color = colors[i % len(colors)]
        ax.broken_barh([(job['start'], job['end'] - job['start'])], (10, 9),
                       facecolors=color)
        ax.text((job['start'] + job['end']) / 2, 15, job['name'], color='white', ha='center', va='center')

    ax.set_ylim(5, 25)
    ax.set_xlim(0, max_time)  # Use max time
    ax.set_xticks(range(0, max_time + 1))  # Whole numbers only
    ax.set_xlabel('Time')
    ax.set_yticks([])  # Hide Y-axis ticks

    # Embed the chart in the tkinter window
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    canvas.draw()


# Generate schedule
def generate_schedule():
    try:
        processes = []
        for i in range(5):
            name = entries[i][0].get()
            if not name:
                continue
            arrival_time = int(entries[i][1].get())
            cpu_cycle = int(entries[i][2].get())
            processes.append({'name': name, 'arrival_time': arrival_time, 'cpu_cycle': cpu_cycle})

        algorithm = algo_selection.get()
        if not processes:
            raise ValueError("Please enter at least one process.")

        if algorithm == "FCFS":
            timeline = fcfs(processes)
        elif algorithm == "SJN":
            # Call SJN logic
            raise NotImplementedError("SJN logic not implemented yet.")
        elif algorithm == "SRT":
            # Call SRT logic
            raise NotImplementedError("SRT logic not implemented yet.")
        elif algorithm == "Round Robin":
            time_quantum = int(time_quantum_entry.get())
            # Call Round Robin logic
            raise NotImplementedError("Round Robin logic not implemented yet.")
        else:
            raise ValueError("Select a valid scheduling algorithm.")

        display_gantt_chart(timeline, canvas_frame)
    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI setup
root = tk.Tk()
root.title("Process Scheduling")

# Add labels for inputs
tk.Label(root, text="Process Name").grid(row=0, column=1, padx=5, pady=5)
tk.Label(root, text="Arrival Time").grid(row=0, column=2, padx=5, pady=5)
tk.Label(root, text="CPU Cycle").grid(row=0, column=3, padx=5, pady=5)

# Input fields
entries = []
for i in range(5):
    tk.Label(root, text=f"Process {i+1}:").grid(row=i + 1, column=0, padx=5, pady=5)
    process_name = tk.Entry(root, width=10)
    process_name.grid(row=i + 1, column=1, padx=5, pady=5)
    arrival_time = tk.Entry(root, width=10)
    arrival_time.grid(row=i + 1, column=2, padx=5, pady=5)
    cpu_cycle = tk.Entry(root, width=10)
    cpu_cycle.grid(row=i + 1, column=3, padx=5, pady=5)
    entries.append((process_name, arrival_time, cpu_cycle))

# Dropdown for algorithm selection
tk.Label(root, text="Algorithm:").grid(row=6, column=0, padx=5, pady=5)
algo_selection = Combobox(root, values=["FCFS", "SJN", "SRT", "Round Robin"], state="readonly")
algo_selection.grid(row=6, column=1, padx=5, pady=5)

# Input for Round Robin time quantum
tk.Label(root, text="Time Quantum (RR):").grid(row=7, column=0, padx=5, pady=5)
time_quantum_entry = tk.Entry(root, width=10)
time_quantum_entry.grid(row=7, column=1, padx=5, pady=5)

# Generate schedule button
tk.Button(root, text="Generate Schedule", command=generate_schedule).grid(row=8, column=0, columnspan=4, pady=10)

# Frame for embedding the Gantt chart
canvas_frame = tk.Frame(root, width=800, height=300)
canvas_frame.grid(row=9, column=0, columnspan=4, padx=10, pady=10)

root.mainloop()
