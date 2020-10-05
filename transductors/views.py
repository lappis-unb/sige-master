import json

from django.shortcuts import render

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers, viewsets, permissions, status

from .api import *
from slaves.models import Slave
from .models import EnergyTransductor
from .serializers import EnergyTransductorSerializer, AddToServerSerializer
from django.http import Http404
from .serializers import EnergyTransductorSerializer, \
    AddToServerSerializer, EnergyTransductorListSerializer

from django.utils import timezone

from rest_framework import mixins

from django.db.models import Q


class EnergyTransductorViewSet(viewsets.ModelViewSet):
    queryset = EnergyTransductor.objects
    serializer_class = EnergyTransductorSerializer
    permission_classes = (permissions.AllowAny,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            if instance.slave_server is not None:
                response = delete_transductor(
                    instance.id_in_slave, instance, instance.slave_server)
                if response.status_code is not 204:
                    return Response(status=status.HTTP_400_BAD_REQUEST) 
            instance.delete()
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class EnergyTransductorListViewSet(viewsets.GenericViewSet, 
                                   mixins.RetrieveModelMixin, 
                                   mixins.ListModelMixin):
    serializer_class = EnergyTransductorListSerializer

    def get_queryset(self):
        transductors = EnergyTransductor.objects.all()
        slaves = Slave.objects.all()
        transductorList = {}
        for transductor in transductors:
            crit = transductor.events_failedconnectiontransductorevent.filter(
                ended_at__isnull=True).count()
            prec = transductor.events_voltagerelatedevent.filter(
                ended_at__isnull=True).count()
            last72h = transductor. \
                events_failedconnectiontransductorevent.filter(
                    Q(ended_at__isnull=True) | Q(ended_at__range=[
                        timezone.now() - timezone.timedelta(days=3), 
                        timezone.now()
                    ])).count()
            last72h = last72h + transductor.events_voltagerelatedevent.filter(
                Q(ended_at__isnull=True) | Q(ended_at__range=[
                    timezone.now() - timezone.timedelta(days=3), 
                    timezone.now()
                ])).count()
            transductorInformation = {
                'id': transductor.pk,
                'serial_number': transductor.serial_number,
                'campus': transductor.campus.name,
                'name': transductor.name,
                'active': transductor.active,
                'model': transductor.model,
                'grouping': transductor.grouping.all(),
                'current_precarious_events_count': prec,
                'current_critical_events_count': crit,
                'events_last72h': last72h
            }
            transductor_id = transductor.pk
            transductorList[transductor.pk] = transductorInformation
        for slave in slaves:
            slave_transductors = slave.transductors.all()
            for transductor in slave_transductors:
                transductor_id = transductor.pk
                count = transductorList[transductor_id][
                    'current_precarious_events_count']
                count = count + \
                    slave.events_failedconnectionslaveevent.filter(
                        ended_at__isnull=True).count()
                transductorList[transductor_id][
                    'current_precarious_events_count'] = count
                count = transductorList[transductor_id]['events_last72h']
                count = count + \
                    slave.events_failedconnectionslaveevent.filter(
                        Q(ended_at__isnull=True) | Q(ended_at__range=[
                            timezone.now() - timezone.timedelta(days=3), 
                            timezone.now()
                        ])).count()
                transductorList[transductor_id]['events_last72h'] = count
        response = []
        for item in transductorList.values():
            response.append(item)
        return response
