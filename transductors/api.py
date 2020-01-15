import requests


def create_transductor(transductor, slave_server):
    protocol = "http://"
    endpoint = "/energy_transductors/"
    address = protocol\
        + slave_server.ip_address\
        + ":"\
        + slave_server.port\
        + endpoint

    return requests.post(address, json=__get_transductor_data(transductor,
                                                              slave_server))


def update_transductor(transductor, slave_server):
    protocol = "http://"
    endpoint = "/energy_transductors/"
    address = protocol\
        + slave_server.ip_address\
        + ":"\
        + slave_server.port\
        + endpoint\
        + transductor.serial_number\
        + "/"

    return requests.put(address, json=__get_transductor_data(transductor,
                                                             slave_server))


def delete_transductor(transductor, slave_server):
    protocol = "http://"
    endpoint = "/energy_transductors/"
    address = protocol\
        + slave_server.ip_address\
        + ":"\
        + slave_server.port\
        + endpoint\
        + transductor.serial_number\
        + "/"

    return requests.delete(address)


def __get_transductor_data(transductor, slave_server):
    lat = (
        transductor.geolocation_latitude
        if transductor.geolocation_latitude is not None else 0.0
    )
    long = (
        transductor.geolocation_longitude
        if transductor.geolocation_longitude is not None else 0.0
    )

    return {
        "model": transductor.model,
        "serial_number": transductor.serial_number,
        "ip_address": transductor.ip_address,
        "physical_location": transductor.physical_location,
        "geolocation_latitude": lat,
        "geolocation_longitude": long,
        "measurement_minutelymeasurement": [],
        "measurement_quarterlymeasurement": [],
        "measurement_monthlymeasurement": [],
        "firmware_version": '0.1'
    }
