import logging

import httpx

logger = logging.getLogger("tasks")


def request_measurements(path, slave, pk=None, start_date=None, end_date=None):
    url = f"http://{slave.server_address}:{slave.port}{path}"
    params = {
        "transductor": pk,
        "start_date": start_date,
        "end_date": end_date,
    }

    logger.info(f"Starting data collection from: {url}")
    logger.debug(
        f"params: {{'transductor': {params['transductor']},"
        f"'start_date': {params['start_date'].strftime('%d-%m-%Y %H:%M:%S')}}}"
        if start_date
        else params
    )

    data, url = send_request(url, params)
    while url:
        page_data, url = send_request(url)
        data.extend(page_data)

    logger.info(f"Finished data collection from Endpoint: {path}.")
    logger.debug(f"Total results received: {len(data)}")
    return data


def request_events(slave, event_type, transductor=None, start_date=None, end_date=None):
    url = f"http://{slave.server_address}:{slave.port}/{event_type}/"

    params = {
        "id": transductor.id,
        "start_date": start_date,
        "end_date": end_date,
    }

    data = []
    while url:
        page_data, url = send_request(url, params)
        data.extend(page_data)
    return data


def request_all_events(slave):
    """Gets all slave related events."""
    responses = [
        ("FailedConnectionTransductorEvent", request_measurements("failed-connection-events", slave)),
        ("VoltageRelatedEvent", request_measurements("voltage-events", slave)),
    ]
    return responses


def build_url(slave, endpoint):
    return f"http://{slave.server_address}:{slave.port}/{endpoint}/"


def send_request(url, params=None):
    logger.debug(f"Sending HTTP request to: {url}")
    try:
        response = httpx.get(url, params=params)
        response.raise_for_status()
        results = response.json()["results"]
        next_url = response.json()["next"]
        logger.debug(f"Successful HTTP request: status_code={response.status_code}, received {len(results)} results")
        return results, next_url
    except httpx.HTTPError as exc:
        logger.exception(f"HTTP Exception for {exc.request.url} - {exc}")
        raise
