import asyncio
import json
import logging

import httpx
from rest_framework.status import is_server_error, is_success

logger = logging.getLogger(__name__)


def send_request(method, url, data=None):
    try:
        if method.upper() not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response = httpx.request(method, url, json=data)
        response.raise_for_status()
        return response
    except httpx.HTTPError as exc:
        logger.exception(f"HTTP Exception for {exc.request.url} - {exc}")
        raise


def create_transductor(transductor):
    endpoint = "/energy-transductors/"
    slave_server = transductor.slave_server
    url = f"http://{slave_server.server_address}:{slave_server.port}{endpoint}"
    data = _get_transductor_data(transductor)

    return send_request("POST", url, data)


def update_transductor(transductor):
    endpoint = "/energy-transductors/"
    slave_server = transductor.slave_server
    data = _get_transductor_data(transductor)
    url = f"http://{slave_server.server_address}:{slave_server.port}{endpoint}{transductor.id}/"

    return send_request("PUT", url, data)


def delete_transductor(transductor):
    endpoint = "/energy-transductors/"
    slave_server = transductor.slave_server
    url = f"http://{slave_server.server_address}:{slave_server.port}{endpoint}{transductor.id}/"

    return send_request("DELETE", url)


def _get_transductor_data(transductor):
    physical_location = f"{transductor.campus}"

    return {
        "id": transductor.id,
        "model": transductor.model,
        "serial_number": transductor.serial_number,
        "ip_address": transductor.ip_address,
        "firmware_version": transductor.firmware_version,
        "port": transductor.port,
        "geolocation_latitude": transductor.geolocation_latitude,
        "geolocation_longitude": transductor.geolocation_longitude,
        "physical_location": physical_location,
        "installation_date": transductor.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
    }


# ---------------------------------------------------------------------------------------------
# TODO: Subistituir funcoes sync por async
# ---------------------------------------------------------------------------------------------


async def delete_from_slave(instance):
    return await request_slave_transductor(instance, "DELETE")


async def create_on_slave(instance):
    return await request_slave_transductor(instance, "POST")


async def update_on_slave(instance):
    return await request_slave_transductor(instance, "PUT")


async def request_slave_transductor(instance, method, max_retries=3, wait_time=5):
    endpoint = "/energy-transductors/"
    slave_server = instance.slave_server
    data = _get_transductor_data(instance)

    base_url = f"http://{slave_server.server_address}:{slave_server.port}{endpoint}"
    if method in ["update", "delete"]:
        base_url = f"{base_url}/{instance.id}"

    if method == "delete":
        data = None

    for attempt in range(1, max_retries + 1):
        try:
            result = await _make_request(method, base_url, data)
            return result

        except Exception as e:
            _handle_retry(attempt, max_retries, wait_time, method, e)

    return str(e), None


async def _make_request(method, base_url, data):
    async with httpx.AsyncClient() as client:
        response = await client.request(method, base_url, json=data)

        if is_server_error(response.status_code):
            raise Exception(f"{response.text} - {response.status_code}")

        if is_success(response.status_code):
            serialized_data = json.loads(response.text)
            return serialized_data, response.status_code

        return response.text, response.status_code


async def _handle_retry(attempt, max_retries, wait_time, method, exception):
    logger.warning(f"Attempt {attempt}: {exception} - retrying in {wait_time} seconds")
    if attempt == max_retries:
        logger.error(
            f"Failed: {method} transductor Slave API after {attempt} attempts: {exception}"
        )
        raise exception  # ou return str(exception), None se preferir
    else:
        await asyncio.sleep(wait_time)
