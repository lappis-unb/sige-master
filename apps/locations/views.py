import logging

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.locations.models import Address, GeographicLocation, State
from apps.locations.serializers import (
    AddressDetailSerializer,
    AddressSerializer,
    GeographicLocationSerializer,
    StateSerializer,
)
from apps.locations.services import cities_by_state

logger = logging.getLogger("apps")


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return AddressDetailSerializer
        return AddressSerializer

    @action(detail=False, methods=["get"], url_path="get-cities")
    def get_cities(self, request, code=None):
        state_code = request.query_params.get("code", code)

        if state_code is None:
            return Response({"error": "State code is required"}, status=400)

        cities = cities_by_state(state_code)
        return Response(cities, status=200)

    @method_decorator(cache_page(600))
    @action(detail=False, methods=["get"], url_path="get-states")
    def get_states(self, request):
        queryset = State.objects.all()
        serializer = StateSerializer(queryset, many=True)
        return Response(serializer.data)


class GeographicLocationViewSet(viewsets.ModelViewSet):
    queryset = GeographicLocation.objects.all()
    serializer_class = GeographicLocationSerializer
