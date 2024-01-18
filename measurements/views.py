import codecs
import csv
import os
import re
from copy import copy
from datetime import datetime, timedelta

import numpy as np
from dateutil import relativedelta
from django.http import StreamingHttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Case, When, Q, Count, QuerySet
from rest_framework import mixins, permissions, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException, NotAcceptable
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from transductors.models import EnergyTransductor


from measurements.filters import (
    MinutelyMeasurementFilter,
    MonthlyMeasurementFilter,
    QuarterlyMeasurementFilter,
    RealTimeMeasurementFilter,
    UferMeasurementFilter,
)
from measurements.lttb import downsample
from measurements.missing_values import get_measurements_with_missing_values

from measurements.models import (
    MinutelyMeasurement,
    MonthlyMeasurement,
    QuarterlyMeasurement,
    RealTimeMeasurement,
    Tax,
)
from measurements.serializers import (
    MeasurementSerializer,
    MinutelyMeasurementSerializer,
    MonthlyMeasurementSerializer,
    QuarterlyMeasurementSerializer,
    QuarterlySerializer,
    RealTimeMeasurementSerializer,
    TaxSerializer,
    ThreePhaseSerializer,
    UferSerializer,
    ReportSerializer,
)


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 60


class RealTimeMeasurementViewSet(viewsets.ModelViewSet):
    serializer_class = RealTimeMeasurementSerializer
    queryset = RealTimeMeasurement.objects.all().order_by("collection_date")
    filter_backends = [DjangoFilterBackend]
    filterset_class = RealTimeMeasurementFilter


class MinutelyMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MinutelyMeasurement.objects.all().order_by("collection_date")
    serializer_class = MinutelyMeasurementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MinutelyMeasurementFilter
    pagination_class = CustomPageNumberPagination
    fields = []

    def list(self, request, *args, **kwargs):
        transductor = request.query_params.get("id")
        filterset = self.filter_queryset(self.get_queryset())

        if not self.fields or not filterset:
            return super().list(request, *args, **kwargs)

        minutely_measurements = []
        IS_THREEPHASIC = 3

        if len(self.fields) == IS_THREEPHASIC:
            minutely_measurements = self.threephasic_measurement_collections(transductor, filterset)
        else:
            minutely_measurements = self.simple_measurement_collections(transductor, filterset)

        return Response(minutely_measurements)

    def threephasic_measurement_collections(self, transductor, queryset):
        is_filtered = self.request.query_params.get("is_filtered")
        phases = ["phase_a", "phase_b", "phase_c"]

        measurements = {}
        limits = {}

        for idx, phase in enumerate(phases):
            values = queryset.values(self.fields[idx], "collection_date")
            measurements[phase] = get_measurements_with_missing_values(values, self.fields[idx])

            if is_filtered == "True":
                measurements[phase] = self._apply_lttb(measurements[phase])

            limits[phase] = self._get_limits(measurements[phase])

        minutely_measurements = {
            "transductor": transductor,
            "min": min(limits[phase]["min"] for phase in phases),
            "max": max(limits[phase]["max"] for phase in phases),
        }

        for phase in phases:
            minutely_measurements[phase] = self._format_date_from_measurements(measurements[phase])

        return [minutely_measurements]

    def simple_measurement_collections(self, transductor, queryset):
        is_filtered = self.request.query_params.get("is_filtered")

        measurements = get_measurements_with_missing_values(
            queryset.values(self.fields[0], "collection_date"), self.fields[0]
        )

        if is_filtered == "True":
            measurements = self._apply_lttb(measurements)

        limits = self._get_limits(measurements)

        minutely_measurements = {
            "transductor": transductor,
            "min": limits["min"],
            "max": limits["max"],
            "measurements": self._format_date_from_measurements(measurements),
        }

        return [minutely_measurements]

    def _apply_lttb(self, measurements) -> list:
        threshold = int(self.request.query_params.get("threshold", os.getenv("LIMIT_FILTER")))

        filtered_values = copy(measurements)
        indexes = range(len(filtered_values))
        filtered_values = [
            [counter, item[1], timezone.datetime.timestamp(item[0])] for counter, item in zip(indexes, filtered_values)
        ]
        filtered_values = np.array(filtered_values)
        filtered_values = downsample(filtered_values, threshold)
        filtered_values = [[timezone.datetime.fromtimestamp(item[2]), item[1]] for item in filtered_values]

        return filtered_values

    def _get_limits(self, measurements: list) -> dict:
        limits = {
            "min": 0,
            "max": 0,
        }

        if measurements and len(measurements):
            limits["min"] = 1e9
            for measurement in measurements:
                measurement_value = measurement[1]
                if measurement_value < limits["min"] and measurement_value > 0:
                    limits["min"] = measurement_value
                elif measurement_value > limits["max"]:
                    limits["max"] = measurement_value

        return limits

    def _format_date_from_measurements(self, measurements):
        return [[measurement[0].strftime("%m/%d/%Y %H:%M:%S"), measurement[1]] for measurement in measurements]


class QuarterlyMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuarterlyMeasurement.objects.all()
    serializer_class = QuarterlyMeasurementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = QuarterlyMeasurementFilter
    pagination_class = CustomPageNumberPagination
    information = "generation"
    fields = []

    def list(self, request, *args, **kwargs):
        filterset = self.filter_queryset(self.get_queryset())
        self.queryset = filterset

        if not self.fields or not filterset:
            return super().list(request, *args, **kwargs)

        data = {self.information: [], "min": 0, "max": 0}
        measurements = self.queryset.order_by("collection_date").values(*self.fields, "collection_date")

        if measurements:
            response = self.apply_algorithm(measurements)
            for value in response:
                if value[1] is not None and value[2] is not None:
                    total = value[1] + value[2]
                    if total > data["max"]:
                        data["max"] = total

                data[self.information].append([value[0], total])

        return Response(data, status=200)

    def apply_algorithm(self, measurements, transductor=None):
        periodicity = self.request.query_params.get("type")

        if transductor is None:
            transductor = []

        measurements_list = [[measurements[0]["collection_date"], 0, 0]]

        if periodicity == "hourly":
            self.get_hourly_measurements(measurements, measurements_list)
        elif periodicity == "daily":
            self.get_daily_measurements(measurements, measurements_list)

        else:
            measurements_list = []

        return measurements_list

    def get_hourly_measurements(self, measurements, measurements_list):
        for i in range(len(measurements)):
            actual = measurements[i]["collection_date"]
            last = measurements_list[len(measurements_list) - 1][0]

            last_hour = last.hour

            if actual.hour == last_hour:
                self.build_data(actual, measurements, measurements_list, i)
            else:
                self.finish_data(actual, last, measurements, measurements_list, i)

            last = measurements_list[len(measurements_list) - 1][0]
            measurements_list[len(measurements_list) - 1][0] = timezone.datetime(
                last.year, last.month, last.day, last.hour, 0, 0
            )

    def get_daily_measurements(self, measurements, measurements_list):
        for i in range(len(measurements) - 1):
            actual = measurements[i]["collection_date"]
            last = measurements_list[len(measurements_list) - 1][0]

            last_day = last.day

            if actual.day == last_day:
                self.build_data(actual, measurements, measurements_list, i)
            else:
                last = last.replace(hour=0)
                self.finish_data(actual, last, measurements, measurements_list, i)

            last = measurements_list[len(measurements_list) - 1][0]
            measurements_list[len(measurements_list) - 1][0] = timezone.datetime(
                last.year, last.month, last.day, 0, 0, 0
            )

    def build_data(self, actual, measurements, measurements_list, index):
        measurements_list[len(measurements_list) - 1][0] = measurements[index]["collection_date"]
        value = measurements[index][self.fields[1]]

        if value is not None:
            if measurements_list[len(measurements_list) - 1][1] is not None:
                measurements_list[len(measurements_list) - 1][1] += value

    def finish_data(self, actual, last, measurements, measurements_list, index):
        answer_date = timezone.datetime(actual.year, actual.month, actual.day, actual.hour, 0, 0)

        measurements_list[len(measurements_list) - 1][0] = timezone.datetime(
            last.year, last.month, last.day, last.hour, 0, 0
        )

        measurements_list.append([answer_date, measurements[index][self.fields[1]], 0])


