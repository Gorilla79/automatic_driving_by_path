import socket
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import cos, sin, radians
from threading import Thread

# File path for the map CSV
CSV_FILE_PATH = r"D:\capstone\24_12_13\415insdie_grid_test_size_min.csv"

# UDP Configuration
LOCAL_IP = "0.0.0.0"  # PC IP
LOCAL_PORT = 5001  # Listening port

# Shared variables
lidar_data = None
lidar_lock = Thread()

def unpack_lidar_data(data):
    """Parse incoming LiDAR JSON data."""
    parsed_data = json.loads(data)
    angles = np.array(parsed_data["angles"])
    distances = np.array(parsed_data["distances"])
    return angles, distances

def lidar_receiver():
    """Receive LiDAR data from the robot."""
    global lidar_data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCAL_IP, LOCAL_PORT))
    print(f"Listening for LiDAR data on {LOCAL_IP}:{LOCAL_PORT}")

    while True:
        try:
            data, _ = sock.recvfrom(65536)
            with lidar_lock:
                lidar_data = unpack_lidar_data(data.decode())
        except Exception as e:
            print(f"Error receiving data: {e}")

def compare_with_csv(angles, distances, map_data):
    """Compare LiDAR data with map to estimate position and direction."""
    best_match_score = 0
    best_position = None

    for x in range(map_data.shape[0]):
        for y in range(map_data.shape[1]):
            if map_data[x, y] == 0:  # Only consider free space
                simulated_distances = []
                for angle in angles:
                    dx = int(x + distances * cos(angle))
                    dy = int(y + distances * sin(angle))
                    if 0 <= dx < map_data.shape[0] and 0 <= dy < map_data.shape[1]:
                        simulated_distances.append(map_data[dx, dy])
                score = np.mean([1 for a, b in zip(distances, simulated_distances) if abs(a - b) < 0.2])
                if score > best_match_score:
                    best_match_score = score
                    best_position = (x, y)

    return best_position if best_match_score > 0.8 else None

def visualize_lidar(map_data):
    """Visualize LiDAR data and estimated position."""
    global lidar_data

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(map_data, cmap='gray', origin='upper')

    def update(frame):
        with lidar_lock:
            if lidar_data:
                angles, distances = lidar_data
                lidar_points_x = distances * np.cos(np.radians(angles))
                lidar_points_y = distances * np.sin(np.radians(angles))

                ax.scatter(lidar_points_x, lidar_points_y, c='red', s=1)
                estimated_position = compare_with_csv(angles, distances, map_data)
                if estimated_position:
                    ax.scatter(estimated_position[0], estimated_position[1], c='blue', s=50, label="Estimated Position")
        plt.draw()

    ani = FuncAnimation(fig, update, interval=50)
    plt.show()


if __name__ == "__main__":
    # Load map data
    map_data = pd.read_csv(CSV_FILE_PATH, header=None).to_numpy()

    # Start LiDAR receiver thread
    Thread(target=lidar_receiver, daemon=True).start()

    # Visualize LiDAR and position
    visualize_lidar(map_data)