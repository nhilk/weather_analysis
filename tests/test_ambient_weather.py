import os
import sys
import pytest
import polars as pl
sys.path.append('src')
from ambient_weather import transform_data_facts

def base_ambient(date="2023-01-01T12:00:00"):
    return {
        "date": date,
        "source": "https://ambientweather.net",
        "tempf": 72.5,
        "baromrelin": 29.92,
        "humidity": 45,
        "winddir": 180,
        "windspdmph_avg10m": 5.4,
        "windgustmph": 8.2,
        "dailyrainin": 0.0,
    }

def test_transform_with_numeric_strings():
    # numeric fields supplied as strings should still produce a DataFrame (values preserved as strings)
    ambient = base_ambient()
    ambient.update({
        "tempf": "72.5",
        "baromrelin": "29.92",
        "humidity": "45",
        "winddir": "180",
        "windspdmph_avg10m": "5.4",
        "windgustmph": "8.2",
        "dailyrainin": "0.0",
    })
    df = transform_data_facts(ambient, location_id=2)
    assert isinstance(df, pl.DataFrame)
    # values remain the provided strings
    assert df["temperature"][0] == "72.5"
    assert df["humidity"][0] == "45"
    assert df["wind_direction"][0] == "180"

def test_transform_with_invalid_date_type_raises_value_error():
    # date provided as an integer (inconsistent type) should cause a ValueError from transform_data_facts
    ambient = base_ambient(date=1672531200)  # int instead of ISO string
    with pytest.raises(ValueError) as excinfo:
        transform_data_facts(ambient, location_id=1)
    assert "Error transforming data" in str(excinfo.value)

def test_transform_with_none_ambient_raises_required_error():
    # ambient_data None should raise the explicit "Data is required" ValueError
    with pytest.raises(ValueError) as excinfo:
        transform_data_facts(None, location_id=1)
    assert str(excinfo.value) == "Data is required"

def test_transform_with_none_field_results_in_null_column():
    # individual fields set to None should be preserved as nulls in the resulting DataFrame
    ambient = base_ambient()
    ambient["tempf"] = None
    ambient["humidity"] = None
    df = transform_data_facts(ambient, location_id=5)
    assert isinstance(df, pl.DataFrame)
    # Polars represents missing values as None when accessed
    assert df["temperature"][0] is None
    assert df["humidity"][0] is None