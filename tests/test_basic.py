"""
Basic tests for kerykeion-mcp package
"""

import pytest
from kerykeion_mcp import get_current_time, __version__


def test_version():
    """Test that version is defined"""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_get_current_time():
    """Test get_current_time function"""
    result = get_current_time()

    assert result["success"] is True
    assert "data" in result

    data = result["data"]
    assert "datetime_str" in data
    assert "timestamp" in data
    assert "weekday" in data
    assert "year" in data
    assert "month" in data
    assert "day" in data
    assert "hour" in data
    assert "minute" in data
    assert "second" in data


def test_get_current_time_structure():
    """Test the structure of current time data"""
    result = get_current_time()
    data = result["data"]

    # Check that all fields are present and have reasonable values
    assert isinstance(data["year"], int)
    assert 2020 <= data["year"] <= 2100  # reasonable year range
    assert 1 <= data["month"] <= 12
    assert 1 <= data["day"] <= 31
    assert 0 <= data["hour"] <= 23
    assert 0 <= data["minute"] <= 59
    assert 0 <= data["second"] <= 59
    assert isinstance(data["timestamp"], int)
    assert data["timestamp"] > 0
