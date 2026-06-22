from laser_drone_target import create_system, Deployment, System
import pytest
from datetime import datetime, timedelta

def test_deployment_within_window():
    system = create_system()
    deployment = system.deploy("new_environment")
    assert deployment.is_within_deployment_window()

def test_deployment_outside_window():
    system = create_system()
    deployment = Deployment("new_environment", datetime.now() - timedelta(hours=3))
    assert not deployment.is_within_deployment_window()

def test_update_performance():
    system = create_system()
    deployment = system.deploy("new_environment")
    system.update(deployment, "Updated performance data")
    assert deployment.get_performance() == "Updated performance data"

def test_get_deployment():
    system = create_system()
    deployment = system.deploy("new_environment")
    assert system.get_deployment("new_environment") == deployment

def test_get_documentation():
    system = create_system()
    assert system.get_documentation() == "Comprehensive documentation"

def test_create_system():
    system = create_system()
    assert isinstance(system, System)
    assert system.deployments == []
    assert system.documentation == "Comprehensive documentation"

def test_deploy_system():
    system = create_system()
    deployment = system.deploy("new_environment")
    assert isinstance(deployment, Deployment)
    assert deployment.environment == "new_environment"
    assert deployment.deployment_time is not None
