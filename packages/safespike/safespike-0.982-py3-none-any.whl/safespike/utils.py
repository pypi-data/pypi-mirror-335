import numpy as np
import quaternion
import pandas as pd
from .sensor_data import SensorData
from typing import Dict 

def quaternions_to_euler(quaternions):
    roll = []
    pitch = []
    yaw = []
    
    for quat in quaternions:
        # Convert quaternion to rotation matrix, then to Euler angles
        euler_angles = quaternion.as_euler_angles(quat)
        roll.append(euler_angles[0])
        pitch.append(euler_angles[1])
        yaw.append(euler_angles[2])
    
    return np.array(roll), np.array(pitch), np.array(yaw)

def raw_to_sensor_data(orientation_file_path, vertical_acceleration_file_path):
    orientation_df = pd.read_csv(orientation_file_path)
    vertical_acceleration_df = pd.read_csv(vertical_acceleration_file_path)

    orientation = np.array([
        np.quaternion(row.W, row.X, row.Y, row.Z)
        for _, row in orientation_df.iterrows()
    ])

    vertical_acceleration = vertical_acceleration_df['Z'].values 
    orientation_epochs = orientation_df['Epoch'].values
    vertical_acceleration_epochs = vertical_acceleration_df['Epoch'].values
    orientation_data = SensorData(orientation, orientation_epochs)
    vertical_acceleration_data = SensorData(vertical_acceleration, vertical_acceleration_epochs)
    return orientation_data, vertical_acceleration_data

def mean_orientation(quaternions):
    """
    Compute the mean of a set of quaternions (geometric mean).
    quaternions: list or array of `quaternion.quaternion` objects.
    Returns: mean quaternion as a `quaternion.quaternion` object.
    """
    # Convert quaternions into a matrix (each quaternion as a row)
    Q = np.array([quaternion.as_float_array(q) for q in quaternions])  # w, x, y, z
    
    # Compute the covariance matrix (for quaternion rotations)
    M = np.dot(Q.T, Q)  # M is a 4x4 matrix
    
    # Perform eigenvalue decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(M)
    
    # The mean quaternion corresponds to the eigenvector with the largest eigenvalue
    largest_eigenvalue_index = np.argmax(eigenvalues)
    mean_quat = eigenvectors[:, largest_eigenvalue_index]
    # Create a quaternion from the eigenvector
    mean_quaternion = np.quaternion(mean_quat[0], mean_quat[1], mean_quat[2], mean_quat[3])
    
    # Normalize using quaternion's built-in normalization
    mean_quaternion = mean_quaternion.normalized()
    
    return mean_quaternion




def load_csv_files(file_mappings: Dict[str, str]) -> Dict[str, np.ndarray]:

    
    df_shin_quat = pd.read_csv(file_mappings["shin_quat"])
    df_shin_acc = pd.read_csv(file_mappings["shin_acc"])
    df_thigh_quat = pd.read_csv(file_mappings["thigh_quat"])
    df_thigh_acc = pd.read_csv(file_mappings["thigh_acc"])

    #convert quaternions from csv into array
    shin_orientation = np.array([
    np.quaternion(row.w, row.x, row.y, row.z)
    for _, row in df_shin_quat.iterrows()
    ])

    thigh_orientation = np.array([
    np.quaternion(row.w, row.x, row.y, row.z)
    for _, row in df_thigh_quat.iterrows()
    ])


    # we use the .values attribute since that returns numpy array
    data_dict = {
        "shin_orientation" : shin_orientation,
        "shin_x_acc" : df_shin_acc.x.values,
        "shin_y_acc" : df_shin_acc.y.values,
        "shin_z_acc" : df_shin_acc.z.values,
        "shin_acc_epochs" : df_shin_acc.epoch.values,
        "shin_orientation_epochs" : df_shin_quat.epoch.values,

        "thigh_orientation" : thigh_orientation,
        "thigh_x_acc" : df_thigh_acc.x.values,
        "thigh_y_acc" : df_thigh_acc.y.values,
        "thigh_z_acc" : df_thigh_acc.z.values,
        "thigh_acc_epochs" : df_thigh_acc.epoch.values,
        "thigh_orientation_epochs": df_thigh_quat.epoch.values,
    }

    return data_dict



