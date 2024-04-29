import logging

from django.utils import timezone


def get_measurements_with_missing_values(measurements, value_field: str, missing_values_fill=0, missing_tolerance=10):
    new_measurements = []

    if measurements and len(measurements):
        size = len(measurements)

        start_date_in_minutes = get_minutes_from_date(measurements[0]["collection_date"])
        end_date_in_minutes = get_minutes_from_date(measurements[size - 1]["collection_date"])
        original_measurements_count = 0
        missing_start = -1

        for minute in range(start_date_in_minutes, end_date_in_minutes + 1):
            original_measurement_minute = get_minutes_from_date(
                measurements[original_measurements_count]["collection_date"]
            )

            if original_measurement_minute == minute:
                original_value = measurements[original_measurements_count][value_field]
                original_measurements_count += 1
                missing_end = minute

                if missing_start > -1 and missing_end > -1:
                    new_measurements.extend(
                        get_missing_values_filled(missing_start, missing_end, missing_values_fill, missing_tolerance)
                    )
                    missing_start = -1
                new_measurements.append([get_date_from_minutes(minute), original_value])
            elif missing_start <= -1:
                missing_start = minute

    return new_measurements


def get_missing_values_filled(missing_start=0, missing_end=0, missing_values_fill=0, missing_tolerance=10) -> list:
    missing_values = []
    if abs(missing_start - missing_end) >= missing_tolerance:
        for missing_minute in range(missing_start, missing_end):
            missing_values.append([get_date_from_minutes(missing_minute), missing_values_fill])
    return missing_values


def get_minutes_from_date(date) -> int:
    return int(timezone.datetime.timestamp(date) / 60)


def get_date_from_minutes(minutes):
    return timezone.datetime.fromtimestamp(minutes * 60)
