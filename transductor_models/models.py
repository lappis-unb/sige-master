from django.db import models


class TransductorModel(models.Model):
    """
    Class responsible to define a transductor model which contains
    crucial informations about the transductor itself.

    Attributes:
        name (str): The factory name.
        transport_protocol (str): The transport protocol.
        serial_protocol (str): The serial protocol.
        register_addresses (list): Registers with data to be collected.
            .. note::
            This attribute must meet the following pattern:

            [[Register Address (int), Register Type (int)]]

            Where:
                - Register Address: register address itself.
                - Register Type: register data type.
                    - 0 - Integer
                    - 1 - Float

            Example: [[68, 0], [70, 1]]

    Example of use:

        >>> TransductorModel(name="Test Name", transport_protocol="UDP",
        serial_protocol="Modbus RTU", register_addresses=[[68, 0], [70, 1]])
        <TransductorModel: Test Name>
    """

    name = models.CharField(max_length=50, unique=True)
    serial_protocol = models.CharField(max_length=50, default="")
    transport_protocol = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.name
