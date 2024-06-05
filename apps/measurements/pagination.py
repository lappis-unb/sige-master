from collections import OrderedDict

from rest_framework.pagination import BasePagination, PageNumberPagination
from rest_framework.response import Response


class MeasurementPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100
    last_page_strings = ("last",)


class ChartDataPagination(BasePagination):
    def paginate_queryset(self, queryset, request, view=None):
        page_size = request.query_params.get("page_size")
        if page_size:
            self.page_size = int(page_size)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
