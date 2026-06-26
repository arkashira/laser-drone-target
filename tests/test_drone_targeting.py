from drone_targeting import get_positioning_data, calculate_targeting_information, create_user_interface
import io
import sys

def test_get_positioning_data():
    alternative_positioning_system = "mock_system"
    positioning_data = get_positioning_data(alternative_positioning_system)
    assert positioning_data.latitude == 37.7749
    assert positioning_data.longitude == -122.4194
    assert positioning_data.altitude == 100.0

def test_calculate_targeting_information():
    positioning_data = get_positioning_data("mock_system")
    target_latitude = 37.7859
    target_longitude = -122.4364
    targeting_information = calculate_targeting_information(positioning_data, target_latitude, target_longitude)
    assert targeting_information.target_latitude == target_latitude
    assert targeting_information.target_longitude == target_longitude
    assert targeting_information.distance_to_target > 0

def test_create_user_interface(capsys):
    positioning_data = get_positioning_data("mock_system")
    targeting_information = calculate_targeting_information(positioning_data, 37.7859, -122.4364)
    create_user_interface(positioning_data, targeting_information)
    captured = capsys.readouterr()
    assert "Positioning Data:" in captured.out
    assert "Targeting Information:" in captured.out

def test_main():
    captured_output = io.StringIO()
    sys.stdout = captured_output
    sys.argv = ["drone_targeting.py", "--target_latitude", "37.7859", "--target_longitude", "-122.4364"]
    from drone_targeting import main
    main()
    sys.stdout = sys.__stdout__
    assert "Positioning Data:" in captured_output.getvalue()
    assert "Targeting Information:" in captured_output.getvalue()