class MonthlyMeasurementViewSet(viewsets.ModelViewSet):
    queryset = MonthlyMeasurement.objects.all().order_by("-collection_date")
    serializer_class = MonthlyMeasurementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MonthlyMeasurementFilter
    pagination_class = CustomPageNumberPagination


class MinutelyActivePowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ["active_power_a", "active_power_b", "active_power_c"]


class MinutelyReactivePowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ["reactive_power_a", "reactive_power_b", "reactive_power_c"]


class MinutelyApparentPowerThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ["apparent_power_a", "apparent_power_b", "apparent_power_c"]


class MinutelyPowerFactorThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ["power_factor_a", "power_factor_b", "power_factor_c"]


class MinutelyDHTVoltageThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ["dht_voltage_a", "dht_voltage_b", "dht_voltage_c"]


class MinutelyDHTCurrentThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ["dht_current_a", "dht_current_b", "dht_current_c"]


class MinutelyTotalActivePowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ["total_active_power"]


class MinutelyTotalReactivePowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ["total_reactive_power"]


class MinutelyTotalApparentPowerViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ["total_apparent_power"]


class MinutelyTotalPowerFactorViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ["total_power_factor"]


class VoltageThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ["voltage_a", "voltage_b", "voltage_c"]


class CurrentThreePhaseViewSet(MinutelyMeasurementViewSet):
    serializer_class = ThreePhaseSerializer
    fields = ["current_a", "current_b", "current_c"]


class FrequencyViewSet(MinutelyMeasurementViewSet):
    serializer_class = MeasurementSerializer
    fields = ["frequency_a"]


class TotalConsumptionViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ["consumption_peak_time", "consumption_off_peak_time"]
    information = "consumption"


class TotalGenerationViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ["generated_energy_peak_time", "generated_energy_off_peak_time"]
    information = "generation"


class TotalInductivePowerViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ["inductive_power_peak_time", "inductive_power_off_peak_time"]
    information = "inductive_power"


class TotalCapacitivePowerViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ["capacitive_power_peak_time", "capacitive_power_off_peak_time"]
    information = "capacitive_power"


class DailyConsumptionViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ["consumption_peak_time", "consumption_off_peak_time"]

    def mount_data_list(self, transductor=None):
        total_consumption_per_hour = []
        if transductor is None:
            transductor = []

        response = [0] * 24

        for field in self.fields:
            measurements = self.queryset.values(field, "collection_date")

            if measurements:
                total_consumption_per_hour = self.apply_algorithm(measurements, field)
                for measurement in total_consumption_per_hour:
                    position = int(re.search("([ ][0-9]+)", measurement[0]).group(0))
                    response[position] = measurement[1]

        return response


class ConsumptionCurveViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ["consumption_peak_time", "consumption_off_peak_time"]

    def mount_data_list(self, transductor=[]):
        consumption = []

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        campus = self.request.query_params.get("campus")
        group = self.request.query_params.get("group")
        period = self.request.query_params.get("period")

        if end_date is None:
            end_date = timezone.now()
            end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")

        start_date_compare = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date_compare = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        delta = relativedelta.relativedelta(end_date_compare, start_date_compare)

        # The start_date and end_date in request.
        # query_params have to be the same day
        if self.request.query_params.get("period") == "hourly":
            consumption = self.hourly_consumption_format()
        elif self.request.query_params.get("period") == "daily":
            consumption = self.daily_consumption_format(delta, start_date_compare)
        elif self.request.query_params.get("period") == "monthly":
            consumption = self.monthly_consumption_format(delta, start_date_compare)

        return consumption

    def hourly_consumption_format(self):
        hourly_consumption = {}

        for i in range(24):
            hourly_consumption[str(i) + "h"] = 0

        for field in self.fields:
            measurements = self.queryset.values(field, "collection_date")
            for measurement in measurements:
                hour = measurement["collection_date"].hour
                hourly_consumption[str(hour) + "h"] += measurement[field]

        return hourly_consumption

    def daily_consumption_format(self, delta, start_date):
        daily_consumption = {}
        current_date = start_date

        for i in range(abs(int(delta.days)) + 1):
            daily_consumption[str(current_date.strftime("%d/%m/%y"))] = 0
            current_date = current_date + timedelta(days=1)

        for field in self.fields:
            measurement = measurements = self.queryset.values(field, "collection_date")
            for measurement in measurements:
                day = str(measurement["collection_date"].strftime("%d/%m/%y"))
                daily_consumption[day] += measurement[field]

        return daily_consumption

    def monthly_consumption_format(self, delta, start_date):
        monthly_consumption = {}
        current_date = start_date

        for i in range(abs(int(delta.months)) + 1):
            monthly_consumption[str(current_date.strftime("%m/%y"))] = 0
            current_date = current_date + relativedelta.relativedelta(months=1)

        for field in self.fields:
            measurement = measurements = self.queryset.values(field, "collection_date")
            for measurement in measurements:
                month = str(measurement["collection_date"].strftime("%m/%y"))
                monthly_consumption[month] += measurement[field]

        return monthly_consumption


