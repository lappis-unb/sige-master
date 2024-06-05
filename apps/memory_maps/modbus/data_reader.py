import logging
from enum import Enum

from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.client.udp import ModbusUdpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ModbusException
from pymodbus.payload import BinaryPayloadDecoder

from apps.memory_maps.modbus.helpers import (
    ModbusTypeDecoder,
    apply_sign_transformations,
)

logger = logging.getLogger("apps")


class Protocol(Enum):
    TCP = 1
    UDP = 2
    RTU = 3
    TLS = 4


class ModbusClientFactory:
    def __init__(self, ip_address, port, slave_id, method):
        self.ip_address = ip_address
        self.port = port
        self.method = method
        self.slave_id = slave_id
        self.client = None

    def read_datagroup_blocks(self, register_blocks):
        """
        Reads data from multiple register blocks using Modbus protocol, decodes the data.
        """
        self._start_modbus_client()
        collected_data = {}

        for register_block in register_blocks:
            # TODO - Refatorar a forma de identificar a ordem dos bytes (byte_order) e das palavras (wordorder)
            byte_order = Endian.LITTLE if register_block["byteorder"].startswith(("msb", "f2")) else Endian.BIG

            payload = self._read_registers_block(register_block)
            if payload is None:
                continue

            decoder = BinaryPayloadDecoder.fromRegisters(
                registers=payload,
                byteorder=byte_order,
                wordorder=Endian.LITTLE,
            )

            decoded_data = self._decode_response_message(decoder, register_block)
            collected_data |= decoded_data

        self._stop_client()
        return collected_data

    def _setup_client(self):
        """Create a client instance"""

        if self.method == Protocol.TCP.value:
            client = ModbusTcpClient(self.ip_address, self.port)
        elif self.method == Protocol.UDP.value:
            client = ModbusUdpClient(self.ip_address, self.port)
        else:
            logger.error(f"Invalid protocol Modbus Client: {self.method}")
            raise ModbusException(f"Invalid protocol Modbus Client: {self.method}")
        return client

    def _start_modbus_client(self):
        self.client = self._setup_client()
        self.client.connect()
        logger.info(f"Starting modbus client: connected to {self.ip_address}:{self.port}")

        if not self.client.connected:
            logger.error(f"Connection failure with client: {self.ip_address}:{self.port}")
            raise ConnectionError(f"Connection failure with client: {self.ip_address}:{self.port}")

    def _stop_client(self):
        self.client.close()

    def _read_registers_block(self, register_block):
        """
        Reads the contents of a contiguous block of registers from modbus device
        """

        starting_address = register_block["start_address"]
        size = register_block["size"]

        # TODO - Pegar o tipo de função de leitura Modbus a partir do datamodel ModelTransductor
        # Simplificar o mapa de memória para nao precisar informar a função de leitura
        _function = register_block["function"]
        if _function == "read_input_register":
            response = self.client.read_input_registers(
                address=starting_address,
                count=size,
                slave=self.slave_id,
            )

        elif _function == "read_holding_register":
            response = self.client.read_holding_registers(
                address=starting_address,
                count=size,
                slave=self.slave_id,
            )

        else:
            logger.error(f"Invalid function modbus: {register_block['datamodel']}")
            raise NotImplementedError(f"function modbus: {register_block['datamodel']} not implemented!")

        if response.isError():
            logger.error(f"{self.ip_address} => Error reading holding registers")
            raise ModbusException(f"{self.ip_address} => Error reading holding registers")

        return response.registers

    def _decode_response_message(self, decoder, register_block):
        """
        decode payload message from a modbus response message into data components to their
        respective values which are stored in a dictionary

        O uso de duas casas decimais garante precisão até 0,01, atendendo aos requisitos dos
        medidores Kron Konect e Embrasul MD30, além das normas ANEEL Prodist e IEC 61000-4-7..
        """

        parse_function = ModbusTypeDecoder().parsers[register_block["type"]]
        decoded_value = {}
        for attribute in register_block["attributes"]:
            value = round(parse_function(decoder), 2)
            if isinstance(value, float):
                value = round(value, 2)
            transformed_value = apply_sign_transformations(attribute, value)
            decoded_value[attribute] = transformed_value
        return decoded_value
