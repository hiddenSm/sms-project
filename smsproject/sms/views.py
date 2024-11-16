from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from sentry_sdk import capture_message, set_user#, capture_exception, add_breadcrumb
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .views_utils import sms_serializer_validation, verify_serializer_validation
from .models import VerifyRequests
from .serializers import VerifyRequestsSerializer, SendSmsSerializer
# from .tasks import process_request

# Create your views here.

class SendSmsView(APIView):
    @swagger_auto_schema(
        operation_summary="Send an SMS",
        operation_description="This endpoint allows authenticated users to send an SMS.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number to send SMS'),
                'token_value': openapi.Schema(type=openapi.TYPE_OBJECT, description='Token value for verification'),
                'template_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the template to use'),
            },
            required=['phone', 'token_value', 'template_id'],
        ),
        responses={
            202: openapi.Response('Request is being processed'),
            400: openapi.Response('Invalid input', schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)})),
            401: openapi.Response('Unauthorized'),
            500: openapi.Response('Internal server error'),
        }
    )

    def post(self, request):
        if not request.user.is_authenticated:
            capture_message("Unauthorized access attempt", level="warning")
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        request_sender = request.user.username
        set_user({"id": request.user.id, "email": request.user.email})

        sms_serializer = SendSmsSerializer(data=request.data)

        phone, token_value, template_id = sms_serializer_validation(sms_serializer)
        # phone, token_value, template_id = self.sms_serializer_validation(sms_serializer)

        verify_serializer = VerifyRequestsSerializer(data={
            'request_sender': request_sender,
            'system': VerifyRequests.System.SMSIR,
            'flag': VerifyRequests.Flag.PENDING,
            'phone': phone,
            'token_value': token_value,
            'template_id': template_id,
        })


        # return self.verify_serializer_validation(verify_serializer, phone, token_value, template_id)
        return verify_serializer_validation(verify_serializer, phone, token_value, template_id)