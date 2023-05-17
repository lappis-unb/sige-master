import json

from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from campi.models import Campus
from slaves.models import Slave
from users.permissions import CurrentADMINUserOnly

from .api import *
from .models import EnergyTransductor
from .serializers import AddToServerSerializer, EnergyTransductorListSerializer, EnergyTransductorSerializer


class EnergyTransductorViewSet(viewsets.ModelViewSet):
    queryset = EnergyTransductor.objects
    serializer_class = EnergyTransductorSerializer
    permission_classes = (
        permissions.AllowAny | CurrentADMINUserOnly,
    )  # Para testes de Admin, retirar os permissions.AllowAny

    def get_queryset(self):
        campus_id = self.request.query_params.get("campus_id")

        transductors = []
        try:
            transductors = self.get_transductors_by_campus_id(campus_id)
        except EnergyTransductor.DoesNotExist:
            raise APIException("Campus Id does not match with any campus")

        # return sorted(
        #     transductors,
        #     key=lambda item: (item.campus.name, item.name)
        # )
        return transductors

    def get_transductors_by_campus_id(self, campus_id):
        if campus_id:
            return self.filter_transductors_by_campus_id(campus_id)
        return EnergyTransductor.objects.all()

    def filter_transductors_by_campus_id(self, campus_id):
        return self.queryset.filter(campus=self.get_campus_id(campus_id))

    def get_campus_id(campus_id):
        return Campus.objects.get(id=campus_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            if instance.slave_server is not None:
                if self.status_code_is_not_204(instance):
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            instance.delete()
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    def status_code_is_not_204(self, instance):
        return self.delete(instance).status_code != 204

    def delete(self, instance):
        return delete_transductor(instance.id_in_slave, instance, instance.slave_server)


class EnergyTransductorListViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = EnergyTransductorListSerializer
    # Para testes de Admin, retirar os permissions.AllowAny
    permission_classes = (permissions.AllowAny | CurrentADMINUserOnly,) 
    
    def get_queryset(self):
        transductors = EnergyTransductor.objects.all()
        slaves = Slave.objects.all()
        transductorList = {}
        for transductor in transductors:
            prec = transductor.events_failedconnectiontransductorevent.filter(ended_at__isnull=True).count()
            crit = transductor.events_voltagerelatedevent.filter(ended_at__isnull=True).count()
            last72h = transductor.events_failedconnectiontransductorevent.filter(
                Q(ended_at__isnull=True)
                | Q(ended_at__range=[timezone.now() - timezone.timedelta(days=3), timezone.now()])
            ).count()
            last72h = (
                last72h
                + transductor.events_voltagerelatedevent.filter(
                    Q(ended_at__isnull=True)
                    | Q(ended_at__range=[timezone.now() - timezone.timedelta(days=3), timezone.now()])
                ).count()
            )
            transductorInformation = {
                "id": transductor.pk,
                "serial_number": transductor.serial_number,
                "campus": transductor.campus.name,
                "name": transductor.name,
                "active": transductor.active,
                "model": transductor.model,
                "grouping": transductor.grouping.all(),
                "current_precarious_events_count": prec,
                "current_critical_events_count": crit,
                "events_last72h": last72h,
            }
            transductor_id = transductor.pk
            transductorList[transductor.pk] = transductorInformation
        for slave in slaves:
            slave_transductors = slave.transductors.all()
            for transductor in slave_transductors:
                transductor_id = transductor.pk
                count = transductorList[transductor_id]["current_precarious_events_count"]
                count = count + slave.events_failedconnectionslaveevent.filter(ended_at__isnull=True).count()
                transductorList[transductor_id]["current_precarious_events_count"] = count
                count = transductorList[transductor_id]["events_last72h"]
                count = (
                    count
                    + slave.events_failedconnectionslaveevent.filter(
                        Q(ended_at__isnull=True)
                        | Q(ended_at__range=[timezone.now() - timezone.timedelta(days=3), timezone.now()])
                    ).count()
                )
                transductorList[transductor_id]["events_last72h"] = count
        response = []
        for item in transductorList.values():
            response.append(item)

        # Sorting response by (campus, name)
        return sorted(response, key=lambda item: (item["campus"], item["name"]))
