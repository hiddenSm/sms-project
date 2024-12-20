import logging#, requests
from celery import shared_task
from celery.utils.log import get_task_logger
# from rest_framework import status
from django.db import transaction
from sentry_sdk import capture_exception, capture_message

from .tasks_utils import SmsSystem
from .models import VerifyRequests#, Engine, Templates, TemplatesEngine

logger = get_task_logger(__name__)

file_handler = logging.FileHandler('celery_tasks.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# need to make the sentry c_messages and c_exceptions better and well-suited

@shared_task()
def process_request(request_id, phone, token_value, template_id):
    try:
        with transaction.atomic():
            verify_request = VerifyRequests.objects.select_for_update().get(id=request_id)

            if verify_request.flag == VerifyRequests.Flag.PENDING:
                verify_request.tries =+ 1
                response = SmsSystem().sms_ir(phone, token_value, template_id)
                try:
                    if response.get('status') == 1:
                        verify_request.flag = VerifyRequests.Flag.DONE
                        logger.info(f'Verify code sent to {phone} via SMS.IR. \n')
                except:
                    verify_request.flag = VerifyRequests.Flag.PENDING
                    logger.info(
                        f"Attempt to send sms to {phone} via SMS.IR is failed.\n"
                        f"will try to send sms to {phone} via KAVENEGAR.\n"
                    )
                    capture_message("sms.ir failed. trying kavenegar", level="warning")
                
            elif verify_request.flag == VerifyRequests.Flag.ONGOING:
                    verify_request.system = VerifyRequests.System.KAVENEGAR
                    response = SmsSystem().kavenegar(phone, token_value, template_id)
                    if response.get('return', {}).get('status') == 200:
                        verify_request.flag = VerifyRequests.Flag.DONE
                        verify_request.tries =+ 1
                        logger.info(f'Verify code sent to {phone} via KAVENEGAR')

                    else:
                        verify_request.flag = VerifyRequests.Flag.FAILED
                        verify_request.tries =+ 1

                        logger.info(f"Attempt to send sms to {phone} via KAVENEGAR is failed.\n")

                        logger.info(f"Send user request again!!\n"
                            f"result: requester: {verify_request.request_sender} -- "
                            f"user phone: {phone} -- "
                            f"last try flag: {verify_request.get_flag_display()} -- "
                            f"system: {verify_request.get_system_display()} -- "
                            f"tries: {verify_request.tries}."
                        )
                        capture_message("Tries are full, Send user request again!! treid with both systems", level="warning")

            verify_request.save()

    except VerifyRequests.DoesNotExist as ed:
        capture_exception(ed)
        logger.error(f'Verify request does not exist: {ed}')

    except Exception as e:
        capture_exception(e)
        logger.error(f'Exception during SMS processing: {e}')


@shared_task
def check_pending_requests():
    pending_requests = VerifyRequests.objects.filter(flag=VerifyRequests.Flag.PENDING)

    rp_request = [] 
    for request in pending_requests:
        rp_request.append(request)

    pending_requests.update(flag=VerifyRequests.Flag.ONGOING)

    for request in rp_request:
        process_request.delay(
            request.id, 
            request.phone, 
            request.token_value, 
            request.template_id
        )

        logger.info(f'trying again to send code to {request.phone}')
