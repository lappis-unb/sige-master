import logging

import pandas as pd
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.measurements.filters import (
    CumulativeMeasurementFilter,
    InstantMeasurementFilter,
)
from apps.measurements.models import CumulativeMeasurement, InstantMeasurement
from apps.measurements.pagination import MeasurementPagination
from apps.measurements.serializers import (
    CumulativeMeasurementSerializer,
    GraphDataSerializer,
    InstantMeasurementSerializer,
)
from apps.measurements.lttb import LTTBDownSampler

logger = logging.getLogger("apps.measurements.graphics")


class InstantMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstantMeasurement.objects.all()
    serializer_class = InstantMeasurementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = InstantMeasurementFilter
    pagination_class = MeasurementPagination


class CumulativeMeasurementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CumulativeMeasurementSerializer
    queryset = CumulativeMeasurement.objects.all()
    pagination_class = MeasurementPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_measurements = serializer.save()

        if isinstance(created_measurements, CumulativeMeasurement):
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        data = self.get_serializer(created_measurements, many=True).data
        return Response(data, status=status.HTTP_201_CREATED)


class InstantGraphViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstantMeasurement.objects.all()
    serializer_class = GraphDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = InstantMeasurementFilter

    def list(self, request, *args, **kwargs):
        query_params = self.get_query_params()
        self.validate_params(query_params)

        queryset = self.get_queryset(fields=query_params["fields"])
        if not queryset:
            return Response(status=status.HTTP_204_NO_CONTENT)

        df = pd.DataFrame(list(queryset))
        lttb = query_params["lttb"].lower() == "true"
        response = self.apply_lttb(df) if lttb else df
        serializer = self.get_serializer(response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_query_params(self):
        fields = self.request.query_params.get("fields", "")
        return {
            "fields": fields.split(",") if fields else [],
            "transductor": self.request.query_params.get("transductor", None),
            "lttb": self.request.query_params.get("lttb", None),
            "threshold": self.request.query_params.get("threshold", settings.LIMIT_FILTER),
        }

    def validate_params(self, query_params):
        required_params = ["transductor", "fields"]
        missing_params = [param for param in required_params if query_params.get(param) is None]

        if missing_params:
            message = f"Missing required parameters: {', '.join(missing_params)}"
            logger.error(f"Error: {message}")
            raise ValidationError({"error": message})

    def get_queryset(self, *args, **kwargs):
        fields = kwargs.get("fields", [])
        try:
            queryset = super().get_queryset().values("collection_date", *fields)
        except Exception as e:
            logger.error(f"Error in get_queryset: {e}")
            raise ValidationError({"error": str(e)})
        return self.filter_queryset(queryset)

    def apply_lttb(self, df):
        threshold = int(self.request.query_params.get("threshold", settings.LIMIT_FILTER))
        try:
            downsampler = LTTBDownSampler(threshold, enable_parallel=False)
            return downsampler.apply_lttb(df, dt_column="collection_date")
        except Exception as e:
            logger.error(f"Error in apply_lttb: {e}")
            raise ValidationError({"error": str(e)})


class CumulativeGraphViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CumulativeMeasurement.objects.all()
    serializer_class = GraphDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CumulativeMeasurementFilter

    def list(self, request, *args, **kwargs):
        query_params = self.get_query_params()
        self.validate_params(query_params)

        queryset = self.get_queryset(field=query_params["field"])
        if not queryset.exists():
            return Response({"detail": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        data = pd.DataFrame(list(queryset))
        response = self.apply_resample(data, query_params["period"], query_params["method"])
        serializer = self.get_serializer(response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_query_params(self):
        return {
            "transductor": self.request.query_params.get("transductor", None),
            "field": self.request.query_params.get("field", None),
            "period": self.request.query_params.get("period", "PT15M"),
            "method": self.request.query_params.get("method", "sum"),
        }

    def validate_params(self, query_params):
        required_params = ["transductor", "field"]
        missing_params = [param for param in required_params if query_params.get(param) is None]

        if missing_params:
            message = f"Missing required parameters: {', '.join(missing_params)}"
            logger.error(f"Error: {message}")
            raise ValidationError({"error": message})

    def get_queryset(self, *args, **kwargs):
        field = self.request.query_params.get("field", None)
        try:
            queryset = super().get_queryset().values("collection_date", field)
        except Exception as e:
            logger.error(f"Error in get_queryset: {e}")
            raise ValidationError({"error": str(e)})
        return self.filter_queryset(queryset)

    def apply_resample(self, df, period, method, dropna=True):
        if not period or period == "PT15M":
            return df
        try:
            rule = self.get_resample_frequency(period)
        except Exception as e:
            logger.error(f"Error in apply_resample: {e}")
            raise ValidationError({"error": str(e)})

        df_resampled = df.resample(rule, on="collection_date").apply(method)
        df_resampled = df_resampled.reset_index()

        if dropna:
            df_resampled.dropna(inplace=True)
        return df_resampled

    def get_resample_frequency(self, period):
        frequency = pd.Timedelta(period)
        if frequency is None:
            raise ValueError(f"Invalid period format: '{period}'. Use ISO8601 duration format (PT<value><unit>).")

        elif frequency.total_seconds() < 900:
            raise ValueError(f"Invalid period value: '{period}'. Minimum value is 15 minutes 'PT15M'.")
        logger.debug(f"Resampling rule determined: {frequency.total_seconds() // 60} minutes")
        return frequency

    @action(detail=False, methods=["get"])
    def hourly(self, request, *args, **kwargs):
        query_params = self.get_query_params()
        self.validate_params(query_params)

        queryset = self.get_queryset(field=query_params["field"])
        if not queryset.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)

        data = pd.DataFrame(list(queryset))
        data.set_index("collection_date", inplace=True)
        data_hourly = data.resample("h").apply("sum")

        data_hourly = data_hourly.groupby(data_hourly.index.hour).mean()
        data_hourly = data_hourly.reset_index()
        data_hourly.rename(columns={"collection_date": "hour"}, inplace=True)
        data_hourly.rename(columns={query_params["field"]: "value"}, inplace=True)

        responde = {
            "field": query_params["field"],
            "start_date": data.index[0],
            "end_date": data.index[-1],
            "data": data_hourly.to_dict(orient="records"),
        }

        return Response(responde, status=status.HTTP_200_OK)


# class MeasurementResults(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
#     @api_view(["GET"])
#     def mount_csv_measurement(request):
#         class_name = request.query_params.get("class_name")
#         fields = request.query_params.get("fields")
#         start_date = request.query_params.get("start_date")

#         queryset = None

#         if class_name == "minutely":
#             queryset = MeasurementResults.build_csv(request, MinutelyMeasurement, fields, start_date)
#         elif class_name == "quarterly":
#             queryset = MeasurementResults.build_csv(request, CumulativeMeasurement, fields, start_date)
#         elif class_name == "monthly":
#             queryset = MeasurementResults.build_csv(request, MonthlyMeasurement, fields, start_date)

#         if queryset:
#             pseudo_buffer = Echo()
#             pseudo_buffer.write(codecs.BOM_UTF8)

#             writer = csv.writer(pseudo_buffer)
#             response = StreamingHttpResponse(
#                 (writer.writerow(measurement) for measurement in queryset), content_type="text/csv"
#             )
#             response["Content-Disposition"] = 'attachment; filename="measurement_dataset.csv"'
#             response["Content-Transfer-Encoding"] = "binary"

#             return response
#         else:
#             exception = APIException("Class name was not specified in request params.")
#             exception.status_code = 400
#             raise exception

#     @staticmethod
#     def build_csv(request, class_name, fields, start_date):
#         all_fields = {measurement.name: measurement.verbose_name for measurement in class_name._meta.get_fields()}

#         if start_date is None:
#             raise NotAcceptable("Start date param is needed to create the csv file.")

#         if fields is not None:
#             columns = fields.split(",")
#         else:
#             columns = []

#         queryset = list(class_name.objects.filter(collection_date__gte=start_date).values_list(*columns))

#         if columns:
#             queryset.insert(0, [all_fields[column] for column in columns if column in all_fields])
#         else:
#             queryset.insert(0, [measurement.verbose_name for measurement in class_name._meta.get_fields()])

#         return queryset


# class ReportViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = ReportSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = CumulativeMeasurementFilter
#     fields = [
#         "consumption_peak_time",
#         "consumption_off_peak_time",
#         "generated_energy_peak_time",
#         "generated_energy_off_peak_time",
#     ]

#     def get_queryset(self):
#         queryset = CumulativeMeasurement.objects.all().only(*self.fields)

#         return self.filter_queryset(queryset)

#     def list(self, request, *args, **kwargs):
#         group = request.query_params.get("group")
#         campus = request.query_params.get("campus")
#         if not campus:
#             return Response({"detail": "Campus parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

#         measurements = self.get_queryset()
#         if not measurements.exists():
#             return Response({}, status=status.HTTP_204_NO_CONTENT)

#         aggregated_data = self.get_aggregated_monthy(measurements)
#         aggregated_data["campus"] = campus

#         serializer = self.get_serializer(data=aggregated_data)
#         serializer.is_valid(raise_exception=True)

#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def get_aggregated_monthy(self, measurements: QuerySet) -> dict:
#         aggregates = {field: Sum(field) for field in self.fields}
#         return measurements.aggregate(**aggregates)


# class UferViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = UferSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = UferMeasurementFilter
#     fields = ["power_factor_a", "power_factor_b", "power_factor_c"]

#     def get_queryset(self):
#         queryset = MinutelyMeasurement.objects.all().only(*self.fields, "collection_date")
#         non_zero_queryset = queryset.exclude(power_factor_a=0, power_factor_b=0, power_factor_c=0)

#         return self.filter_queryset(non_zero_queryset).select_related("transductor")

#     def list(self, request):
#         campus_id = request.query_params.get("campus")
#         if not campus_id:
#             return Response({"detail": "Campus parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

#         transductor_ids = Transductor.objects.values_list("id", flat=True)
#         filtered_measurements = self.get_queryset().filter(transductor__in=transductor_ids)

#         filter_conditions = self._generate_filter_conditions()
#         annotations = self._generate_annotations(filter_conditions)
#         aggregated_data = filtered_measurements.values("transductor", "transductor__name").annotate(**annotations)

#         results = []
#         for data in aggregated_data:
#             transductor_info = {"id": data["transductor"], "name": data["transductor__name"]}
#             percentage_data = self._calculate_percentage(data)
#             results.append(self._serialize_transductor_data(percentage_data, transductor_info))

#         return Response(results, status=status.HTTP_200_OK)

#     def _generate_filter_conditions(self, threshold: float = 0.92) -> Q:
#         conditions = Q()
#         for field in self.fields:
#             conditions |= Q(**{f"{field}__gt": -0.92}) & Q(**{f"{field}__lt": 0.92})

#         return conditions

#     def _generate_annotations(self, filter_conditions: Q) -> dict:
#         annotations = {}
#         for field in self.fields:
#             annotations[f"{field}_total"] = Count(field)
#             annotations[f"{field}_interval"] = Count(Case(When(filter_conditions, then=1)))

#         return annotations

#     def _calculate_percentage(self, measurements: dict) -> dict:
#         data = {}

#         for field in self.fields:
#             total = measurements[f"{field}_total"]
#             interval_count = measurements[f"{field}_interval"]
#             data[field] = (interval_count / total) * 100 if total else 0
#         return data

#     def _serialize_transductor_data(self, percent_data: dict, transductor_info: dict) -> dict:
#         serializer = self.serializer_class(
#             data={
#                 "transductor_id": transductor_info["id"],
#                 "transductor_name": transductor_info["name"],
#                 "phase_a": percent_data["power_factor_a"],
#                 "phase_b": percent_data["power_factor_b"],
#                 "phase_c": percent_data["power_factor_c"],
#             }
#         )
#         serializer.is_valid(raise_exception=True)
#         return serializer.validated_data
