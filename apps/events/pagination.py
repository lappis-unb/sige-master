from rest_framework.pagination import PageNumberPagination


class EventPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100
    last_page_strings = ("last",)
