import numpy as np
from .sensor_data import SensorData
from .utils import mean_orientation

class Sensor:
    def __init__(self, sensor_orientation: np.ndarray,
                 x_acceleration: np.ndarray, y_acceleration: np.ndarray, z_acceleration: np.ndarray,
                 acceleration_time_arr: np.ndarray, orientation_time_arr: np.ndarray, 
                 segment_orientation: np.ndarray = None, calibration_time: np.array = None,
                 compute_alignment: bool = False):
        
        self._sensor_orientation = SensorData(data=sensor_orientation, time_arr=orientation_time_arr)
        self._x_acceleration = SensorData(data=x_acceleration,time_arr=acceleration_time_arr)
        self._y_acceleration = SensorData(data=y_acceleration,time_arr=acceleration_time_arr)
        self._z_acceleration = SensorData(data=z_acceleration,time_arr=acceleration_time_arr)
        self._segment_orientation = segment_orientation
        self._calibration_time = calibration_time
        
        self.sensor_to_segment_alignment = None
        if compute_alignment:
            if segment_orientation is None or calibration_time is None:
                raise ValueError("compute_alignment is True, but segment_orientation or calibration_time is not set.")
            self.sensor_to_segment_alignment = self.calculate_sensor_to_segment_alignment(
                segment_orientation=segment_orientation,
                calibration_time=calibration_time
            )
    
    @property
    def sensor_orientation(self) -> SensorData:
        return self._sensor_orientation
    
    @property
    def x_acceleration(self) -> SensorData:
        return self._x_acceleration
    
    @property
    def y_acceleration(self) -> SensorData:
        return self._y_acceleration
    
    @property
    def z_acceleration(self) -> SensorData:
        return self._z_acceleration
    
    @property
    def segment_orientation(self) -> np.ndarray:
        return self._segment_orientation
    
    @property
    def calibration_time(self) -> np.ndarray:
        return self._calibration_time
    
    @calibration_time.setter
    def calibration_time(self, value: np.ndarray):
        if not isinstance(value, np.ndarray):
            raise TypeError("calibration_time must be a numpy array")
        if len(value) != 2:
            raise ValueError("calibration_time must contain exactly 2 values [start_time, end_time]")
        if value[1] <= value[0]:
            raise ValueError("calibration end time must be greater than start time")
        self._calibration_time = value
    
    def calculate_sensor_to_segment_alignment(self, segment_orientation: np.ndarray, calibration_time: np.ndarray) -> np.ndarray:
        """Calculate the sensor to segment alignment rotation"""
        start_calibration_idx = self._find_nearest_idx(self.sensor_orientation.time_arr, calibration_time[0] * 1000)
        end_calibration_idx = self._find_nearest_idx(self.sensor_orientation.time_arr, calibration_time[1] * 1000)

        sensor_calibration_orientation = self.sensor_orientation.data[start_calibration_idx:end_calibration_idx+1]
        average_orientation = mean_orientation(sensor_calibration_orientation)
        
        alignment_rotation = average_orientation / np.linalg.norm(average_orientation)  # Normalize if it's a vector
        alignment_rotation = np.dot(alignment_rotation, segment_orientation)  # Matrix multiplication for rotation
        return alignment_rotation
    
    def _find_nearest_idx(self, array, value):
        return np.abs(array - value).argmin()
