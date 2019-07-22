import requests

def create_transductor(transductor, slave_server):
    protocol = "http://"
    endpoint = "/energy_transductors/"
    address = protocol\
              + slave_server.ip_address\
              + ":"\
              + slave_server.port\
              + endpoint

    model_endpoint = "/transductor_models/"
    model_url = protocol\
              + slave_server.ip_address\
              + ":"\
              + slave_server.port\
              + model_endpoint\
              + transductor.model.model_code\
              + "/"

    data = {
        "model": model_url,
        "serial_number": transductor.serial_number,
        "ip_address": transductor.ip_address,
        "geolocation_latitude": 0.0,
        "geolocation_longitude": 0.0,
        "measurement_minutelymeasurement": [],
        "measurement_quarterlymeasurement": [],
        "measurement_monthlymeasurement": [],
        "firmware_version": '0.1'
    }

    response = requests.post(
        address,
        json = data
    )

    return response
