# SMS Verification System

## Description
This project is a Django-based SMS verification system that integrates with multiple SMS APIs (SMS.IR and Kavenegar) to send verification codes to users. The application uses Celery for asynchronous task processing, Sentry for error tracking and monitoring, and allows for retry mechanisms if one SMS service fails.


## How It Works
This project is designed to reliably send SMS messages using two providers, SMS.IR and Kavenegar, with automatic fallback and error handling. Here’s a breakdown of how it all works:

### 1. Sending an SMS Request 
<!-- **1. Sending an SMS Request** <br /><br /> -->
When a user or client makes a request to the `/sendsms/` endpoint:
   - **Endpoint:** `/sendsms/`
   - **Method:** `POST`
   - The request body includes the phone number, token values, and template ID required to send the SMS.
   - Before sending, the request goes through validation using serializers, ensuring required fields are present.

### 2. Processing the Request with Celery
Once the request is validated:
   - The `SendSmsView` view enqueues a task to Celery, which handles the SMS request in the background.
   - **Benefits of using Celery:** This allows the main API to respond quickly while offloading the SMS sending process to Celery, which processes it asynchronously.

### 3. Sending with Primary Provider: SMS.IR
The `process_request` task first tries to send the SMS using **SMS.IR**:
   - If SMS.IR successfully sends the SMS, the status is recorded as `DONE`.
   - If SMS.IR fails (e.g., due to network issues or provider limitations), Celery will log the failure and proceed to the next step.

### 4. Fallback to Secondary Provider: Kavenegar
If the SMS.IR request fails:
   - The task automatically attempts to send the SMS via **Kavenegar**.
   - If Kavenegar also fails, the system logs the request as `FAILED`.
   - If Kavenegar succeeds, the status is recorded as `DONE`.

### 5. Error Logging and Monitoring with Sentry
The project uses **Sentry** to monitor all errors and warnings during SMS processing:
   - Sentry captures issues such as failed requests and sends alerts, allowing administrators to investigate or troubleshoot problems.
   - All major issues in the SMS sending process are captured, helping maintain system reliability and track performance.

### 6. Tracking Request Status
Each SMS request is tracked in the database with the following information:
   - **Status** (`flag`): Indicates if the request is `PENDING`, `DONE`, or `FAILED`.
   - **Retries** (`tries`): Counts the number of times the system attempted to send the SMS.
   - **System Used** (`system`): Specifies which provider was used (SMS.IR or Kavenegar).

<details>
<summary><strong>Features</strong></summary>

- **Multi-API SMS Sending**: Supports SMS.IR and Kavenegar for sending SMS verification codes.
- **Retry Mechanism**: Automatically retries sending via the alternate service if the primary SMS service fails.
- **Asynchronous Processing**: Uses Celery to process SMS requests asynchronously.
- **Sentry Integration**: Captures and logs error messages to Sentry for monitoring.
- **Transactional Database**: Manages requests in a transactional manner to ensure data consistency.

</details>

<details>
<summary><strong>Technologies Used</strong></summary>

- Django
- Celery
- Redis (for Celery backend)
- Sentry SDK (for error logging)
- 

</details>

## Installation and Setup <br />

### Prerequisites <br />
Clone the repository: <br />

```
git clone https://github.com/hiddenSm/sms-project.git
cd sms-project
```

## Model Relationships & Configuration

<details>
<summary><strong>Model Relationships</strong></summary>

- **Engine**: Represents an SMS provider, storing API details such as `name`, `api_url`, and `provider_token`.
- **Templates**: A template model with a unique `template_id` used across different engines.
- **TemplatesEngine**: Connects **Engine** and **Templates** models by mapping each engine's internal `template_code` to a standard `template_id`, with `token_keys` specifying the required tokens for each template.
- **VerifyRequests**: Logs requests, including sender details, the selected engine (`system`), status (`flag`), number of attempts (`tries`), and token values.

</details>

<details>
<summary><strong>Necessary Configurations</strong></summary>

Before running the project, set up the following configurations in the Django admin:

1. **Engine**:
   - Add each SMS provider (e.g., SMS.IR, Kavenegar) with the necessary API details.

2. **Templates**:
   - Define template entries with unique `template_id` values that are shared across all engines.

3. **TemplatesEngine**:
   - Map each template to the corresponding engine using `template_code` and specify required `token_keys`.

Once configured, `VerifyRequests` will log and track requests as the system operates.

</details> 


## Usage

### API Endpoints
Send SMS Endpoint: `/sendsms/` - Accepts POST requests with `phone, token_value, template_id` parameters to initiate an SMS request. <br >

**Sample Request**:
```
POST /sendsms/
Content-Type: application/json
Authorization: Bearer <your-auth-token>

{
    "phone": "+1234567890",
    "token_value": {"token": "123456"},
    "template_id": 1
}
```

## Background Tasks
   - **process_request**: Processes an SMS request and attempts to send it via SMS.IR. If SMS.IR fails, the request is retried using Kavenegar. <br >
   - **check_pending_requests**: A periodic task to retry any SMS requests with a pending status.


<!---

Access the application: <br />
===================================

Nginx will be available at `http://localhost:80`. <br />

Admin Panel: <br />
===================================
After running the containers, create a superuser for the Django admin panel: <br />
```
docker-compose exec django-app python manage.py createsuperuser
```
Access the admin panel at [http://localhost:80/admin](http://localhost:80/admin). <br /> 

--->