class CostConsumptionViewSet(QuarterlyMeasurementViewSet):
    serializer_class = QuarterlySerializer
    fields = ["consumption_peak_time", "consumption_off_peak_time"]

    def mount_data_list(self, transductor=[]):
        data = {}
        data["cost"] = []
        data["min"] = 0
        data["max"] = 0

        measurements = self.queryset.order_by("collection_date").values(
            self.fields[0], self.fields[1], "collection_date", "tax__value_peak", "tax__value_off_peak"
        )

        if measurements:
            response = self.apply_algorithm(measurements)

            for value in response:
                total_cost = (value[1] + value[2]) / 1000

                if total_cost > data["max"]:
                    data["max"] = total_cost

                data["cost"].append([value[0], total_cost])

        return data

    def apply_algorithm(self, measurements, transductor=[]):
        type = self.request.query_params.get("type")
        measurements_list = [[measurements[0]["collection_date"], 0, 0]]

        if type == "daily":
            for i in range(0, len(measurements)):
                actual = measurements[i]["collection_date"]

                last_day = measurements_list[len(measurements_list) - 1][0].day

                if actual.day == last_day:
                    self.build_data(actual, measurements, measurements_list, i)
                else:
                    self.finish_data(actual, measurements, measurements_list, i, type)

            last = measurements_list[len(measurements_list) - 1][0]
            measurements_list[len(measurements_list) - 1][0] = timezone.datetime(
                last.year, last.month, last.day, 0, 0, 0
            ).strftime("%m/%d/%Y %H:%M:%S")

        elif type == "monthly":
            for i in range(0, len(measurements) - 1):
                actual = measurements[i]["collection_date"]
                last_month = measurements_list[len(measurements_list) - 1][0].month

                if actual.month == last_month:
                    self.build_data(actual, measurements, measurements_list, i)
                else:
                    self.finish_data(actual, measurements, measurements_list, i, type)

            last = measurements_list[-1][0]
            measurements_list[-1][0] = timezone.datetime(last.year, last.month, 1, 0, 0, 0).strftime(
                "%m/%d/%Y %H:%M:%S"
            )
        elif type == "yearly":
            for i in range(0, len(measurements)):
                actual = measurements[i]["collection_date"]

                last_year = measurements_list[-1][0].year

                if actual.year == last_year:
                    self.build_data(actual, measurements, measurements_list, i)
                else:
                    self.finish_data(actual, measurements, measurements_list, i, type)

            last = measurements_list[-1][0]
            measurements_list[-1][0] = timezone.datetime(last.year, 1, 1, 0, 0, 0).strftime("%m/%d/%Y %H:%M:%S")
        else:
            measurements_list = []

        return measurements_list

    def build_data(self, actual, measurements, measurements_list, index):
        measurements_list[-1][0] = measurements[index]["collection_date"]
        if actual.hour in range(0, 17) or actual.hour in range(21, 23):
            value_off_peak = measurements[index]["tax__value_off_peak"]
            measurements_list[-1][1] += measurements[index][self.fields[1]] * value_off_peak if value_off_peak else 1
        else:
            value_peak = measurements[index]["tax__value_peak"]
            measurements_list[-1][2] += measurements[index][self.fields[0]] * value_peak if value_peak else 1

    def finish_data(self, actual, measurements, measurements_list, index, type):
        answer_date = timezone.datetime(actual.year, actual.month, actual.day, actual.hour, 0, 0)

        last = measurements_list[len(measurements_list) - 1][0]

        if type == "daily":
            measurements_list[-1][0] = timezone.datetime(last.year, last.month, last.day, 0, 0, 0).strftime(
                "%m/%d/%Y %H:%M:%S"
            )
        elif type == "monthly":
            measurements_list[-1][0] = timezone.datetime(last.year, last.month, 1, 0, 0, 0).strftime(
                "%m/%d/%Y %H:%M:%S"
            )
        elif type == "yearly":
            measurements_list[-1][0] = timezone.datetime(last.year, 1, 1, 0, 0, 0).strftime("%m/%d/%Y %H:%M:%S")

        if actual.hour in range(0, 17) or actual.hour in range(21, 23):
            value_off_peak = measurements[index]["tax__value_off_peak"]
            measurements_list.append(
                [answer_date, measurements[index][self.fields[1]] * (value_off_peak if value_off_peak else 1), 0]
            )
        else:
            value_peak = measurements[index]["tax__value_peak"]
            measurements_list.append(
                [answer_date, 0, measurements[index][self.fields[0]] * (value_peak if value_peak else 1)]
            )


class Echo:
    def write(self, value):
        return value


