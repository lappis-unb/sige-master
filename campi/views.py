from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import permissions

from .models import Campus
from .models import Transductor
from .serializers import CampusSerializer


class CampusViewSet(viewsets.ModelViewSet):
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        campi = []

        for campus_data in self.queryset:
            campus = campus_data.__dict__
            campus['transductors'] = Transductor.objects.filter(
                campus=campus
            ).count()

            campi.append(campus)

        return campi
