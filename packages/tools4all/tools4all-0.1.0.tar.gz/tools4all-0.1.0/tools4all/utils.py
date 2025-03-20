"""
Utility functions for Tools4All
"""
import random
from typing import List, Dict, Any


def get_temperature(location, format):
    """
    Example tool function to get the temperature for a location.
    
    :param location: The location to get the temperature for
    :param format: The temperature format (celsius or fahrenheit)
    :return: The temperature as a string
    """
    if format == "celsius":
        temp = random.randint(-40, 55)
        return f"Current temperature in {location} is {temp}°C"
    elif format == "fahrenheit":
        temp = random.randint(-40, 134)
        return f"Current temperature in {location} is {temp}°F"
    else:
        return f"Invalid format: {format}"


def get_humidity(location):
    """
    Example tool function to get the humidity for a location.
    
    :param location: The location to get the humidity for
    :return: The humidity as a string
    """
    humidity = random.randint(0, 100)
    return f"Current humidity in {location} is {humidity}%"


def create_weather_tools() -> Dict[str, Any]:
    """
    Create and return a dictionary of weather-related tools.
    
    :return: A dictionary of weather tools
    """
    from .core import ToolRegistry
    
    registry = ToolRegistry()
    
    # Register temperature tool
    registry.register_tool(
        "get_temperature",
        get_temperature,
        "Get the current temperature",
        {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "format": {
                    "type": "string",
                    "enum": [
                        "celsius",
                        "fahrenheit"
                    ],
                    "description": "The temperature unit to use. Infer this from the user's location."
                }
            },
            "required": [
                "location",
                "format"
            ]
        }
    )
    
    # Register humidity tool
    registry.register_tool(
        "get_humidity",
        get_humidity,
        "Get the current humidity",
        {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                }
            },
            "required": [
                "location"
            ]
        }
    )
    
    return registry
