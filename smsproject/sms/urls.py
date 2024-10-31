from django.urls import path
from . import views

urlpatterns = [
    path('sendsms/', views.SendSmsView.as_view(), name='sendsms'),
    # path('smsir/', views.SMSIrView.as_view(), name='smsir'),
    # path('kavenegar/', views.KavenegarView.as_view(), name='egar'),
]
