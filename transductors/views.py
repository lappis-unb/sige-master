from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response

from campi.models import Campus
from slaves.models import Slave
from transductors.api import *
from transductors.models import EnergyTransductor
from transductors.serializers import (
    EnergyTransductorListSerializer,
    EnergyTransductorSerializer,
)
from users.permissions import CurrentADMINUserOnly


class EnergyTransductorViewSet(viewsets.ModelViewSet):
    queryset = EnergyTransductor.objects.all().order_by("-id")
    serializer_class = EnergyTransductorSerializer
    permission_classes = [permissions.AllowAny | CurrentADMINUserOnly]

    def get_queryset(self):
        campus_id = self.request.query_params.get("campus_id")

        if campus_id:
            try:
                campus = Campus.objects.get(id=campus_id)
                return EnergyTransductor.objects.filter(campus=campus).order_by("campus__name", "name")

            except Campus.DoesNotExist:
                raise APIException("Campus Id does not match with any campus")

        return self.queryset.order_by("campus__name", "-id")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        serializer.delete(instance)
        return Response({"message": "Object deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    # TODO Terminar os testes e trocar de chamadas sicnronas para assincronas
    # def destroy(self):
    #     instance = self.get_object()

    #     if instance.slave_server is None:
    #         self.perform_destroy(instance)
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     try:
    #         async_to_sync(delete_from_slave)(instance)

    #     except Exception as e:
    #         instance.pending_deletion = True
    #         instance.active = False
    #         instance.save()
    #         return Response(status=status.HTTP_202_ACCEPTED, data={"detail": "Object marked for deletion."})

    # def create(self, request):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     instance = serializer.save()

    #     if instance.slave_server is not None:
    #         response = async_to_sync(create_on_slave)(instance)
    #         if response != 201:
    #             instance.pending_sync = True
    #             instance.active = False
    #             instance.save()

    #     headers = self.get_success_headers(serializer.data)
    #     print("._." * 80, flush=True)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # def update(self, request):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     instance = serializer.save()

    #     if instance.slave_server is not None:
    #         response = async_to_sync(update_on_slave)(instance)
    #         if response != 200:
    #             instance.pending_sync = True
    #             instance.active = False
    #             instance.save()
    #             return Response(status=status.HTTP_202_ACCEPTED, data={"detail": "Object marked for update."})

    # return Response(serializer.data, status=status.HTTP_200_OK)


class EnergyTransductorListViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
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
