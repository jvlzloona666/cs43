import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Combobox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import heapq  # For implementing SRT


# Scheduling Functions
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


def sjn(processes):
    processes.sort(key=lambda x: (x['arrival_time'], x['cpu_cycle']))
    timeline = []
    current_time = 0
    while processes:
        ready_queue = [p for p in processes if p['arrival_time'] <= current_time]
        if not ready_queue:
            current_time = min(processes, key=lambda x: x['arrival_time'])['arrival_time']
            continue
        shortest = min(ready_queue, key=lambda x: x['cpu_cycle'])
        processes.remove(shortest)
        start_time = current_time
        end_time = start_time + shortest['cpu_cycle']
        timeline.append({'name': shortest['name'], 'start': start_time, 'end': end_time})
        current_time = end_time
    return timeline


def srt(processes):
    timeline = []
    current_time = 0
    remaining_time = {p['name']: p['cpu_cycle'] for p in processes}
    ready_queue = []
    processes = sorted(processes, key=lambda x: x['arrival_time'])  # Ensure processes are sorted by arrival time

    last_process = None  # Track the last process to detect preemption

    while processes or ready_queue:
        # Add all processes that have arrived by `current_time` to the ready queue
        while processes and processes[0]['arrival_time'] <= current_time:
            process = processes.pop(0)
            heapq.heappush(ready_queue, (remaining_time[process['name']], process))

        if ready_queue:
            # Get the process with the shortest remaining time
            remaining, process = heapq.heappop(ready_queue)
            process_name = process['name']

            # Check if preemption occurred
            if last_process != process_name:
                if last_process:
                    # If a previous process was interrupted, record its time slice
                    timeline[-1]['end'] = current_time
                # Start a new time slice for the current process
                timeline.append({'name': process_name, 'start': current_time, 'end': None})
                last_process = process_name

            # Execute the process for 1 time unit
            remaining_time[process_name] -= 1
            current_time += 1

            # Check if the process is finished
            if remaining_time[process_name] == 0:
                # Complete the timeline entry for the finished process
                timeline[-1]['end'] = current_time
            else:
                # Push the process back with updated remaining time
                heapq.heappush(ready_queue, (remaining_time[process_name], process))
        else:
            # No process is ready, increment time
            current_time += 1

    return timeline



def round_robin(processes, quantum):
    timeline = []
    current_time = 0
    process_queue = [p for p in processes]
    while process_queue:
        process = process_queue.pop(0)
        remaining_time = process['cpu_cycle']
        if remaining_time > quantum:
            timeline.append({'name': process['name'], 'start': current_time, 'end': current_time + quantum})
            current_time += quantum
            process['cpu_cycle'] -= quantum
            process_queue.append(process)
        else:
            timeline.append({'name': process['name'], 'start': current_time, 'end': current_time + remaining_time})
            current_time += remaining_time
            process['cpu_cycle'] = 0
    return timeline


# Gantt chart display
# Gantt chart display
def display_gantt_chart(timeline, canvas_frame):
    # Clear any existing chart
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    # Create a new matplotlib figure with a larger size
    fig, ax = plt.subplots(figsize=(10, 4))  # Increase figure size

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
    ax.set_xlabel('Time', fontsize=12)  # Increase font size for the label
    ax.set_yticks([])  # Hide Y-axis ticks

    # Adjust layout to prevent labels from being cut off
    plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.15)  # Adjust margins

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
            timeline = sjn(processes)
        elif algorithm == "SRT":
            timeline = srt(processes)
        elif algorithm == "Round Robin":
            time_quantum = int(time_quantum_entry.get())
            timeline = round_robin(processes, time_quantum)
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

# First part of the text
tk.Label(root, text="Please input '0' in arrival times for FCFS and SJN.", 
         fg="blue").grid(row=10, column=0, columnspan=4, pady=5)

# Second part of the text
tk.Label(root, text="CS43 Project, Submitted by Josh Magdiel K. Villaluz", 
         fg="blue").grid(row=11, column=0, columnspan=4, pady=5)

# Frame for embedding the Gantt chart
canvas_frame = tk.Frame(root, width=800, height=300)
canvas_frame.grid(row=9, column=0, columnspan=4, padx=10, pady=10)

root.mainloop()
