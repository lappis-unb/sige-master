import logging

from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.events.models import Event
from apps.events.pagination import EventPagination
from apps.events.serializers import EventSerializer
from apps.events.services import calculate_aggregation_events
from apps.transductors.models import (
    Status,
    StatusHistory,
    Transductor,
    TransductorModel,
)
from apps.transductors.serializers import (
    TransductorCreateSerializer,
    TransductorDetailSerializer,
    TransductorListSerializer,
    TransductorModelSerializer,
    TransductorStatusDetailSerializer,
    TransductorStatusSerializer,
)
from apps.transductors.services import calculate_aggregation_status
from apps.utils.helpers import get_boolean

logger = logging.getLogger("apps.transductors.views")


class TransductorModelViewSet(viewsets.ModelViewSet):
    queryset = TransductorModel.objects.all()
    serializer_class = TransductorModelSerializer


class TransductorViewSet(viewsets.ModelViewSet):
    queryset = Transductor.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return TransductorListSerializer
        if self.action == "retrieve":
            return TransductorDetailSerializer
        else:
            return TransductorCreateSerializer

    def list(self, request, *args, **kwargs):
        entity_id = request.query_params.get("entity", None)
        if not entity_id:
            return super().list(request, *args, **kwargs)

        inc_desc = get_boolean(request.query_params.get("inc_desc", "true"))
        transductors = self.get_queryset().entity(entity_id, inc_desc)
        serializer = self.get_serializer(transductors, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)


class TransductorStatusViewSet(viewsets.ModelViewSet):
    queryset = StatusHistory.objects.all()
    serializer_class = TransductorStatusSerializer
    # permission_classes = [CurrentADMINUserOnly]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TransductorStatusDetailSerializer
        return TransductorStatusSerializer

    @action(methods=["get"], detail=False)
    def summary(self, request):
        queryset = self.get_queryset()

        general_aggregation = queryset.aggregate(
            total_active=Count("id", filter=Q(status=Status.ACTIVE)),
            total_broken=Count("id", filter=Q(status=Status.BROKEN)),
            total_disabled=Count("id", filter=Q(status=Status.DISABLED)),
            total_maintenance=Count("id", filter=Q(status=Status.MAINTENANCE)),
            total_other=Count("id", filter=Q(status=Status.OTHER)),
        )

        transductors_summary = []
        transductors_qs = Transductor.objects.all().prefetch_related("status_history")
        for transductor in transductors_qs:
            status_history_qs = StatusHistory.objects.filter(transductor=transductor)
            transductor_status_summary = calculate_aggregation_status(status_history_qs, transductor)
            transductors_summary.append(transductor_status_summary)

        response_data = {
            "general_status_summary": general_aggregation,
            "transductors_status_summary": transductors_summary,
        }
        return Response(response_data, status=status.HTTP_200_OK)
