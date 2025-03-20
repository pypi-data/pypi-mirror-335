import numpy as np
import quaternion
from collections import defaultdict

from .sensor import Sensor
from .sensor_data import SensorData, ACLRiskEvent
from .utils import mean_orientation
from .data_synchronizer import DataSynchronizer

class SensorTandem:
    """Manages and synchronizes data from thigh and shank sensors."""
    
    def __init__(self, thigh_sensor: Sensor, shank_sensor: Sensor):
        """Initialize SensorTandem with thigh and shank sensors.
        
        Args:
            thigh_sensor: Sensor instance for thigh measurements
            shank_sensor: Sensor instance for shank measurements
        """
        self._thigh_sensor = thigh_sensor
        self._shank_sensor = shank_sensor
        self._thigh_time = thigh_sensor.sensor_orientation.time_arr
        self._shank_time = shank_sensor.sensor_orientation.time_arr
        self._synced = False
        self.sync_sensors()

    # Properties
    @property
    def thigh_sensor(self) -> Sensor:
        return self._thigh_sensor
    
    @thigh_sensor.setter
    def thigh_sensor(self, value: Sensor):
        if not isinstance(value, Sensor):
            raise TypeError("thigh_sensor must be an instance of Sensor")
        self._thigh_sensor = value
    
    @property
    def shank_sensor(self) -> Sensor:
        return self._shank_sensor
    
    @shank_sensor.setter
    def shank_sensor(self, value: Sensor):
        if not isinstance(value, Sensor):
            raise TypeError("shank_sensor must be an instance of Sensor")
        self._shank_sensor = value

    @property
    def synced(self) -> bool:
        return self._synced
    
    @synced.setter
    def synced(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("synced must be a boolean")
        self._synced = value
    
    @property
    def thigh_time(self):
        """Get the time array for the thigh sensor."""
        return self._thigh_time
    
    @thigh_time.setter
    def thigh_time(self, value):
        """Set the time array for the thigh sensor."""

        self._thigh_time = value

    @property
    def shank_time(self):
        """Get the time array for the shank sensor."""
        return self._shank_time
    
    @shank_time.setter
    def shank_time(self, value):
        """Set the time array for the shank sensor."""

        self._shank_time = value


    # Synchronization methods
    def sync_sensors(self):
        """
        Synchronize sensor readings between thigh and shank sensors based on a unified time array.

        The method creates synchronized `Sensor` objects for both the thigh and shank sensors with relative time (starting from 0).
        It also ensures that the data from the thigh and shank sensors have the same length and are properly aligned in time.

        """
        data_synchronizer = DataSynchronizer(self)

        interpolated_data_dict = data_synchronizer.sync_by_interpolation()
        # Convert to relative time (starting from 0)
        relative_time = interpolated_data_dict['unified_time'] - interpolated_data_dict['unified_time'][0]
        # Access the synced data
        synced_thigh_orient = interpolated_data_dict["thigh_orientation"]
        synced_thigh_x_accel = interpolated_data_dict["thigh_x_acceleration"]
        synced_thigh_y_accel = interpolated_data_dict["thigh_y_acceleration"]
        synced_thigh_z_accel = interpolated_data_dict["thigh_z_acceleration"]

        synced_shank_orient = interpolated_data_dict["shank_orientation"]
        synced_shank_x_accel = interpolated_data_dict["shank_x_acceleration"]
        synced_shank_y_accel = interpolated_data_dict["shank_y_acceleration"]
        synced_shank_z_accel = interpolated_data_dict["shank_z_acceleration"]

        # Create synchronized sensor objects with relative time and the proper arguments
        # Initialize shin sensor
        synced_shank= Sensor(
            sensor_orientation=synced_shank_orient,  # Synced data for shin sensor orientation
            x_acceleration=synced_shank_x_accel,     # Synced data for shin x acceleration
            y_acceleration=synced_shank_y_accel,     # Synced data for shin y acceleration
            z_acceleration=synced_shank_z_accel,     # Synced data for shin z acceleration
            acceleration_time_arr=relative_time,
            orientation_time_arr=relative_time               
        )

        # Initialize thigh sensor
        synced_thigh = Sensor(
            sensor_orientation=synced_thigh_orient,  # Synced data for thigh sensor orientation
            x_acceleration=synced_thigh_x_accel,     # Synced data for thigh x acceleration
            y_acceleration=synced_thigh_y_accel,     # Synced data for thigh y acceleration
            z_acceleration=synced_thigh_z_accel,     # Synced data for thigh z acceleration
            acceleration_time_arr=relative_time,
            orientation_time_arr=relative_time
        )
        self.thigh_time = relative_time
        self.shank_time = relative_time
        self.thigh_sensor = synced_thigh
        self.shank_sensor = synced_shank
        self.synced = True

    # Event detection methods
    def detect_jumps(self, jump_thresh: float, land_thresh: float, hang_time: float) -> defaultdict:
        """Detect jumping events in the sensor data."""
        mid_jump = False
        jump_counter = 0
        i = 0
        jumps = defaultdict(list)
        vertical_accelerations = self.shank_sensor.z_acceleration.data
        num_events = len(vertical_accelerations)
        
        while i < num_events:
            current_time = self._index_to_seconds(i)
            
            if vertical_accelerations[i] > jump_thresh and not mid_jump:
                jumps[jump_counter].append(current_time)  # Store the time directly
                mid_jump = True
                next_time = current_time + hang_time
                i = max(self._seconds_to_index(next_time), i+1)

            elif vertical_accelerations[i] < land_thresh and mid_jump:
                jumps[jump_counter].append(current_time)  # Store the time directly
                mid_jump = False
                next_time = current_time + hang_time
                i = max(self._seconds_to_index(next_time), i+1)
            else:
                i += 1
        return jumps

    def find_acl_risk(self, landing_time: float=0.02, flexion_threshold: float=25, rotation_threshold: float=4.5,
                      jump_thresh: float=1, land_thresh: float=-1, hang_time: float=0.53,angle_method:str='euler') -> list[ACLRiskEvent]:
        """Detect potential ACL risk events.
        
        Args:
            landing_time: Time window for landing analysis (seconds)
            flexion_threshold: Knee flexion threshold for risk detection (degrees)
            jump_thresh: Jump detection threshold (g)
            land_thresh: Landing detection threshold (g)
            hang_time: Expected time in air (seconds)
            
        Returns:
            List of ACLRiskEvent instances
        """
        if not self.synced:
            raise RuntimeError("Sensors must be synchronized before detecting ACL risks. Call sync_sensors() first.")

        jumps = self.detect_jumps(jump_thresh, land_thresh, hang_time)
        acl_risks = []
        
        for jump, times in jumps.items():
            land_start_idx = self._seconds_to_index(times[1] - (landing_time/2))
            land_end_idx = self._seconds_to_index(times[1] + (landing_time/2))
            
            landing_flexion = np.rad2deg(self.relative_knee_angle(
                event_start_idx=land_start_idx, 
                event_end_idx=land_end_idx, 
                angle_type='flexion',
                angle_method=angle_method
            ))
            landing_rotation = np.rad2deg(self.relative_knee_angle(
                event_start_idx=land_start_idx, 
                event_end_idx=land_end_idx, 
                angle_type='rotation',
                angle_method=angle_method
            ))
            if landing_flexion <= flexion_threshold:
                risky_rotation = abs(landing_rotation) >= rotation_threshold
                acl_risk = ACLRiskEvent(
                    event_type='jump',
                    event_start_time=times[0],
                    event_end_time=times[1],
                    knee_flexion=landing_flexion,
                    knee_rotation=landing_rotation,
                    risky_flexion=True,
                    risky_rotation=risky_rotation
                )
                acl_risks.append(acl_risk)
            else:
                acl_risk = ACLRiskEvent(
                event_type='jump',
                event_start_time=times[0],
                event_end_time=times[1],
                knee_flexion=landing_flexion,
                knee_rotation=landing_rotation,
                risky_flexion=False,
                risky_rotation=False
            )
            acl_risks.append(acl_risk)
        return acl_risks

    # Angle calculation methods
    def absolute_knee_angle(self, event_start_idx: int, event_end_idx: int, angle_type: str = 'flexion') -> float:
        """Calculate absolute knee angle.
        
        Args:
            event_start_idx: Start index of the event
            event_end_idx: End index of the event
            angle_type: Type of angle ('flexion', 'rotation', or 'abduction')
            
        Returns:
            Calculated knee angle in radians
        """
        if angle_type not in ['flexion', 'rotation', 'abduction']:
            raise ValueError("angle_type must be 'flexion', 'rotation', or 'abduction'")

        thigh_to_shank_rotation = self._compute_thigh_shank_rotation(event_start_idx, event_end_idx)
        q = quaternion.as_float_array(thigh_to_shank_rotation)
        q0, q1, q2, q3 = q[0], q[1], q[2], q[3]

        if angle_type == 'flexion':
            return np.arctan2((-2 * q2 * q3) + (2 * q0 * q1), 
                            q3**2 - q2**2 - q1**2 + q0**2)
        elif angle_type == 'rotation':
            return np.arctan2((-2 * q1 * q2) + (2 * q0 * q3), 
                            q1**2 + q0**2 - q3**2 - q2**2)
        else:  # abduction
            return np.arcsin((2 * q1 * q3) + (2 * q0 * q2))

    def relative_knee_angle(self, event_start_idx: int, event_end_idx: int, angle_type: str = 'flexion', angle_method: str = 'quaternion') -> float:
        """Calculate relative knee angle (difference from calibration position).
        
        Args:
            event_start_idx: Start index of the event
            event_end_idx: End index of the event
            angle_type: Type of angle ('flexion', 'rotation', or 'abduction')
            method: Calculation method ('quaternion' or 'euler')
            
        Returns:
            Calculated relative knee angle in radians
        """
        if angle_type not in ['flexion', 'rotation', 'abduction']:
            raise ValueError("angle_type must be 'flexion', 'rotation', or 'abduction'")
        if angle_method not in ['quaternion', 'euler']:
            raise ValueError("method must be 'quaternion' or 'euler'")

        if angle_method == 'euler':
            # Map angle types to euler indices
            angle_idx = {'rotation': 0, 'flexion': 1, 'abduction': 2}[angle_type]
            
            # Calculate mean euler angles for event
            thigh_euler = np.mean([quaternion.as_euler_angles(q) for q in 
                self.thigh_sensor.sensor_orientation.data[event_start_idx:event_end_idx+1]], axis=0)
            shank_euler = np.mean([quaternion.as_euler_angles(q) for q in 
                self.shank_sensor.sensor_orientation.data[event_start_idx:event_end_idx+1]], axis=0)
            
            # if we are computing flexion we have to add angles since sensors are facing opposite directions :(
            if angle_type == "flexion":
                relative_angle = shank_euler[angle_idx] - thigh_euler[angle_idx] - 10 #offset
            else:
                relative_angle = thigh_euler[angle_idx] - shank_euler[angle_idx] 
            return relative_angle
        else:
            calibration_start_idx = self._seconds_to_index(self._shank_sensor.calibration_time[0])
            calibration_end_idx = self._seconds_to_index(self._shank_sensor.calibration_time[1])
            absolute_angle = self.absolute_knee_angle(event_start_idx, event_end_idx, angle_type)
            mean_calibration_angle = self.absolute_knee_angle(
                calibration_start_idx, 
                calibration_end_idx, 
                angle_type
            )

            return absolute_angle - mean_calibration_angle

    def compute_knee_flexion_series(self, method='quaternion') -> np.ndarray:
        """Calculate knee flexion angles for the entire time series.
        
        Args:
            method: String indicating calculation method ('quaternion' or 'euler')
        
        Returns:
            numpy.ndarray: Array of knee flexion angles in radians for each time point
        """
        if not self.synced:
            raise RuntimeError("Sensors must be synchronized before computing knee angles. Call sync_sensors() first.")
        
        if method not in ['quaternion', 'euler']:
            raise ValueError("method must be either 'quaternion' or 'euler'")
        
        # Get the orientations for both sensors
        thigh_orientations = self.thigh_sensor.sensor_orientation.data
        shank_orientations = self.shank_sensor.sensor_orientation.data
        
        # Initialize array for storing flexion angles
        flexion_angles = np.zeros(len(thigh_orientations))
        
        if method == 'euler':
            for i in range(len(thigh_orientations)):
                # Convert quaternions to Euler angles (returns in radians)
                thigh_euler = quaternion.as_euler_angles(thigh_orientations[i])
                shank_euler = quaternion.as_euler_angles(shank_orientations[i])
                flexion_angles[i] = np.rad2deg(shank_euler[1] - thigh_euler[1])
        else:  # quaternion method
            for i in range(len(thigh_orientations)):
                thigh_orientation = thigh_orientations[i]
                shank_orientation = shank_orientations[i]
                
                thigh_segment = thigh_orientation * self.thigh_sensor.sensor_to_segment_alignment
                shank_segment = shank_orientation * self.shank_sensor.sensor_to_segment_alignment
                
                thigh_to_shank = thigh_segment * shank_segment
                q = quaternion.as_float_array(thigh_to_shank)
                q0, q1, q2, q3 = q[0], q[1], q[2], q[3]
                
                flexion_angles[i] = np.rad2deg(np.arctan2((-2 * q2 * q3) + (2 * q0 * q1),
                                            q3**2 - q2**2 - q1**2 + q0**2))
        
        return flexion_angles


    def _find_nearest_idx(self, array, value):
        return np.abs(array - value).argmin()

    def _seconds_to_index(self, seconds):
        if not hasattr(self, '_thigh_sensor') or not self._thigh_sensor:
            raise ValueError("Sensor data not initialized")
        
        time_arr = self._thigh_sensor.sensor_orientation.time_arr
        miliseconds = seconds * 1000
        return self._find_nearest_idx(time_arr, miliseconds)

    def _index_to_seconds(self, index):
        if not hasattr(self, '_thigh_sensor') or not self._thigh_sensor:
            raise ValueError("Sensor data not initialized")
        
        time_arr = self._thigh_sensor.sensor_orientation.time_arr
        if index < 0 or index >= len(time_arr):
            raise ValueError(f"Index {index} out of bounds for time array of length {len(time_arr)}")
        
        return time_arr[index] / 1000

    def _compute_thigh_shank_rotation(self, event_start_idx: int, event_end_idx: int) -> np.ndarray:
        """Compute the rotation between thigh and shank segments.
        
        Args:
            event_start_idx: Start index of the event
            event_end_idx: End index of the event
            
        Returns:
            Quaternion representing the rotation between segments
        """
        mean_thigh_sensor_orientation = mean_orientation(
            self.thigh_sensor.sensor_orientation.data_arr[event_start_idx:event_end_idx]
        )
        mean_shank_sensor_orientation = mean_orientation(
            self.shank_sensor.sensor_orientation.data_arr[event_start_idx:event_end_idx]
        )
        
        mean_thigh_orientation = mean_thigh_sensor_orientation * self.thigh_sensor.sensor_to_segment_rotation
        mean_shank_orientation = mean_shank_sensor_orientation * self.shank_sensor.sensor_to_segment_rotation

        return np.array(mean_thigh_orientation * mean_shank_orientation)

    def _sync_by_nearest(self, unified_time):
        """Synchronize sensor data using nearest neighbor method"""
        # Get time arrays
        thigh_time = self.thigh_time
        shank_time = self.shank_time
        
        # Find nearest indices for all sensors
        thigh_indices = [self._find_nearest_idx(thigh_time, t) for t in unified_time]
        shank_indices = [self._find_nearest_idx(shank_time, t) for t in unified_time]
        
        # Access the x, y, z acceleration and orientation data using getters
        thigh_orient_data = self.thigh_sensor.sensor_orientation.data[thigh_indices]
        thigh_x_accel_data = self.thigh_sensor.x_acceleration.data[thigh_indices]
        thigh_y_accel_data = self.thigh_sensor.y_acceleration.data[thigh_indices]
        thigh_z_accel_data = self.thigh_sensor.z_acceleration.data[thigh_indices]
        
        shank_orient_data = self.shank_sensor.sensor_orientation.data[shank_indices]
        shank_x_accel_data = self.shank_sensor.x_acceleration.data[shank_indices]
        shank_y_accel_data = self.shank_sensor.y_acceleration.data[shank_indices]
        shank_z_accel_data = self.shank_sensor.z_acceleration.data[shank_indices]
        
        # Return the synchronized data as a dictionary
        return {
            "thigh_orientation": thigh_orient_data,
            "thigh_x_acceleration": thigh_x_accel_data,
            "thigh_y_acceleration": thigh_y_accel_data,
            "thigh_z_acceleration": thigh_z_accel_data,
            "shank_orientation": shank_orient_data,
            "shank_x_acceleration": shank_x_accel_data,
            "shank_y_acceleration": shank_y_accel_data,
            "shank_z_acceleration": shank_z_accel_data
        }
