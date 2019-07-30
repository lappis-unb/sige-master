import requests


def create_transductor_model(transductor_model, slave_server):
    protocol = "http://"
    endpoint = "/transductor_models/"
    address = protocol\
              + slave_server.ip_address\
              + ":"\
              + slave_server.port\
              + endpoint

    return requests.post(address, json=__get_data(transductor_model))

def update_transductor_model(transductor_model, slave_server):
    protocol = "http://"
    endpoint = "/transductor_models/"
    address = protocol\
              + slave_server.ip_address\
              + ":"\
              + slave_server.port\
              + endpoint\
              + transductor_model.model_code\
              + "/"

    return requests.put(address, json = __get_data(transductor_model))

def delete_transductor_model(transductor_model, slave_server):
    protocol = "http://"
    endpoint = "/transductor_models/"
    address = protocol\
              + slave_server.ip_address\
              + ":"\
              + slave_server.port\
              + endpoint\
              + transductor_model.model_code\
              + "/"

    return requests.delete(address)

def __get_data(transductor_model):
    return {
        "name": transductor_model.name,
        "model_code": transductor_model.model_code,
        "serial_protocol": transductor_model.serial_protocol,
        "transport_protocol": (transductor_model.transport_protocol),
        "minutely_register_addresses": transductor_model.minutely_register_addresses,
        "quarterly_register_addresses": transductor_model.quarterly_register_addresses,
        "monthly_register_addresses": transductor_model.monthly_register_addresses
    }
