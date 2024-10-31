from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth.models import User
from .models import VerifyRequests
from .tasks import process_request, check_pending_requests
# import os

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

class SendSmsViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.url = reverse('sendsms') 

        self.verify_request = VerifyRequests.objects.create(
            request_sender="test_user",
            system=VerifyRequests.System.SMSIR,
            flag=VerifyRequests.Flag.PENDING,
            phone="09123456789",
            token_value="123456",
            template_id=1,
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)
    
    @patch('sms.views.process_request.delay')
    def test_send_sms_authenticated(self, mock_process_request):
        self.authenticate()
        data = {
            'phone': '1234567890',
            'token_value': '123456',
            'template_id': 1
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(VerifyRequests.objects.filter(phone='1234567890').exists())
        verify_request = VerifyRequests.objects.get(phone='1234567890')
        mock_process_request.assert_called_once_with(verify_request.id, '1234567890', '123456', 1)

    def test_send_sms_unauthenticated(self):
        data = {
            'phone': '1234567890',
            'token_value': '123456',
            'template_id': 1
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(VerifyRequests.objects.filter(phone='1234567890').exists())

    def test_send_sms_invalid_data(self):
        self.authenticate()
        data = {
            'phone': '1234567890',
            # Missing token_value and template_id
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('sms.tasks.SmsSystem.sms_ir')
    @patch('sms.tasks.SmsSystem.kavenegar')
    def test_process_request_sms_ir_success(self, mock_kavenegar, mock_sms_ir):
        mock_sms_ir.return_value = {'status': 1}
        mock_kavenegar.return_value = {}

        verify_request = VerifyRequests.objects.create(
            request_sender=self.user.username,
            system=VerifyRequests.System.SMSIR,
            flag=VerifyRequests.Flag.PENDING,
            phone='1234567890',
            token_value='123456',
            template_id=1,
        )

        # from sms.tasks import process_request
        process_request(verify_request.id, verify_request.phone, verify_request.token_value, verify_request.template_id)

        verify_request.refresh_from_db()
        self.assertEqual(verify_request.flag, VerifyRequests.Flag.DONE)

    @patch('sms.tasks.SmsSystem.sms_ir')
    @patch('sms.tasks.SmsSystem.kavenegar')
    def test_process_request_sms_ir_fail_kavenegar_success(self, mock_kavenegar, mock_sms_ir):
        mock_sms_ir.return_value = {'status': 0}
        mock_kavenegar.return_value = {'return': {'status': 200}}

        verify_request = VerifyRequests.objects.create(
            request_sender=self.user.username,
            system=VerifyRequests.System.SMSIR,
            flag=VerifyRequests.Flag.ONGOING,
            phone='1234567890',
            token_value='123456',
            template_id=1,
        )

        # from sms.tasks import process_request
        process_request(verify_request.id, verify_request.phone, verify_request.token_value, verify_request.template_id)

        verify_request.refresh_from_db()
        self.assertEqual(verify_request.system, VerifyRequests.System.KAVENEGAR)
        self.assertEqual(verify_request.flag, VerifyRequests.Flag.DONE)

    @patch('sms.tasks.SmsSystem.sms_ir')
    @patch('sms.tasks.SmsSystem.kavenegar')
    def test_process_request_both_fail(self, mock_kavenegar, mock_sms_ir):
        mock_sms_ir.return_value = {'status': 0}
        mock_kavenegar.return_value = {'return': {'status': 404}}

        verify_request = VerifyRequests.objects.create(
            request_sender=self.user.username,
            system=VerifyRequests.System.SMSIR,
            flag=VerifyRequests.Flag.ONGOING,
            phone='1234567890',
            token_value='123456',
            template_id=1,
        )

        # from sms.tasks import process_request
        process_request(verify_request.id, verify_request.phone, verify_request.token_value, verify_request.template_id)

        verify_request.refresh_from_db()
        self.assertEqual(verify_request.flag, VerifyRequests.Flag.FAILED)
        # self.assertEqual(verify_request.flag, VerifyRequests.Flag.PENDING)
        self.assertEqual(verify_request.tries, 1)


class CheckPendingRequestsTests(APITestCase):
    @patch('sms.tasks.process_request.delay')
    def test_check_pending_requests(self, mock_process_request):
        VerifyRequests.objects.create(
            request_sender='testuser',
            system=VerifyRequests.System.SMSIR,
            flag=VerifyRequests.Flag.PENDING,
            phone='1234567890',
            token_value='123456',
            template_id=1,
        )

        # from sms.tasks import check_pending_requests
        check_pending_requests()

        pending_request = VerifyRequests.objects.get(phone='1234567890')
        self.assertEqual(pending_request.flag, VerifyRequests.Flag.ONGOING)
        mock_process_request.assert_called_once_with(
            pending_request.id, pending_request.phone, pending_request.token_value, pending_request.template_id
        )