class MeasurementResults(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    @api_view(["GET"])
    def mount_csv_measurement(request):
        class_name = request.query_params.get("class_name")
        fields = request.query_params.get("fields")
        start_date = request.query_params.get("start_date")

        queryset = None

        if class_name == "minutely":
            queryset = MeasurementResults.build_csv(request, MinutelyMeasurement, fields, start_date)
        elif class_name == "quarterly":
            queryset = MeasurementResults.build_csv(request, QuarterlyMeasurement, fields, start_date)
        elif class_name == "monthly":
            queryset = MeasurementResults.build_csv(request, MonthlyMeasurement, fields, start_date)

        if queryset:
            pseudo_buffer = Echo()
            pseudo_buffer.write(codecs.BOM_UTF8)

            writer = csv.writer(pseudo_buffer)
            response = StreamingHttpResponse(
                (writer.writerow(measurement) for measurement in queryset), content_type="text/csv"
            )
            response["Content-Disposition"] = 'attachment; filename="measurement_dataset.csv"'
            response["Content-Transfer-Encoding"] = "binary"

            return response
        else:
            exception = APIException("Class name was not specified in request params.")
            exception.status_code = 400
            raise exception

    @staticmethod
    def build_csv(request, class_name, fields, start_date):
        all_fields = {measurement.name: measurement.verbose_name for measurement in class_name._meta.get_fields()}

        if start_date is None:
            raise NotAcceptable("Start date param is needed to create the csv file.")

        if fields is not None:
            columns = fields.split(",")
        else:
            columns = []

        queryset = list(class_name.objects.filter(collection_date__gte=start_date).values_list(*columns))

        if columns:
            queryset.insert(0, [all_fields[column] for column in columns if column in all_fields])
        else:
            queryset.insert(0, [measurement.verbose_name for measurement in class_name._meta.get_fields()])

        return queryset


class TaxViewSet(viewsets.ModelViewSet):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    permission_classes = (permissions.AllowAny,)


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = QuarterlyMeasurementFilter
    fields = [
        "consumption_peak_time",
        "consumption_off_peak_time",
        "generated_energy_peak_time",
        "generated_energy_off_peak_time",
    ]

    def get_queryset(self):
        queryset = QuarterlyMeasurement.objects.all().only(*self.fields)

        return self.filter_queryset(queryset)

    def list(self, request, *args, **kwargs):
        group = request.query_params.get("group")
        campus = request.query_params.get("campus")
        if not campus:
            return Response({"detail": "Campus parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        measurements = self.get_queryset()
        if not measurements.exists():
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        aggregated_data = self.get_aggregated_monthy(measurements)
        aggregated_data["campus"] = campus

        serializer = self.get_serializer(data=aggregated_data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_aggregated_monthy(self, measurements: QuerySet) -> dict:
        aggregates = {field: Sum(field) for field in self.fields}
        return measurements.aggregate(**aggregates)


class UferViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UferSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UferMeasurementFilter
    fields = ["power_factor_a", "power_factor_b", "power_factor_c"]

    def get_queryset(self):
        queryset = MinutelyMeasurement.objects.all().only(*self.fields, "collection_date")
        non_zero_queryset = queryset.exclude(power_factor_a=0, power_factor_b=0, power_factor_c=0)

        return self.filter_queryset(non_zero_queryset).select_related("transductor")

    def list(self, request):
        campus_id = request.query_params.get("campus")
        if not campus_id:
            return Response({"detail": "Campus parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        transductor_ids = EnergyTransductor.objects.values_list("id", flat=True)
        filtered_measurements = self.get_queryset().filter(transductor__in=transductor_ids)

        filter_conditions = self._generate_filter_conditions()
        annotations = self._generate_annotations(filter_conditions)
        aggregated_data = filtered_measurements.values("transductor", "transductor__name").annotate(**annotations)

        results = []
        for data in aggregated_data:
            transductor_info = {"id": data["transductor"], "name": data["transductor__name"]}
            percentage_data = self._calculate_percentage(data)
            results.append(self._serialize_transductor_data(percentage_data, transductor_info))

        return Response(results, status=status.HTTP_200_OK)

    def _generate_filter_conditions(self, threshold: float = 0.92) -> Q:
        conditions = Q()
        for field in self.fields:
            conditions |= Q(**{f"{field}__gt": -0.92}) & Q(**{f"{field}__lt": 0.92})

        return conditions

    def _generate_annotations(self, filter_conditions: Q) -> dict:
        annotations = {}
        for field in self.fields:
            annotations[f"{field}_total"] = Count(field)
            annotations[f"{field}_interval"] = Count(Case(When(filter_conditions, then=1)))

        return annotations

    def _calculate_percentage(self, measurements: dict) -> dict:
        data = {}

        for field in self.fields:
            total = measurements[f"{field}_total"]
            interval_count = measurements[f"{field}_interval"]
            data[field] = (interval_count / total) * 100 if total else 0
        return data

    def _serialize_transductor_data(self, percent_data: dict, transductor_info: dict) -> dict:
        serializer = self.serializer_class(
            data={
                "transductor_id": transductor_info["id"],
                "transductor_name": transductor_info["name"],
                "phase_a": percent_data["power_factor_a"],
                "phase_b": percent_data["power_factor_b"],
                "phase_c": percent_data["power_factor_c"],
            }
        )
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
