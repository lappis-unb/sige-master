import requests
from datetime import datetime, timedelta


def request_measurements(measurement_type, slave, transductor=None, 
                         start_date=None, end_date=None):
    protocol = "http://"
    endpoint = "/" + measurement_type + "/"
    address = protocol\
        + slave.ip_address\
        + ":"\
        + slave.port\
        + endpoint

    if transductor is not None and start_date is not None:
        params = {
            "id": transductor.id,
            "start_date": start_date,
            "end_date": datetime.now()
        }
    else:
        params = {}

    return requests.get(address, params=params)


def request_events(slave, event_type):
    """
    Makes the http request to get events from a slave server
    """
    protocol = "http://"
    endpoint = "/" + event_type + "/"

    params = {}
    if transductor is not None:
        params["id"] = transductor.id

    if start_date is not None:
        start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
        params["start_date"] = start_date        

    if end_date is not None:
        end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
        params["end_date"] = end_date        

    return requests.get(address, params=params)


def request_all_events(slave):
    """
    Gets all slave related events.
    Returns an array of tuples containing tuple(Classname, response) pairs
    """
    responses = [
        (
            "FailedConnectionTransductorEvent",
            request_measurements('failed-connection-events', slave)
        ),
        (
            "VoltageRelatedEvent",
            request_measurements('voltage-events', slave)
        )
    ]

    return responses
