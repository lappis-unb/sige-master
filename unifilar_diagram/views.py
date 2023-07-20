from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import permissions

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Location, TransmissionLine, PowerSwitch, Campus
from .serializers import LocationSerializer, TransmissionLineSerializer, PowerSwitchSerializer
from django.db.models import Q

class DrawViewSet(ViewSet):
    def list(self, request):
        campus = request.query_params.get('campus')
        lines = TransmissionLine.objects.filter(origin_station__campus=campus)
        serializer = TransmissionLineSerializer(lines, many=True)

        coordinates = []

        for line in serializer.data:
            key = len(coordinates)
            points = [
                {
                    'lat':line['origin_station_latitude'],
                    'lng':line['origin_station_longitude'],
                },
                {
                    'lat':line['destination_station_latitude'],
                    'lng':line['destination_station_longitude']
                },
            ]
            status = line['active']

            coordinates.append({
                    'key':key,
                    'points': points,
                    'status': status
                })

        return Response(coordinates)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_queryset(self):
        campus = self.request.query_params.get('campus')
        if campus is not None:
            self.queryset = self.queryset.filter(campus=campus)

        return self.queryset

class TransmissionLineViewSet(viewsets.ModelViewSet):
    queryset = TransmissionLine.objects.all()
    serializer_class = TransmissionLineSerializer

    def get_queryset(self):
        campus = self.request.query_params.get('campus')
        if campus is not None:
            self.queryset = self.queryset.filter(
                Q(origin_station__campus=campus) | Q(destination_station__campus=campus)
            )

        return self.queryset

class PowerSwitchViewSet(viewsets.ModelViewSet):
    queryset = PowerSwitch.objects.all()
    serializer_class = PowerSwitchSerializer

    def get_queryset(self):
        campus = self.request.query_params.get('campus')
        if campus is not None:
            self.queryset = self.queryset.filter(
                Q(origin_station__campus=campus) | Q(destination_station__campus=campus)
            )

        return self.queryset   