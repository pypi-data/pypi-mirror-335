import numpy as np
import pandas as pd
from .utils import mean_orientation
import numpy as np
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp
from scipy.interpolate import CubicSpline
import quaternion
class DataSynchronizer:
    def __init__(self, sensor_tandem):
        """
        Initialize with two time series data sets
        
        Parameters:
        thigh_time (array-like): Time array for thigh data
        thigh_data (array-like): Data values for thigh
        shank_time (array-like): Time array for shank data
        shank_data (array-like): Data values for shank
        """
        self.thigh_orientation_time = np.array(sensor_tandem.thigh_sensor.sensor_orientation.time_arr)
        self.shank_orientation_time = np.array(sensor_tandem.shank_sensor.sensor_orientation.time_arr)
        self.thigh_acceleration_time = np.array(sensor_tandem.thigh_sensor.x_acceleration.time_arr)
        self.shank_acceleration_time = np.array(sensor_tandem.shank_sensor.x_acceleration.time_arr)
        self.thigh_orientation = np.array(sensor_tandem.thigh_sensor.sensor_orientation.data)
        self.thigh_x_acceleration = np.array(sensor_tandem.thigh_sensor.x_acceleration.data)
        self.thigh_y_acceleration = np.array(sensor_tandem.thigh_sensor.y_acceleration.data)
        self.thigh_z_acceleration = np.array(sensor_tandem.thigh_sensor.z_acceleration.data)
        self.shank_orientation = np.array(sensor_tandem.shank_sensor.sensor_orientation.data)
        self.shank_x_acceleration = np.array(sensor_tandem.shank_sensor.x_acceleration.data)
        self.shank_y_acceleration = np.array(sensor_tandem.shank_sensor.y_acceleration.data)
        self.shank_z_acceleration = np.array(sensor_tandem.shank_sensor.z_acceleration.data)

        

    def sync_by_interpolation(self):
        """
        Synchronize data using interpolation to align to unified time points
        
        Parameters:
        unified_time (array-like, optional): Unified time array. If None, will be created.
        
        Returns:
        tuple: (unified_time, synchronized_thigh_data, synchronized_shank_data)
        """


        unified_time = np.union1d(np.concatenate([self.thigh_acceleration_time,self.shank_acceleration_time]),np.concatenate([self.thigh_orientation_time,self.shank_orientation_time]))
        unified_time = unified_time[unified_time != 0]


        # first - build a map for epochs to index
        time_index_map = self.build_time_to_index_map(unified_time=unified_time)
       # second - instantiate two lists of size unified time
        
            # 3 - being to populate each list, if multiple of same epoch, average values, if missing put a NaN
        populated_thigh_orientation = self.populate_synced_list(data=self.thigh_orientation, time=self.thigh_orientation_time,
                                                                unified_time=unified_time, time_index_map=time_index_map,
                                                                data_type="orientation")
        populated_thigh_x_acceleration = self.populate_synced_list(data=self.thigh_x_acceleration, time=self.thigh_acceleration_time,
                                                                unified_time=unified_time, time_index_map=time_index_map,
                                                                data_type="acceleration")
        #update rest of times according to pattern above
        populated_thigh_y_acceleration = self.populate_synced_list(data=self.thigh_y_acceleration, time=self.thigh_acceleration_time,
                                                                unified_time=unified_time, time_index_map=time_index_map,
                                                                data_type="acceleration")
        populated_thigh_z_acceleration = self.populate_synced_list(data=self.thigh_z_acceleration, time=self.thigh_acceleration_time,
                                                                unified_time=unified_time, time_index_map=time_index_map,
                                                                data_type="acceleration")
        populated_shank_orientation = self.populate_synced_list(data=self.shank_orientation, time=self.shank_orientation_time,
                                                                unified_time=unified_time, time_index_map=time_index_map,
                                                                data_type="orientation")
        populated_shank_x_acceleration = self.populate_synced_list(data=self.shank_x_acceleration, time=self.shank_acceleration_time,
                                                                unified_time=unified_time, time_index_map=time_index_map,
                                                                data_type="acceleration")
        populated_shank_y_acceleration = self.populate_synced_list(data=self.shank_y_acceleration, time=self.shank_acceleration_time,
                                                                unified_time=unified_time, time_index_map=time_index_map,
                                                                data_type="acceleration")
        populated_shank_z_acceleration = self.populate_synced_list(data=self.shank_z_acceleration, time=self.shank_acceleration_time,
                                                                unified_time=unified_time, time_index_map=time_index_map,
                                                                data_type="acceleration")

        # Create a dictionary to store the data and their types
        data_dict = {
            "thigh_orientation": {"data": populated_thigh_orientation, "type": "orientation"},
            "thigh_x_acceleration": {"data": populated_thigh_x_acceleration, "type": "acceleration"},
            "thigh_y_acceleration": {"data": populated_thigh_y_acceleration, "type": "acceleration"},
            "thigh_z_acceleration": {"data": populated_thigh_z_acceleration, "type": "acceleration"},
            "shank_orientation": {"data": populated_shank_orientation, "type": "orientation"},
            "shank_x_acceleration": {"data": populated_shank_x_acceleration, "type": "acceleration"},
            "shank_y_acceleration": {"data": populated_shank_y_acceleration, "type": "acceleration"},
            "shank_z_acceleration": {"data": populated_shank_z_acceleration, "type": "acceleration"}
        }

        # Interpolate gaps for each data type and store the results
        interpolated_data = {}
        for key, value in data_dict.items():
            interpolated_data[key] = self.interpolate_gaps(value["data"], value["type"])

        # Add unified time to the result dictionary
        interpolated_data["unified_time"] = unified_time
        return interpolated_data


    def build_time_to_index_map(self, unified_time) -> dict:
        time_index_map = {}
        for index,time in enumerate(unified_time):
            time_index_map[time] = index 
        
        return time_index_map

    def populate_synced_list(self,data, time, unified_time, time_index_map,data_type):

        if data_type=='orientation':
            final_array = np.full(unified_time.shape, np.nan,dtype=np.quaternion)
        else:
            final_array = np.full(unified_time.shape, np.nan)


        i = 0
        while i < len(time):
            start = i
            vals = []

            # Collect all values corresponding to the same timestamp
            while i < len(time) and time[i] == time[start]:
                vals.append(data[i])
                i += 1
            
            # Compute mean and assign to the correct index
            if data_type=="orientation":
                mean_val = mean_orientation(vals)
            else:
                mean_val = np.mean(vals)
            if not time[start] == 0:
                final_array[time_index_map[time[start]]] = mean_val

        return final_array


    def interpolate_gaps(self,data,data_type):
        """
        Interpolates NaN values in an array of quaternions using SLERP.

        Parameters:
            quaternions (ndarray): Nx4 array of quaternions (w, x, y, z).
            window_size (int): The number of neighboring valid quaternions to consider.

        Returns:
            ndarray: The quaternion array with NaNs filled using SLERP.
        """
        if data_type== 'orientation':
            valid_mask = np.all(~np.isnan(quaternion.as_float_array(quaternion.as_float_array(data))).any(axis=1),axis=1)

        else:
            valid_mask = ~np.isnan(quaternion.as_float_array(data)).any(axis=1)


        # Convert to Rotation objects for easier SLERP
        valid_indices = np.where(valid_mask)[0]

        filled_data= data.copy()
        for i in range(len(data)):
            if not valid_mask[i]:  # If current quaternion is NaN
                # Find closest valid quaternions
                left_idx = valid_indices[valid_indices < i][-1] if np.any(valid_indices < i) else None
                right_idx = valid_indices[valid_indices > i][0] if np.any(valid_indices > i) else None
                
                if left_idx is not None and right_idx is not None and data_type=="orientation":
                    # Get the valid quaternions
                    q1 = R.from_quat(quaternion.as_float_array(data[left_idx]))
                    q2 = R.from_quat(quaternion.as_float_array(data[right_idx]))
                    
                    # Create key times array based on indices
                    key_times = np.array([left_idx, right_idx])
                    
                    # Create Slerp object with the two rotations
                    slerper = Slerp(key_times, R.concatenate([q1, q2]))
                    
                    # Calculate interpolated quaternion at index i
                    # Normalize the position between left and right indices
                    interp_rotation = slerper([i])
                    
                    # Extract the interpolated quaternion
                    interp_data = quaternion.from_float_array(interp_rotation.as_quat()[0])
                elif left_idx is not None and right_idx is not None and data_type=="acceleration":
                                                    # Find additional points if available
                                    # For acceleration data, try to get more points for better interpolation
                    # Let's try to get up to 3 valid points on each side if available
                    
                    # Number of points to try to get on each side
                    num_points = 3
                    
                    # Get additional points on the left
                    left_points = []
                    current_idx = left_idx
                    for _ in range(num_points):
                        if current_idx is not None:
                            left_points.append(current_idx)
                            # Find the next valid index to the left
                            current_left = valid_indices[valid_indices < current_idx]
                            current_idx = current_left[-1] if len(current_left) > 0 else None
                        else:
                            break
                    
                    # Get additional points on the right
                    right_points = []
                    current_idx = right_idx
                    for _ in range(num_points):
                        if current_idx is not None:
                            right_points.append(current_idx)
                            # Find the next valid index to the right
                            current_right = valid_indices[valid_indices > current_idx]
                            current_idx = current_right[0] if len(current_right) > 0 else None
                        else:
                            break
                    
                    # Combine and sort all points
                    x_points = np.array(left_points[::-1] + right_points)
                    y_points = np.array([data[idx] for idx in x_points])
                    
                    # If we have at least 3 points, use cubic spline
                    if len(x_points) >= 3:
                        # Create a cubic spline interpolation
                        cs = CubicSpline(x_points, y_points)
                        
                        # Interpolate at index i
                        interp_data = cs(i)
                    else:
                        # Fall back to linear interpolation if we don't have enough points
                        t = (i - left_idx) / (right_idx - left_idx)
                        interp_data = (1 - t) * data[left_idx] + t * data[right_idx]
                        
                elif left_idx is not None:
                    # Only left valid quaternion exists
                    interp_data = data[left_idx]
                elif right_idx is not None:
                    # Only right valid quaternion exists
                    interp_data= data[right_idx]
                else:
                    raise("Error: No valid quaternion for interpolation, something went wrong :(")
                
                filled_data[i] = interp_data

        return filled_data