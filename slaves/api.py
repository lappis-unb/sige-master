import requests
import datetime


def request_measurements(slave, transductor, start_date, measurement_type):
    protocol = "http://"
    endpoint = "/" + measurement_type +"_measurements/"
    address = protocol\
        + slave.ip_address\
        + ":"\
        + slave.port\
        + endpoint

    #Fix date interval
    params = {
        "serial_number": transductor.serial_number,
        "start_date": start_date,
        "end_date": "2019-10-10"
        # "end_date": datetime.date.today()
    }

    response = requests.get(address, params)

    print("###################")
    print(response.content)
    print("###################")

    return response

# def create_transductor(transductor, slave_server):
#     protocol = "http://"
#     endpoint = "/energy_transductors/"
#     address = protocol\
#         + slave_server.ip_address\
#         + ":"\
#         + slave_server.port\
#         + endpoint
#
#     return requests.post(address, json=__get_transductor_data(transductor,
#                                                               slave_server))
#
#
#
# def create_transductor(transductor, slave_server):
#     protocol = "http://"
#     endpoint = "/energy_transductors/"
#     address = protocol\
#         + slave_server.ip_address\
#         + ":"\
#         + slave_server.port\
#         + endpoint
#
#     return requests.post(address, json=__get_transductor_data(transductor,
#                                                               slave_server))
#
#
# def update_transductor(transductor, slave_server):
#     protocol = "http://"
#     endpoint = "/energy_transductors/"
#     address = protocol\
#         + slave_server.ip_address\
#         + ":"\
#         + slave_server.port\
#         + endpoint\
#         + transductor.serial_number\
#         + "/"
#
#     return requests.put(address, json=__get_transductor_data(transductor,
#                                                              slave_server))
#
#
# def delete_transductor(transductor, slave_server):
#     protocol = "http://"
#     endpoint = "/energy_transductors/"
#     address = protocol\
#         + slave_server.ip_address\
#         + ":"\
#         + slave_server.port\
#         + endpoint\
#         + transductor.serial_number\
#         + "/"
#
#     return requests.delete(address)
#
#
# def __get_transductor_data(transductor, slave_server):
#     lat = transductor.latitude if transductor.latitude is not None else 0.0
#     long = transductor.longitude if transductor.longitude is not None else 0.0
#
#     return {
#         "model": __get_model_url(transductor, slave_server),
#         "serial_number": transductor.serial_number,
#         "ip_address": transductor.ip_address,
#         "physical_location": transductor.location,
#         "geolocation_latitude": lat,
#         "geolocation_longitude": long,
#         "measurement_minutelymeasurement": [],
#         "measurement_quarterlymeasurement": [],
#         "measurement_monthlymeasurement": [],
#         "firmware_version": '0.1'
#     }
#
#
# def __get_model_url(transductor, slave_server):
#     protocol = "http://"
#     endpoint = "/energy_transductors/"
#     model_endpoint = "/transductor_models/"
#
#     return protocol\
#         + slave_server.ip_address\
#         + ":"\
#         + slave_server.port\
#         + model_endpoint\
#         + transductor.model.model_code\
#         + "/"
