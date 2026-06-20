import json
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class IMUData:
    """Immutable container for a single IMU reading."""
    acceleration: Tuple[float, float, float]
    gyroscope: Tuple[float, float, float]
    magnetometer: Tuple[float, float, float]


class IMU:
    """Simple IMU wrapper that parses JSON sensor data and provides helper methods."""

    def __init__(self, sensor_data: str):
        """
        Initialise the IMU with a JSON string.

        The JSON must contain three keys:
        - ``acceleration``: list of three floats
        - ``gyroscope``: list of three floats
        - ``magnetometer``: list of three floats
        """
        self.sensor_data = json.loads(sensor_data)

    def read_imu_data(self) -> IMUData:
        """
        Convert the raw JSON payload into an :class:`IMUData` instance.

        The original JSON uses lists; the public API expects immutable tuples,
        matching the type hints and test expectations.
        """
        return IMUData(
            acceleration=tuple(self.sensor_data["acceleration"]),
            gyroscope=tuple(self.sensor_data["gyroscope"]),
            magnetometer=tuple(self.sensor_data["magnetometer"]),
        )

    def calculate_position_and_orientation(
        self, imu_data: IMUData
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """
        Produce a simplistic position and orientation from IMU data.

        * Position is taken directly from the acceleration vector.
        * Orientation is taken directly from the gyroscope vector.
        """
        position = imu_data.acceleration
        orientation = imu_data.gyroscope
        return position, orientation

    def navigate_to_target(
        self,
        position: Tuple[float, float, float],
        orientation: Tuple[float, float, float],
    ) -> bool:
        """
        Determine whether the drone is already at the target.

        For demonstration purposes the target is the origin with a neutral orientation.
        """
        target_position = (0.0, 0.0, 0.0)
        target_orientation = (0.0, 0.0, 0.0)
        return position == target_position and orientation == target_orientation
