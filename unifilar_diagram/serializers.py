from rest_framework import serializers
from .models import Location, TransmissionLine, PowerSwitch

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id','name', 'latitude', 'longitude','campus']


class TransmissionLineSerializer(serializers.ModelSerializer):
    origin_station_name = serializers.ReadOnlyField(source='origin_station.name')
    destination_station_name = serializers.ReadOnlyField(source='destination_station.name')
    origin_station_latitude = serializers.ReadOnlyField(source='origin_station.latitude')
    origin_station_longitude = serializers.ReadOnlyField(source='origin_station.longitude')
    destination_station_latitude = serializers.ReadOnlyField(source='destination_station.latitude')
    destination_station_longitude = serializers.ReadOnlyField(source='destination_station.longitude')
    campus = serializers.ReadOnlyField(source='origin_station.campus.name')
    type = serializers.SerializerMethodField()

    class Meta:
        model = TransmissionLine
        fields = ['id','origin_station', 'destination_station', 'origin_station_name', 'destination_station_name',
                  'origin_station_latitude', 'origin_station_longitude',
                  'destination_station_latitude', 'destination_station_longitude', 'type','active','campus']

    def get_type(self, obj):
        return 'Line'


class PowerSwitchSerializer(serializers.ModelSerializer):
    origin_station_name = serializers.ReadOnlyField(source='origin_station.name')
    destination_station_name = serializers.ReadOnlyField(source='destination_station.name')
    origin_station_latitude = serializers.ReadOnlyField(source='origin_station.latitude')
    origin_station_longitude = serializers.ReadOnlyField(source='origin_station.longitude')
    destination_station_latitude = serializers.ReadOnlyField(source='destination_station.latitude')
    destination_station_longitude = serializers.ReadOnlyField(source='destination_station.longitude')
    campus = serializers.ReadOnlyField(source='origin_station.campus.id')

    type = serializers.SerializerMethodField()

    class Meta:
        model = PowerSwitch
        fields = ['id','origin_station', 'destination_station', 'origin_station_name', 'destination_station_name',
                  'origin_station_latitude', 'origin_station_longitude',
                  'destination_station_latitude', 'destination_station_longitude', 'type','active','switched_on','campus']

    def get_type(self, obj):
        return 'Switch'