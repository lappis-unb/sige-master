from rest_framework import serializers, viewsets

from .models import Slave
from .serializers import SlaveSerializer


# class SlaveView(APIView):
#     def get(self, request):
#         slaves = Slave.objects.all()
#         serializer = SlaveSerializer(slaves, many=True)
#         return Response({"slaves": slaves})

class SlaveViewSet(viewsets.ModelViewSet):
    queryset = Slave.objects.all()
    serializer_class = SlaveSerializer
