from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import permissions

from .models import Line
from .serializers import LineSerializer


class LineViewSet(viewsets.ModelViewSet):
    serializer_class = LineSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Line.objects.all()

    def get_queryset(self):
        campus = self.request.query_params.get('campus')
        if campus is not None:
            self.queryset = self.queryset.filter(campus=campus)

        return self.queryset
