"""Fressnapf API Client."""

import logging
from typing import Any
from httpx import AsyncClient

_LOGGER: logging.Logger = logging.getLogger(__name__)


class APIError(Exception):
    """General API error."""

class InvalidCredentials(APIError):
    """Invalid credentials."""


class InvalidDeviceToken(APIError):
    """Invalid device token error."""


class InvalidToken(APIError):
    """Invalid auth token error."""


class InvalidSerialNumber(APIError):
    """Invalid serial number error."""


async def request_sms_code(client: AsyncClient, phonenumber: str, auth_token: str) -> dict[str, Any]:
    """request sms code from user.iot-pet-tracking.cloud"""
    url = f"https://user.iot-pet-tracking.cloud/api/app/v1/users/request_sms_code"
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip",
        "Connection": "keep-alive",
        "User-Agent": "okhttp/4.9.2",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }

    data = {
        "user": {
            "phone": f"{phonenumber}",
            "locale": "en"
        },
        "tracker_service": "fressnapf"
    }
    response = await client.post(url, headers=headers, json=data)
    result = response.json()
    _LOGGER.debug("Result from sms request: %s", result)

    if "error" in result:
        if "Bad credentials" in result["error_description"]:
            raise InvalidCredentials(result["error"])
        raise Exception(result["error"])
    return result


async def verify_phone_number(client: AsyncClient, userid: str,  smstoken: str, auth_token: str) -> dict[str, Any]:
    """send number validation to user.iot-pet-tracking.cloud"""
    url = f"https://user.iot-pet-tracking.cloud/api/app/v1/users/verify_phone_number"
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip",
        "Connection": "keep-alive",
        "User-Agent": "okhttp/4.9.2",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }

    data = {
        "user": {
            "id": f"{userid}",
            "smscode": f"{smstoken}",
            "user_token": {
                "push_token": "",
                "app_version": "2.9.0_11",
                "app_platform": "android",
                "platform_version": 30,
                "phone_name": "HomeAssistant"
            }
        }
    }
    response = await client.post(url, headers=headers, json=data)
    result = response.json()
    _LOGGER.debug("Result from phonenumber verification: %s", result)

    if "error" in result:
        if "code did not match" in result["error"]:
            raise InvalidToken(result["error"])
        raise Exception(result["error"])
    return result


async def get_devices(client: AsyncClient, userid: str,  user_access_token: str, auth_token: str) -> dict[str, Any]:
    """ get devices from itsmybike.cloud / user.iot-pet-tracking.cloud"""
    url = f"https://user.iot-pet-tracking.cloud/api/app/v1/devices/"
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip",
        "Connection": "keep-alive",
        "User-Agent": "okhttp/4.9.2",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }

    params = {
        "user_id": f"{userid}",
        "user_access_token": f"{user_access_token}"
    }


    response = await client.get(url, headers=headers, params=params)
    result = response.json()
    _LOGGER.debug("Result from request devices: %s", result)

    if "error" in result: #checked
        if "user_access_token" in result["error"]:
            raise InvalidCredentials(result["error"])
        raise Exception(result["error"])
    return result


async def get_fressnapf_response(
    client: AsyncClient, serial_number: int, device_token: str, auth_token: str
) -> dict[str, Any]:
    """Get data from the API."""
    url = f"https://itsmybike.cloud/api/pet_tracker/v2/devices/{serial_number}?devicetoken={device_token}"
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip",
        "authorization": f"Token token={auth_token}",
        "Connection": "keep-alive",
        "Host": "itsmybike.cloud",
        "User-Agent": "okhttp/4.9.2",
        "Content-Type": "application/json",
    }
    response = await client.get(url, headers=headers)
    result = response.json()
    _LOGGER.debug("Result from fressnapf_tracker: %s", result)

    if "error" in result:
        if "Access denied" in result["error"]:
            raise InvalidToken(result["error"])
        if "Invalid devicetoken" in result["error"]:
            raise InvalidDeviceToken(result["error"])
        if "Device not found" in result["error"]:
            raise InvalidSerialNumber(result["error"])
        raise Exception(result["error"])
    return _transform_result(result)


def _transform_result(result: dict[str, Any]) -> dict[str, Any]:
    """Flatten some entries."""
    if result["tracker_settings"]["features"]["flash_light"]:
        result["led_brightness_value"] = result["led_brightness"]["value"]
        result["led_brightness_status"] = result["led_brightness"]["status"]
        result["led_activatable_overall"] = result["led_activatable"]["overall"]
    if result["tracker_settings"]["features"]["sleep_mode"]:
        result["deep_sleep_value"] = result["deep_sleep"]["value"]
        result["deep_sleep_status"] = result["deep_sleep"]["status"]
    return result
