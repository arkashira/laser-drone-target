from drone_targeting import get_positioning_data, calculate_targeting_information, display_targeting_information
import io
import sys

def test_get_positioning_data():
    alternative_positioning_system = "test_system"
    positioning_data = get_positioning_data(alternative_positioning_system)
    assert positioning_data.latitude == 37.7749
    assert positioning_data.longitude == -122.4194
    assert positioning_data.altitude == 100.0

def test_calculate_targeting_information():
    positioning_data = get_positioning_data("test_system")
    target_latitude = 37.7859
    target_longitude = -122.4364
    targeting_information = calculate_targeting_information(positioning_data, target_latitude, target_longitude)
    assert targeting_information.target_latitude == target_latitude
    assert targeting_information.target_longitude == target_longitude
    assert targeting_information.distance_to_target > 0

def test_display_targeting_information(capsys):
    targeting_information = calculate_targeting_information(get_positioning_data("test_system"), 37.7859, -122.4364)
    display_targeting_information(targeting_information)
    captured = capsys.readouterr()
    assert "Target Latitude:" in captured.out
    assert "Target Longitude:" in captured.out
    assert "Distance to Target:" in captured.out

def test_calculate_targeting_information_edge_case():
    positioning_data = get_positioning_data("test_system")
    target_latitude = positioning_data.latitude
    target_longitude = positioning_data.longitude
    targeting_information = calculate_targeting_information(positioning_data, target_latitude, target_longitude)
    assert targeting_information.distance_to_target == 0
