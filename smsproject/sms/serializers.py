from rest_framework import serializers
from .models import VerifyRequests

class VerifyRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerifyRequests
        fields = ['request_sender', 'system', 'flag'] # commented?
        fields = ['request_sender', 'phone', 'system', 'flag', 'token_value', 'template_id']

class SendSmsSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    token_value = serializers.JSONField()
    template_id = serializers.IntegerField()