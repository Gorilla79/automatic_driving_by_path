import os
import json
import socket
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.interpolate import splprep, splev
from matplotlib.patches import Circle
from threading import Thread
import tkinter as tk

# File path for the map CSV
grid_file_path = r"D:\capstone\24_12_13\415insdie_grid_test_size_min.csv"

# Socket configuration
local_ip = "0.0.0.0"  # PC IP
local_port = 5000  # PC listening port
robot_ip = "192.168.0.9"  # Robot's IP address
robot_port = 5001  # Robot's listening port

# Global variables
robot_position = {"x": 0.0, "y": 0.0, "theta": 0.0}
drawn_path_points = []
stop_signal = False


def udp_listener():
    """Receive position updates from the robot."""
    global robot_position
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((local_ip, local_port))
    print("Listening for robot updates...")

    buffer = b""
    try:
        while not stop_signal:
            data, _ = sock.recvfrom(1024)
            buffer += data
            try:
                # Attempt to decode JSON
                robot_position = json.loads(buffer.decode())
                buffer = b""  # Clear buffer on successful decode
                print(f"Robot position updated: {robot_position}")
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Error receiving data: {e}")
    finally:
        sock.close()


def inflate_obstacles(grid, car_size):
    """Inflate obstacles to account for car size."""
    structure = np.ones(car_size)
    inflated_grid = binary_dilation(grid == 0, structure=structure).astype(int)
    return 1 - inflated_grid


def smooth_drawn_path(points):
    """Smooth the drawn path."""
    if len(points) < 3:
        return points
    points = np.array(points)
    x, y = points[:, 0], points[:, 1]
    tck, _ = splprep([x, y], s=5)
    u_fine = np.linspace(0, 1, len(x) * 10)
    x_smooth, y_smooth = splev(u_fine, tck)
    return list(zip(x_smooth, y_smooth))


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


def draw_map_with_gui():
    """Draw the map, robot's position, and interactive GUI."""
    global drawn_path_points, robot_position

    # Load the grid data
    grid_data = pd.read_csv(grid_file_path, header=None).to_numpy()
    car_size = (6, 6)
    inflated_grid = inflate_obstacles(grid_data, car_size)

    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(grid_data, cmap="gray", origin="upper")
    ax.set_title("Robot Path Planning")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # GUI for control
    root = tk.Tk()
    root.title("Robot Control")

    tk.Label(root, text="Robot X:").grid(row=0, column=0)
    tk.Label(root, text="Robot Y:").grid(row=1, column=0)

    robot_x_label = tk.Label(root, text="0.0")
    robot_y_label = tk.Label(root, text="0.0")
    robot_x_label.grid(row=0, column=1)
    robot_y_label.grid(row=1, column=1)

    def update_gui():
        while not stop_signal:
            robot_x_label.config(text=f"{robot_position['x']:.2f}")
            robot_y_label.config(text=f"{robot_position['y']:.2f}")
            time.sleep(0.1)

    Thread(target=update_gui, daemon=True).start()

    def on_mouse_click(event):
        """Capture mouse click for path drawing."""
        if event.xdata and event.ydata:
            drawn_path_points.append((event.xdata, event.ydata))
            ax.plot(event.xdata, event.ydata, 'ro', markersize=2)
            plt.draw()

    def draw_path():
        """Process the drawn path and send to robot."""
        if len(drawn_path_points) < 2:
            print("Draw a valid path with at least two points.")
            return
        smoothed_path = smooth_drawn_path(drawn_path_points)
        ax.plot(*zip(*smoothed_path), 'b-', linewidth=2)
        plt.draw()
        send_route_to_robot(smoothed_path)

    def stop_robot():
        """Stop the robot."""
        global stop_signal
        stop_signal = True
        root.destroy()

    tk.Button(root, text="Draw Path", command=draw_path).grid(row=2, column=0, columnspan=2)
    tk.Button(root, text="Stop Robot", command=stop_robot).grid(row=3, column=0, columnspan=2)

    fig.canvas.mpl_connect("button_press_event", on_mouse_click)
    plt.show()
    root.mainloop()


if __name__ == "__main__":
    Thread(target=udp_listener, daemon=True).start()
    draw_map_with_gui()