import requests#, sentry_sdk
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from sentry_sdk import capture_exception, capture_message, add_breadcrumb, set_user

from .models import VerifyRequests
from .serializers import VerifyRequestsSerializer, SendSmsSerializer
from .tasks import process_request

# Create your views here.

class SendSmsView(APIView):
    def post(self, request):
        # capture_message("Test message to check Sentry integration", level="info")
        if request.user.is_authenticated:
            request_sender = request.user.username
            set_user({"id": request.user.id, "email": request.user.email})

        else:
            capture_message("Unauthorized access attempt", level="warning")
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        sms_serializer = SendSmsSerializer(data=request.data)

        if not sms_serializer.is_valid():
            # return Response({'error': 'Missing phone, token, or template'}, status=status.HTTP_400_BAD_REQUEST)
            add_breadcrumb(message="SMS serializer validation failed", level="warning")
            capture_message("SMS serializer validation failed", level="warning")
            return Response(sms_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = sms_serializer.validated_data['phone']
        token_value = sms_serializer.validated_data['token_value']
        template_id = sms_serializer.validated_data['template_id']


        verify_serializer = VerifyRequestsSerializer(data={
            'request_sender': request_sender,
            'system': VerifyRequests.System.SMSIR,
            'flag': VerifyRequests.Flag.PENDING,
            'phone': phone,
            'token_value': token_value,
            'template_id': template_id,
        })

        if verify_serializer.is_valid():
            try:
                verify_request = verify_serializer.save()
                process_request.delay(verify_request.id, phone, token_value, template_id)
                capture_message("SMS request is being processed", level="info")
            
                return Response({'status': 'Request is being processed'}, status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                add_breadcrumb(message="Exception during verify request save or task processing", level="error")
                capture_exception(e)
                return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            add_breadcrumb(message="VerifyRequestsSerializer validation failed", level="warning")
            capture_message("VerifyRequestsSerializer validation failed", level="warning")
            return Response(verify_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



