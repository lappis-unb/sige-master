import requests
from datetime import datetime, timedelta


def request_measurements(slave, transductor, start_date, measurement_type):
    protocol = "http://"
    endpoint = "/" + measurement_type + "/"
    address = protocol\
        + slave.ip_address\
        + ":"\
        + slave.port\
        + endpoint

    try:
        params = {
            "serial_number": transductor.serial_number,
            "start_date": start_date,
            "end_date": datetime.now()
        }
    except Exception as exception:
        print(exception)
        params = {}

    return requests.get(address)


def request_events(slave, event_type):
    """
    Makes the http request to get events from a slave server
    """
    protocol = "http://"
    endpoint = "/" + event_type + "/"

    params = {}

    url = "%s%s:%s%s" % (protocol, slave.ip_address, slave.port, endpoint)

    response = requests.get(url, params=params)
    return response


def request_all_events(slave):
    """
    Gets all slave related events.
    Returns an array of tuples containing tuple(Classname, response) pairs
    """
    responses = [
        (
            "FailedConnectionTransductorEvent",
            request_events(slave, 'failed-connection-events')
        ),
        (
            "VoltageRelatedEvent",
            request_events(slave, 'voltage-events')
        )
    ]

    return responses
