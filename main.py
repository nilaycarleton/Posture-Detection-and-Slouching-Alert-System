import cv2
import mediapipe as mp
import numpy as np
import ctypes
import time
import pygame
import os
import csv
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load the shared library
lib_path = os.path.join(os.path.dirname(__file__), 'libdistance.so')
lib = ctypes.CDLL(lib_path)

# Specify the argument types and the return type
lib.calculate_distance.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
lib.calculate_distance.restype = ctypes.c_double

lib.is_slouching.argtypes = [ctypes.c_double, ctypes.c_double]
lib.is_slouching.restype = ctypes.c_bool

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

pygame.mixer.init()
warning_sound = pygame.mixer.Sound('warning.wav')

cap = cv2.VideoCapture(0)
start_time = None

# Initialize CSV file for logging data
csv_file_path = 'posture_data.csv'
fieldnames = ['timestamp', 'distance', 'slouching']

if not os.path.exists(csv_file_path):
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

# Real-time plot setup
fig, ax = plt.subplots()
plt.ion()

def update_plot():
    data = pd.read_csv(csv_file_path)
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data.set_index('timestamp', inplace=True)
    ax.clear()
    ax.plot(data.index, data['distance'], '-b', label='Distance')
    ax.scatter(data.index, data['slouching'] * data['distance'], color='red', marker='x', label='Slouching')
    plt.xlabel('Time')
    plt.ylabel('Distance / Slouching')
    plt.title('Posture Data Over Time')
    plt.legend()
    plt.draw()

# Open the webcam and start processing
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Ignoring empty camera frame.")
            continue

        image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            left_shoulder_z = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].z
            right_shoulder_z = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].z
            left_hip_z = landmarks[mp_pose.PoseLandmark.LEFT_HIP].z
            right_hip_z = landmarks[mp_pose.PoseLandmark.RIGHT_HIP].z
            mid_hip_z = (left_hip_z + right_hip_z) / 2
            left_elbow_z = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].z
            right_elbow_z = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].z

            # Calculate average distance of elbows and mid_hip to shoulders
            distance_shoulder_elbow = lib.calculate_distance(left_shoulder_z, right_shoulder_z, left_elbow_z, right_elbow_z)
            distance_shoulder_hip = lib.calculate_distance(left_shoulder_z, right_shoulder_z, left_hip_z, right_hip_z)
            distance_shoulder_mid_hip = lib.calculate_distance(left_shoulder_z, right_shoulder_z, mid_hip_z, mid_hip_z)

            # Average distance as an indicator
            distance = (distance_shoulder_elbow + distance_shoulder_hip + distance_shoulder_mid_hip) / 3
            threshold = 0.50  # Adjust threshold as needed

            slouching = lib.is_slouching(distance, threshold)
            current_time = time.time()

            if slouching:
                if start_time is None:
                    start_time = current_time
                elif current_time - start_time > 60:
                    cv2.rectangle(image, (0, 0), (image.shape[1], image.shape[0]), (0, 255, 255), 10)
                    if current_time - start_time > 120:
                        warning_sound.play()
                        cv2.rectangle(image, (0, 0), (image.shape[1], image.shape[0]), (0, 0, 255), 10)
                        cv2.putText(image, 'Try to develop postural awareness', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        cv2.putText(image, 'Adjust your desk, chair and computer screen', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                if start_time is not None and current_time - start_time < 30:
                    start_time = None
                elif start_time is None:
                    cv2.rectangle(image, (0, 0), (image.shape[1], image.shape[0]), (0, 255, 0), 10)

            cv2.putText(image, f'Distance: {distance:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            heatmap = np.zeros_like(image)
            for landmark in results.pose_landmarks.landmark:
                x, y = int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])
                cv2.circle(heatmap, (x, y), 5, (0, 0, 255), -1)
            heatmap = cv2.addWeighted(image, 0.7, heatmap, 0.3, 0)

            # Log the data
            timestamp = datetime.datetime.now().isoformat()
            with open(csv_file_path, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({'timestamp': timestamp, 'distance': distance, 'slouching': slouching})

            update_plot()  # Update the plot after logging new data
                
            cv2.imshow('MediaPipe Pose with Heatmap', heatmap)
            plt.pause(0.001)  # Allow the plot to update

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()
