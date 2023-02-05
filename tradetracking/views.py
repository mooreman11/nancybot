# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from tradetracking.congressional_tracking import update_congressional_data, parse_congressperson


class UpdateStockData(APIView):
    def get(self, request):
        try:
            data = update_congressional_data()
            return Response(data, 200)
        except Exception as e:
            return Response(str(e), 500)


class CongressionalStock(APIView):
    def get(self, request):
        try:
            data = parse_congressperson()
            return Response(data, 200)
        except Exception as e:
            return Response(str(e), 500)
