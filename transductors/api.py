import requests


def check_connection(slave):
    if slave is None:
        return True 

    protocol = "http://"
    endpoint = "/energy-transductors/"
    address = protocol\
        + slave.ip_address\
        + ":"\
        + slave.port\
        + endpoint
    try:
        response = requests.get(address, timeout=1)
    except Exception:
        return False

    if response.status_code == 200:
        return True

    else:
        return False


def create_transductor(transductor_data, slave_server):
    protocol = "http://"
    endpoint = "/energy-transductors/"
    address = protocol\
        + slave_server.ip_address\
        + ":"\
        + slave_server.port\
        + endpoint

    return requests.post(address, 
                         json=__get_transductor_data(
                             transductor_data, slave_server),
                         timeout=1
                         )


def update_transductor(transductor_id, transductor_data, slave_server):
    protocol = "http://"
    endpoint = "/energy-transductors/"

    address = protocol\
        + slave_server.ip_address\
        + ":"\
        + slave_server.port\
        + endpoint\
        + str(transductor_id)\
        + "/"

    return requests.put(address, 
                        json=__get_transductor_data(
                            transductor_data, slave_server),
                        timeout=1
                        )


def delete_transductor(transductor_id, transductor, slave_server):
    protocol = "http://"
    endpoint = "/energy-transductors/"
    address = protocol\
        + slave_server.ip_address\
        + ":"\
        + slave_server.port\
        + endpoint\
        + str(transductor_id)\
        + "/"

    return requests.delete(address, timeout=1)


def __get_transductor_data(transductor, slave_server):
    latitude = transductor.get('geolocation_latitude')
    if latitude is None:
        latitude = 0.0

    longitude = transductor.get('geolocation_longitude')

    if longitude is None:
        longitude = 0.0

    return {
        "model": transductor.get('model'),
        "serial_number": transductor.get('serial_number'),
        "ip_address": transductor.get('ip_address'),
        "geolocation_latitude": latitude,
        "geolocation_longitude": longitude,
        "measurement_minutelymeasurement": [],
        "measurement_quarterlymeasurement": [],
        "measurement_monthlymeasurement": [],
        "firmware_version": transductor.get('firmware_version')
    }
