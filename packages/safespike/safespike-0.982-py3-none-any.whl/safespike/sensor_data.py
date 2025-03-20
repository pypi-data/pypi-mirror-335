import numpy as np
from dataclasses import dataclass

@dataclass
class SensorData:
    data: np.ndarray
    time_arr: np.ndarray
    
    def __post_init__(self):
        if not isinstance(self.data, np.ndarray):
            raise TypeError("Data must be a numpy ndarray.")
        if not isinstance(self.time_arr, np.ndarray):
            raise TypeError("Time array must be a numpy ndarray.")
        if len(self.data) != len(self.time_arr):
            raise ValueError("Data and time arrays must have the same length.")


@dataclass
class ACLRiskEvent:
    event_type: str
    event_start_time: float
    event_end_time: float 
    knee_flexion: float
    knee_rotation: float
    risky_flexion: bool
    risky_rotation: bool 
