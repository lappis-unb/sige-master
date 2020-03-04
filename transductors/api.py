import requests


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


def update_transductor(transductor_data, slave_server):
    protocol = "http://"
    endpoint = "/energy-transductors/"
    serial_number = transductor_data.get("serial_number")
    
    address = protocol\
        + slave_server.ip_address\
        + ":"\
        + slave_server.port\
        + endpoint\
        + serial_number\
        + "/"

    j = __get_transductor_data(transductor_data, slave_server)

    print(j )
    return requests.put(address, json=j)

    # return requests.put(address, json=__get_transductor_data(transductor_data,
    #                                                          slave_server))


def delete_transductor(transductor, slave_server):
    protocol = "http://"
    endpoint = "/energy-transductors/"
    address = protocol\
        + slave_server.ip_address\
        + ":"\
        + slave_server.port\
        + endpoint\
        + transductor.serial_number\
        + "/"

    return requests.delete(address)


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
