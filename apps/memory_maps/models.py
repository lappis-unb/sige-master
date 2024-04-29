import logging

from django.db import models

from apps.memory_maps.modbus.helpers import type_modbus
from apps.memory_maps.modbus.settings import CSV_SCHEMA
from apps.transductors.models import TransductorModel

logger = logging.getLogger("apps")


class MemoryMap(models.Model):
    model = models.OneToOneField(TransductorModel, on_delete=models.CASCADE, related_name="memory_map")
    instant_measurements = models.JSONField()
    cumulative_measurements = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.model.name}"

    class Meta:
        verbose_name_plural = "Memory Maps"

    def get_memory_map_by_type(self, data_type: str):
        # TODO - move string literals to constants in settings or utils
        if data_type in {"instant", "realtime", "minutely"}:
            return self.instant_measurements
        elif data_type in {"cumulative", "aggregate", "quarterly"}:
            return self.cumulative_measurements
        return {}

    @classmethod
    def create_from_csv(cls, transductor_model: TransductorModel, csv_data: list[dict], max_block: int):
        instance = cls(model=transductor_model, instant_measurements={}, cumulative_measurements={})

        instance.instant_measurements = instance._process_csv_data("minutely", csv_data, max_block)
        instance.cumulative_measurements = instance._process_csv_data("quarterly", csv_data, max_block)
        return instance.save()

    def update_from_csv(self, csv_data: list[dict], max_block: int):
        self.instant_measurements = self._process_csv_data("minutely", csv_data, max_block)
        self.cumulative_measurements = self._process_csv_data("quarterly", csv_data, max_block)
        return self.save()

    def _process_csv_data(self, data_group, csv_data, max_block):
        datagroup_registers = self._get_valid_registers_by_group(csv_data, data_group)

        if not datagroup_registers:
            return {}

        return self._build_sequential_blocks(datagroup_registers, max_block)

    def _get_valid_registers_by_group(self, csv_data: list[dict], data_group: str) -> list[dict]:
        required_headers = CSV_SCHEMA.keys()

        try:
            datagroup_registers = []
            for line in csv_data:
                if line["group"] != data_group:
                    continue

                filtered_line = {column: line[column] for column in line if column in required_headers}
                filtered_line.update(
                    {
                        "address": int(line["address"]),
                        "size": int(line["size"]),
                        "type": type_modbus(line["type"]),
                    }
                )
                datagroup_registers.append(filtered_line)
            return datagroup_registers

        except (TypeError, ValueError, KeyError) as e:
            raise ValueError(f"Error occurred while processing data: {e}") from e

    def _build_sequential_blocks(self, registers: list[dict], len_max_block: int) -> list[dict]:
        """
        Group consecutive registers with type and until the `len_max_block` number of registers
        is reached or the next register has a different address or type than the previous one.
        It then adds the block of consecutive registers to a list of sequential blocks.
        """

        sequential_blocks = []
        current_block = {
            "start_address": registers[0]["address"],
            "size": registers[0]["size"],
            "type": registers[0]["type"],
            "byteorder": registers[0]["byteorder"],
            "function": registers[0]["function"],
            "attributes": [registers[0]["attribute"]],
        }

        register_counter = 1
        for i in range(1, len(registers)):
            current_line = registers[i]

            check_conditions = all(
                [
                    current_line["address"] == current_block["start_address"] + current_block["size"],
                    current_line["type"] == current_block["type"],
                    register_counter < len_max_block,
                ]
            )

            if check_conditions:
                current_block["size"] += current_line["size"]
                register_counter += 1
                current_block["attributes"].append(current_line["attribute"])

            else:
                sequential_blocks.append(current_block)
                current_block = {
                    "start_address": current_line["address"],
                    "size": current_line["size"],
                    "type": current_line["type"],
                    "byteorder": current_line["byteorder"],
                    "function": current_line["function"],
                    "attributes": [current_line["attribute"]],
                }
                register_counter = 1

        sequential_blocks.append(current_block)
        return sequential_blocks


# ===========================================================================================================================
# class SequentialBlock(models.Model):
#     memory_map = models.ForeignKey(MemoryMap, on_delete=models.CASCADE, related_name="sequential_blocks")
#     start_address = models.PositiveIntegerField()
#     size = models.PositiveIntegerField()
#     type = models.CharField(max_length=10)
#     byteorder = models.CharField(max_length=10)
#     function = models.CharField(max_length=10)
#     attributes = models.JSONField()

#     def __str__(self):
#         return f"Block {self.start_address} - {self.size}"

#     class Meta:
#         verbose_name = "Sequential Block"
#         verbose_name_plural = "Sequential Blocks"
#         unique_together = ["memory_map", "start_address"]
#         ordering = ["start_address"]

#     @classmethod
#     def create_from_csv(cls, memory_map: MemoryMap, csv_data: list[dict], max_block: int):
#         datagroup_registers = cls._get_valid_registers_by_group(csv_data, memory_map.model, max_block)
#         sequential_blocks = cls._build_sequential_blocks(datagroup_registers, max_block)

#         for block in sequential_blocks:
#             cls.objects.create(memory_map=memory_map, **block)
