import requests

def create_transductor(transductor, slave_server):
    protocol = "http://"
    endpoint = "/energy_transductors/"
    address = protocol\
              + slave_server.ip_address\
              + ":"\
              + slave_server.port\
              + endpoint

    return requests.post(address, json = __get_transductor_data(transductor, slave_server))

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

    return requests.put(address, json = __get_transductor_data(transductor, slave_server))

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
    latitude = transductor.latitude if transductor.latitude is not None else 0.0
    longitude = transductor.longitude if transductor.longitude is not None else 0.0

    return {
        "model": __get_model_url(transductor, slave_server),
        "serial_number": transductor.serial_number,
        "ip_address": transductor.ip_address,
        "physical_location": transductor.location,
        "geolocation_latitude": latitude,
        "geolocation_longitude": longitude,
        "measurement_minutelymeasurement": [],
        "measurement_quarterlymeasurement": [],
        "measurement_monthlymeasurement": [],
        "firmware_version": '0.1'
    }

def __get_model_url(transductor, slave_server):
    protocol = "http://"
    endpoint = "/energy_transductors/"
    model_endpoint = "/transductor_models/"

    return protocol\
           + slave_server.ip_address\
           + ":"\
           + slave_server.port\
           + model_endpoint\
           + transductor.model.model_code\
           + "/"
