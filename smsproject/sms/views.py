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




########################################################################################################

## these are for testing the sending api and system, work without celery
## no need to these...
# need to be apply some changing (models configurations)
class KavenegarView(APIView):
    def get(self, request):
        API_KEY = '34343348717A64303550316C517965364D7063577A413D3D'        
        url = f'https://api.kavenegar.com/v1/{API_KEY}/verify/lookup.json'

        params = {
            'receptor': '09378524398',
            'token': '12345',
            'template': 'pingiAcademyBirthNotif',
        }

        response = requests.post(url, params=params)

        return Response(response.json())

class SMSIrView(APIView):
    def post(self, request):
        url = 'https://api.sms.ir/v1/send/verify'

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain',
            'x-api-key': 'leu9beYayciDSpgRHxSJxu9WsR7yG2pdCeoUnukXLef7FqoBRnRCBz05BTRWDjGZ'
        }

        body = {
            "mobile": "9378524398",
            "templateId": 365137,
            "parameters": [
                {
                    "name": "TOKEN",
                    "value": "12345"
                }
            ]
        }

        # response = requests.post(url, json=body, headers=headers)
        # return Response(response.json())
        
        try:
            response = requests.post(url, json=body, headers=headers, timeout=1)
            
            serializer = VerifyRequestsSerializer(data={
                'request_sender': '9378524398', ##
                'system': VerifyRequests.System.SMSIR,
                'flag': VerifyRequests.Flag.DONE
            })

            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(response.json(), status=response.status_code)
        
        except requests.exceptions.Timeout as e:

            serializer = VerifyRequestsSerializer(data={
                'request_sender': '9378524398', ##
                'system': VerifyRequests.System.SMSIR,
                'flag': VerifyRequests.Flag.FAILED
            })

            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'error': str(e)}, status=status.HTTP_408_REQUEST_TIMEOUT)



# def sendsmsview(request):
#     url = 'https://api.sms.ir/v1/send/verify'

#     headers = {
#         'Content-Type': 'application/json',
#         'Accept': 'text/plain',
#         'x-api-key': 'leu9beYayciDSpgRHxSJxu9WsR7yG2pdCeoUnukXLef7FqoBRnRCBz05BTRWDjGZ'
#     }

#     body = {
#         "mobile": "9378524398",
#         "templateId": 365137,
#         "parameters": [
#         {
#             "name": "TOKEN",
#             "value": "12345"
#         }
#         ]
#     }

#     response = requests.post(url, json=body, headers=headers)

#     return JsonResponse(response.json())