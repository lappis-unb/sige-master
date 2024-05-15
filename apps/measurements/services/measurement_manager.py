import logging
from datetime import timedelta

from django.db import transaction

from apps.measurements.models import CumulativeMeasurement

MINUTES_INTERVAL = 15
logger = logging.getLogger("apps")


class CumulativeMeasurementManager:
    """
    A class to manage the creation and handling of cumulative measurements based on provided data.

    This class provides functionality to calculate missing measurement intervals, distribute
    measurement deltas across these intervals, and create new CumulativeMeasurement instances
    to fill in gaps in measurement data. The creation of new measurements based on the validated
    input data and fields specified.

    Methods:
        handle_cumulative_measurements(validated_data, last_measurement, fields):
            The main method intended for external use. It processes the validated data to
            manage and create new cumulative measurement instances.

        _calculate_intervals_missing(last_measurement, validated_data):
            Calculate the number of time intervals missing between the last recorded measurement
            and the new data provided.

        _calculate_delta_fields(last_measurement, validated_data, fields):
            Calculate the delta for specified fields between the last measurement and new validated data.

        _distribute_interval_measurements(delta_data, intervals):
            Distribute the calculated deltas evenly over the number of missing intervals.

        _create_missing_measurements(last_measurement, data_chunk, intervals_missed):
            Create and return a list of new CumulativeMeasurement instances to fill in the missing intervals.

    Usage:
        - To create new cumulative measurements, instantiate this class and call the
          `handle_cumulative_measurements` method with appropriate data.

    Example:
        >>> validated_data = {'collection_date': datetime.datetime(2021, 5, 15), 'active_consumption': 19, ....}
        >>> last_measurement = CumulativeMeasurement.objects.get(id=1)
        >>> fields = ['active_consumption', 'active_generated', ....]
        >>> measurements = MeasurementCreator.handle_cumulative_measurements(validated_data, last_measurement, fields)
    """

    @classmethod
    def handle_measurements(cls, validated_data, last_measurement, fields):
        """This is the only method that should be called from outside the class"""

        intervals_missed = cls._calculate_intervals_missing(last_measurement, validated_data)

        delta_data = cls._calculate_delta_fields(last_measurement, validated_data, fields)
        delta_validated_data = validated_data.copy()
        delta_validated_data.update(delta_data)

        if intervals_missed <= 1:
            return CumulativeMeasurement.objects.create(**delta_validated_data)

        data_chunk = cls._distribute_interval_measurements(delta_validated_data, intervals_missed, fields)
        return cls._create_missing_instances(last_measurement, data_chunk, intervals_missed)

    @classmethod
    def _calculate_delta_fields(cls, last_measurement, validated_data, fields):
        delta_data = {}
        for field in fields:
            if field in validated_data:
                last_value = getattr(last_measurement, field, 0)
                new_value = validated_data[field]
                if new_value < last_value:
                    logger.warning(f"Invalid measurement value for field '{field}': {new_value}")
                    raise ValueError(f"Invalid measurement value for field '{field}': {new_value}")
                if new_value is None:
                    logger.warning(f"Invalid new measurement value for field '{field}': {new_value}")
                    new_value = 0

                if last_value is None:
                    logger.warning(f"Invalid last measurement value for field '{field}': {last_value}")
                    last_value = 0

                delta = new_value - last_value
                delta_data[field] = delta
                logger.debug(f"Calculated delta for field '{field}': {delta}")
        return delta_data

    @classmethod
    def _calculate_intervals_missing(cls, last_measurement, validated_data):
        delta_time = validated_data["collection_date"] - last_measurement.updated
        intervals_missing = delta_time / timedelta(minutes=MINUTES_INTERVAL)
        return max(int(intervals_missing), 0)

    @classmethod
    def _distribute_interval_measurements(cls, delta_data, intervals_missed, cumulative_fields):
        return {
            field: round(value / intervals_missed, 2)
            for field, value in delta_data.items()
            if field in cumulative_fields
        }

    @classmethod
    def _create_missing_instances(cls, last_measurement, data_chunk, intervals_missed):
        start_time = last_measurement.updated
        transductor = last_measurement.transductor

        if start_time is None or transductor is None:
            logger.warning("Invalid last measurement data: 'updated' and 'transductor' fields are required.")
            raise ValueError("last_measurement must have 'updated' and 'transductor' fields")

        with transaction.atomic():
            instances = []
            for pos in range(intervals_missed):
                timestamp = start_time + timedelta(minutes=15 * pos)
                instance = CumulativeMeasurement(
                    transductor=transductor,
                    collection_date=timestamp,
                    is_calculated=True,
                    **data_chunk,
                )
                instances.append(instance)

            with transaction.atomic():
                CumulativeMeasurement.objects.bulk_create(instances)

            return instances
