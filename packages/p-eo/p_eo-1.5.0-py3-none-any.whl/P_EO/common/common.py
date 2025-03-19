import json

import requests
from requests.exceptions import RequestException


def json_format(data: dict):
    converted_data = {}
    for key, value in data.items():
        try:
            # Try to parse the value as JSON
            converted_data[key] = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # If it fails, keep the original value
            converted_data[key] = value
    return converted_data


def get_chrome_driver_by_port(port):
    url = f'http://127.0.0.1:{port}/json/version'
    try:
        data = requests.get(url).json()
        return data['Browser'].split('/')[-1]
    except RequestException:
        raise Exception(f'Failed to get Chrome driver version for port {port}')
