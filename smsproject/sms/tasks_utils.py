import requests, logging
from rest_framework import status
from celery.utils.log import get_task_logger
from sentry_sdk import capture_exception, capture_message

from .models import Engine, Templates, TemplatesEngine


logger = get_task_logger(__name__)

file_handler = logging.FileHandler('celery_tasks.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


# the Engine.name should be setted as the coded engine in this class (check the if's, and inputed engine.name)
class SmsSystem():
    def create_parameters(self, engine, template_tokens, tokens, phone, template_code):
       if engine == 'smsir':
           parameters = []
           for i in range(len(tokens)):
               token = {
                        "name": template_tokens[i],
                        "value": tokens[i]
                    }
               parameters.append(token)
          
           return parameters
       

       elif engine == 'kavenegar':
           params = {}
           params['receptor'] = phone
           for i in range(len(tokens)):
               params[template_tokens[i]] = tokens[i]
           params['template'] = template_code

           return params


    def sms_ir(self, phone, tokens, template_id):
        template = Templates.objects.get(template_id=template_id)
        engine = Engine.objects.get(name='smsir') # need to be adjust
        engine_template = TemplatesEngine.objects.get(engine_key=engine, template_key=template)
        template_code = engine_template.template_code # the template code inside each engin/system
        template_tokens = engine_template.token_keys 
        x_api_key = engine.provider_token

        url = engine.api_url # 'https://api.sms.ir/v1/send/verify' 
        # url = 'https://api.sms.ir/v1/send/verify******' 
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain',
            'x-api-key': x_api_key 
        }
        
        body = {
            "mobile": phone,
            "templateId": template_code,
            
            "parameters": SmsSystem().create_parameters(engine.name, template_tokens, tokens, phone, template_code),
        }

        try:
            response = requests.post(url, json=body, headers=headers)
            return response.json()
        
        except Exception as ex:
            capture_exception(ex)
            return status.HTTP_405_METHOD_NOT_ALLOWED
    

    def kavenegar(self, phone, tokens, template_id):
        template = Templates.objects.get(template_id=template_id)
        engine = Engine.objects.get(name='kavenegar') # need to be adjust
        try:
            engine_template = TemplatesEngine.objects.get(engine_key=engine, template_key=template)

            template_code = engine_template.template_code
            template_tokens = engine_template.token_keys

        except TemplatesEngine.DoesNotExist as ed:
            capture_message('this template doent exist in this engine', level="error")
            capture_exception(ed)
            print('this template doent exist in this engine')

        API_KEY = engine.provider_token
        # url = f'{engine.api_url}/{API_KEY}/verify/lookup.json'
        url = f'{engine.api_url}/{API_KEY}/verify*****/lookup.json'

        try:
            # params = SmsSystem().create_parameters(engine.name, template_tokens, tokens, phone, template_code),
            params = SmsSystem().create_parameters(engine.name, template_tokens, tokens, phone, template_code)

            logger.debug(f"Sending Kavenegar request with parameters: {params}")

        except UnboundLocalError as eu:
            print('UnboundLocalError')
            capture_exception(eu)



        response = requests.post(url, params=params)
        logger.debug(f"Kavenegar Response: {response.json()}")
        return response.json()
