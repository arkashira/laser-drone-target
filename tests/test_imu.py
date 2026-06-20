from imu import IMU, IMUData

def test_read_imu_data():
    sensor_data = '{"acceleration": [1.0, 2.0, 3.0], "gyroscope": [4.0, 5.0, 6.0], "magnetometer": [7.0, 8.0, 9.0]}'
    imu = IMU(sensor_data)
    imu_data = imu.read_imu_data()
    assert imu_data.acceleration == (1.0, 2.0, 3.0)
    assert imu_data.gyroscope == (4.0, 5.0, 6.0)
    assert imu_data.magnetometer == (7.0, 8.0, 9.0)

def test_calculate_position_and_orientation():
    sensor_data = '{"acceleration": [1.0, 2.0, 3.0], "gyroscope": [4.0, 5.0, 6.0], "magnetometer": [7.0, 8.0, 9.0]}'
    imu = IMU(sensor_data)
    imu_data = imu.read_imu_data()
    position, orientation = imu.calculate_position_and_orientation(imu_data)
    assert position == (1.0, 2.0, 3.0)
    assert orientation == (4.0, 5.0, 6.0)

def test_navigate_to_target():
    sensor_data = '{"acceleration": [0.0, 0.0, 0.0], "gyroscope": [0.0, 0.0, 0.0], "magnetometer": [0.0, 0.0, 0.0]}'
    imu = IMU(sensor_data)
    imu_data = imu.read_imu_data()
    position, orientation = imu.calculate_position_and_orientation(imu_data)
    assert imu.navigate_to_target(position, orientation) == True

def test_navigate_to_target_failure():
    sensor_data = '{"acceleration": [1.0, 2.0, 3.0], "gyroscope": [4.0, 5.0, 6.0], "magnetometer": [7.0, 8.0, 9.0]}'
    imu = IMU(sensor_data)
    imu_data = imu.read_imu_data()
    position, orientation = imu.calculate_position_and_orientation(imu_data)
    assert imu.navigate_to_target(position, orientation) == False
