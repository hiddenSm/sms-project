# SMS Verification System

## Description
This project is a Django-based SMS verification system that integrates with multiple SMS APIs (SMS.IR and Kavenegar) to send verification codes to users. The application uses Celery for asynchronous task processing, Sentry for error tracking and monitoring, and allows for retry mechanisms if one SMS service fails.


## How It Works

<details>
<summary><strong>Sending an SMS Request</strong></summary>

When a user or client makes a request to the `/sendsms/` endpoint:
- **Endpoint:** `/sendsms/`
- **Method:** `POST`
- The request body includes the phone number, token values, and template ID required to send the SMS.
- Before sending, the request goes through validation using serializers, ensuring required fields are present.

</details>

<details>
<summary><strong>Processing the Request with Celery</strong></summary>

Once the request is validated:
- The `SendSmsView` view enqueues a task to Celery, which handles the SMS request in the background.
- **Benefits of using Celery:** This allows the main API to respond quickly while offloading the SMS sending process to Celery, which processes it asynchronously.

</details>

<details>
<summary><strong>Sending with Primary Provider: SMS.IR</strong></summary>

The `process_request` task first tries to send the SMS using **SMS.IR**:
- If SMS.IR successfully sends the SMS, the status is recorded as `DONE`.
- If SMS.IR fails (e.g., due to network issues or provider limitations), Celery will log the failure and proceed to the next step.

</details>

<details>
<summary><strong>Fallback to Secondary Provider: Kavenegar</strong></summary>

If the SMS.IR request fails:
- The task automatically attempts to send the SMS via **Kavenegar**.
- If Kavenegar also fails, the system logs the request as `FAILED`.
- If Kavenegar succeeds, the status is recorded as `DONE`.

</details>

<details>
<summary><strong>Error Logging and Monitoring with Sentry</strong></summary>

The project uses **Sentry** to monitor all errors and warnings during SMS processing:
- Sentry captures issues such as failed requests and sends alerts, allowing administrators to investigate or troubleshoot problems.
- All major issues in the SMS sending process are captured, helping maintain system reliability and track performance.

</details>

<details>
<summary><strong>Tracking Request Status</strong></summary>

Each SMS request is tracked in the database with the following information:
- **Status** (`flag`): Indicates if the request is `PENDING`, `DONE`, or `FAILED`.
- **Retries** (`tries`): Counts the number of times the system attempted to send the SMS.
- **System Used** (`system`): Specifies which provider was used (SMS.IR or Kavenegar).

</details>

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


## Usage

### API Endpoints
Send SMS Endpoint: `/sendsms/` - Accepts POST requests with `phone, token_value, template_id` parameters to initiate an SMS request. <br >

**Swagger**:
You can check the request and response samples on `/swagger/`.

<!--- 
## Background Tasks
   - **process_request**: Processes an SMS request and attempts to send it via SMS.IR. If SMS.IR fails, the request is retried using Kavenegar. <br >
   - **check_pending_requests**: A periodic task to retry any SMS requests with a pending status.
--->


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


## Access the application:
To run the SMS Verification System, you need to start the Django development server, Celery worker, and Celery beat scheduler. Follow these steps:
<br />

### 1. Start the Django Development Server
Run the following command to start the Django server:

```
python manage.py runserver
```
This command will start the server at http://127.0.0.1:8000/ by default. You can access the application via this URL in your web browser.

### 2. Start the Celery Worker
In a new terminal window, navigate to your project directory and run the Celery worker:

```
celery -A smsproject worker -l INFO --concurrency=1
```
This command will start the Celery worker, which processes the SMS requests in the background. The --concurrency=1 flag sets the number of concurrent worker processes to 1. Adjust this value based on your system's capabilities and needs.

### 3. Start the Celery Beat Scheduler
In another terminal window, start the Celery beat scheduler to handle periodic tasks:

```
celery -A smsproject beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
This command ensures that scheduled tasks, such as retrying pending SMS requests, are executed at the specified intervals. The DatabaseScheduler allows for scheduling based on entries in the database.





<!-- ############################################# -->

<!--- 
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
--->

<!---
## How It Works
This project is designed to reliably send SMS messages using two providers, SMS.IR and Kavenegar, with automatic fallback and error handling. Here’s a breakdown of how it all works:

### 1. Sending an SMS Request 
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
--->
