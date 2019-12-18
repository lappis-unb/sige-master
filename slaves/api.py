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
