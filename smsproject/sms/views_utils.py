from rest_framework import status
from rest_framework.response import Response
from sentry_sdk import capture_exception, capture_message, add_breadcrumb

from .tasks import process_request


def verify_serializer_validation(verify_serializer, phone, token_value, template_id):
    if not verify_serializer.is_valid():
        add_breadcrumb(message="VerifyRequestsSerializer validation failed", level="warning")
        capture_message("VerifyRequestsSerializer validation failed", level="warning")
    
    try:
        verify_request = verify_serializer.save()
        process_request.delay(verify_request.id, phone, token_value, template_id)
        capture_message("SMS request is being processed", level="info")
    
        return Response({'status': 'Request is being processed'}, status=status.HTTP_202_ACCEPTED)
    
    except Exception as e:
        add_breadcrumb(message="Exception during verify request save or task processing", level="error")
        capture_exception(e)
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        


def sms_serializer_validation(sms_serializer):
    if not sms_serializer.is_valid():
        add_breadcrumb(message="SMS serializer validation failed", level="warning")
        capture_message("SMS serializer validation failed", level="warning")
        return Response(sms_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone = sms_serializer.validated_data['phone']
    token_value = sms_serializer.validated_data['token_value']
    template_id = sms_serializer.validated_data['template_id']
    return phone,token_value,template_id