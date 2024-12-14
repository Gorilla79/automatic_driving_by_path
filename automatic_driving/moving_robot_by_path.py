import socket
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import tkinter as tk
from tkinter import ttk
import threading

# File path for the map CSV
grid_file_path = r"D:\capstone\24_12_13\415insdie_grid_test_size_min.csv"

# Socket configuration
local_ip = "0.0.0.0"
local_port = 5000
robot_ip = "192.168.0.9"  # Robot's IP address
robot_port = 5001

# Global variables
robot_position = None
robot_orientation = None
route_points = []
stop_signal = False

# UDP listener thread function
def udp_listener():
    """Thread to listen for robot position updates."""
    global robot_position, robot_orientation
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((local_ip, local_port))

    print("Listening for robot updates...")
    while not stop_signal:
        try:
            data, _ = sock.recvfrom(1024)
            message = json.loads(data.decode())
            robot_position = (message["x"], message["y"])
            robot_orientation = message["theta"]
            print(f"Robot position updated: {robot_position}, orientation: {robot_orientation:.2f}")
        except Exception as e:
            print(f"Error receiving data: {e}")
    sock.close()

# Send the route to the robot
def send_route_to_robot(route):
    """Send the planned route to the robot."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        message = {"command": "start_route", "route": route}
        sock.sendto(json.dumps(message).encode(), (robot_ip, robot_port))
        print("Route sent to robot.")
    except Exception as e:
        print(f"Error sending route: {e}")
    finally:
        sock.close()

# Send stop signal to the robot
def send_stop_signal():
    """Send an emergency stop signal to the robot."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        message = {"command": "stop"}
        sock.sendto(json.dumps(message).encode(), (robot_ip, robot_port))
        print("Stop signal sent to robot.")
    except Exception as e:
        print(f"Error sending stop signal: {e}")
    finally:
        sock.close()

# Tkinter GUI and Matplotlib integration
class RobotControlInterface:
    def __init__(self, root):
        global route_points
        self.root = root
        self.root.title("Robot Control Interface")
        self.route_points = route_points
        self.initialize_ui()

        # Matplotlib figure
        self.grid_data = np.loadtxt(grid_file_path, delimiter=",")
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.imshow(self.grid_data, cmap="gray", origin="upper")
        self.ax.set_title("Robot Position and Route")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.route_line, = self.ax.plot([], [], "r-", linewidth=2, label="Route")
        self.robot_indicator = None

        # Timer-based update for Matplotlib
        self.update_plot()

    def initialize_ui(self):
        """Initialize the Tkinter UI."""
        frame = tk.Frame(self.root)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Input fields for route points
        tk.Label(frame, text="X Coordinate").grid(row=0, column=0)
        tk.Label(frame, text="Y Coordinate").grid(row=1, column=0)
        self.entry_x = tk.Entry(frame)
        self.entry_y = tk.Entry(frame)
        self.entry_x.grid(row=0, column=1)
        self.entry_y.grid(row=1, column=1)

        # Buttons
        ttk.Button(frame, text="Add Route Point", command=self.add_route_point).grid(row=2, column=0, columnspan=2)
        ttk.Button(frame, text="Send Route", command=self.send_route).grid(row=3, column=0, columnspan=2)
        ttk.Button(frame, text="Stop Robot", command=self.stop_robot).grid(row=4, column=0, columnspan=2)

    def add_route_point(self):
        """Add a route point by mouse click."""
        try:
            x = float(self.entry_x.get())
            y = float(self.entry_y.get())
            self.route_points.append((x, y))
            print(f"Added route point: {x}, {y}")
        except ValueError:
            print("Invalid input. Please enter numeric values.")

    def send_route(self):
        """Send the route to the robot."""
        send_route_to_robot(self.route_points)

    def stop_robot(self):
        """Send the stop signal to the robot."""
        global stop_signal
        send_stop_signal()
        stop_signal = True

    def update_plot(self):
        """Update the Matplotlib plot with robot position and route."""
        global robot_position

        if robot_position:
            # Update robot position
            if self.robot_indicator:
                self.robot_indicator.remove()
            self.robot_indicator = Circle(robot_position, radius=5, color="blue", label="Robot")
            self.ax.add_patch(self.robot_indicator)

        if self.route_points:
            # Update route
            route_np = np.array(self.route_points)
            self.route_line.set_data(route_np[:, 0], route_np[:, 1])

        self.fig.canvas.draw_idle()
        self.root.after(100, self.update_plot)  # Schedule the next update

# Main function
if __name__ == "__main__":
    # Start UDP listener
    threading.Thread(target=udp_listener, daemon=True).start()

    # Start Tkinter main loop
    root = tk.Tk()
    app = RobotControlInterface(root)
    root.mainloop()