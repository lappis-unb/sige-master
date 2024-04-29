from csv import DictReader
from datetime import datetime, timedelta
from pathlib import Path

from django.utils import timezone

from apps.memory_maps.modbus.settings import (
    ON_PEAK_TIME_END,
    ON_PEAK_TIME_START,
    SIGN_TRANSFORMATIONS,
)


class ModbusTypeDecoder(object):
    """
    Parsing different data types commonly used in Modbus communication. Use dictionary to
    mapping the data type string names to their corresponding parsing methods.
    """

    def __init__(self):
        self.parsers = {
            "uint8": self.parse_8bit_uint(),
            "uint16": self.parse_16bit_uint(),
            "uint32": self.parse_32bit_uint(),
            "uint64": self.parse_64bit_uint(),
            "int8": self.parse_8bit_int(),
            "int16": self.parse_16bit_int(),
            "int32": self.parse_32bit_int(),
            "int64": self.parse_64bit_int(),
            "float16": self.parse_16bit_float(),
            "float32": self.parse_32bit_float(),
            "float64": self.parse_64bit_float(),
            "bits": self.parse_bits(),
        }

    @staticmethod
    def parse_bits():
        return lambda d: d.decode_bits()

    @staticmethod
    def parse_8bit_uint():
        return lambda d: d.decode_8bit_uint()

    @staticmethod
    def parse_16bit_uint():
        return lambda d: d.decode_16bit_uint()

    @staticmethod
    def parse_32bit_uint():
        return lambda d: d.decode_32bit_uint()

    @staticmethod
    def parse_64bit_uint():
        return lambda d: d.decode_64bit_uint()

    @staticmethod
    def parse_8bit_int():
        return lambda d: d.decode_8bit_int()

    @staticmethod
    def parse_16bit_int():
        return lambda d: d.decode_16bit_int()

    @staticmethod
    def parse_32bit_int():
        return lambda d: d.decode_32bit_int()

    @staticmethod
    def parse_64bit_int():
        return lambda d: d.decode_64bit_int()

    @staticmethod
    def parse_16bit_float():
        return lambda d: d.decode_16bit_float()

    @staticmethod
    def parse_32bit_float():
        return lambda d: d.decode_32bit_float()

    @staticmethod
    def parse_64bit_float():
        return lambda d: d.decode_64bit_float()


def remove_format_datetime(measurements):
    measurements_copy = measurements.copy()
    for measurement, _ in measurements_copy.items():
        if measurement in (
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "day_of_the_month",
            "day_of_the_week",
            "day_of_the_year",
        ):
            del measurements[measurement]

    return timezone.datetime(
        measurements_copy["year"],
        measurements_copy["month"],
        measurements_copy["day_of_the_month"],
        measurements_copy["hour"],
        measurements_copy["minute"],
        measurements_copy["second"],
    )


def type_modbus(data_type: str) -> str:
    clean_format = data_type.replace(" ", "").strip("-").lower()

    uint8 = {"u8", "ui8", "uint8"}
    uint16 = {"u16", "ui16", "uint", "word", "uint16", "s16", "short"}
    uint32 = {"ui32", "u32", "uint32", "dword", "ul32", "ulong"}
    uint64 = {"uint64", "u64", "ui64", "ulong64", "ulonglong"}
    int8 = {"int8", "i8", "integer8"}
    int16 = {"int", "i16", "int16", "int16bit", "integer", "integer16"}
    int32 = {"int32", "i32", "integer32", "l32", "long", "long32", "li32"}
    int64 = {"int64", "i64", "integer64", "longlong", "longint64"}
    float16 = {"float16", "f16", "fp16", "half"}
    float32 = {"f32", "fp32", "float", "float32", "real", "single"}
    float64 = {"f64", "fp64", "float64", "lreal", "double"}
    bits = {"bit", "bits", "b"}

    if clean_format in uint8:
        data_type = "uint8"
    elif clean_format in uint16:
        data_type = "uint16"
    elif clean_format in uint32:
        data_type = "uint32"
    elif clean_format in uint64:
        data_type = "uint64"
    elif clean_format in int8:
        data_type = "int8"
    elif clean_format in int16:
        data_type = "int16"
    elif clean_format in int32:
        data_type = "int32"
    elif clean_format in int64:
        data_type = "int64"
    elif clean_format in float16:
        data_type = "float16"
    elif clean_format in float32:
        data_type = "float32"
    elif clean_format in float64:
        data_type = "float64"
    elif clean_format in bits:
        data_type = "bits"
    else:
        raise ValueError(f"Unsupported type: {data_type}")

    return data_type


def is_peak_time(dt_reference: datetime = None) -> bool:
    if dt_reference is None:
        dt_reference = timezone.now()

    # Nao considera o minuto final para ajustar ao cronjob:
    # exemplo coleta: 18h => time = 17:59 => return False
    #                 21h => time = 20:59 => return True
    time = (dt_reference - timedelta(minutes=1)).time()

    is_weekday = dt_reference.weekday() < 5  # de segunda a sexta-feira
    is_peak_time = ON_PEAK_TIME_START <= time <= ON_PEAK_TIME_END

    return is_weekday and is_peak_time


def map_registers_to_model(register_blocks, model):
    mapping = {block["register_name"]: block["model_attribute"] for block in register_blocks}
    setattr(model, "register_mapping", mapping)


def reader_csv_file(path_file: Path):
    csv_data = []
    with open(path_file, "r", encoding="utf8") as file_handle:
        csv_reader = DictReader(file_handle, delimiter=",", skipinitialspace=True)

        for row in csv_reader:
            row = {key.lower().strip(): value.lower().strip() for key, value in row.items()}

            if row.get("active") in ["t", "y", "true", "yes", "1"]:
                csv_data.append(row)
    return csv_data


def get_now():
    return timezone.now().strftime("%d/%m/%Y  %H:%M:%S")


def update_key_attributes(self, modbus_data) -> dict:
    """
    Update the key attributes of the provided modbus_data with the appropriate peak/off-peak
    time and return as a dictionary
    """

    peak_time = "_peak_time" if is_peak_time() else "_off_peak_time"
    return {attribute + peak_time: value for attribute, value in modbus_data.items()}


def apply_sign_transformations(attribute, value):
    transform = SIGN_TRANSFORMATIONS.get(attribute, None)

    return transform(value) if transform else value
