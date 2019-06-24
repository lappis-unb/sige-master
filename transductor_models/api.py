import requests


def create_transductor_model(transductor_model):
    from slaves.models import Slave
    slave_server = Slave.objects.first()

    protocol = "http://"
    endpoint = "/transductor_models/"
    address = protocol\
              + slave_server.ip_address\
              + ":"\
              + slave_server.port\
              + endpoint

    data = {
        "name": transductor_model.name,
        "model_code": transductor_model.model_code,
        "serial_protocol": transductor_model.serial_protocol,
        "transport_protocol": (transductor_model.transport_protocol),
        "minutely_register_addresses": transductor_model.minutely_register_addresses,
        "quarterly_register_addresses": transductor_model.quarterly_register_addresses,
        "monthly_register_addresses": transductor_model.monthly_register_addresses
    }

    response = requests.post(
        address,
        json=data
    )

    return response
