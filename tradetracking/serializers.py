from rest_framework import serializers

from tradetracking.models import Filing, Trade


class FilingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filing
        fields = '__all__'

class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = '__all__'
