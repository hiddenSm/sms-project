from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Engine(models.Model):
    name = models.CharField(max_length=256)
    api_url = models.CharField(max_length=256)
    provider_token = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.name

class Templates(models.Model):
    name = models.CharField(max_length=256)
    template_id = models.IntegerField() # administrator setted code for each template (for all the engines/systems)

    def __str__(self) -> str:
        return f'{self.template_id}'

class TemplatesEngine(models.Model):
    engine_key = models.ForeignKey(Engine, on_delete=models.CASCADE)
    template_key = models.ForeignKey(Templates, on_delete=models.CASCADE) # the id that setted in Templates model by administrator
    template_code = models.CharField(max_length=256) # code/name of each template inside each engine(system) provider
    token_keys = models.JSONField()

    def __str__(self) -> str:
        return f'{self.template_code} - {self.engine_key}'

class VerifyRequests(models.Model):
    class Flag(models.TextChoices):
        PENDING = "W", _("WAITING")
        ONGOING = "O", _("OnGoing")
        DONE = "P", _("PASSED")
        # RETRY = "R", _("ReTry")
        FAILED = "F", _("Failed")

    class System(models.TextChoices):
        SMSIR = "SI", _("SMS.IR")
        KAVENEGAR = "KN", _("KAVENEGAR")

    system = models.CharField(max_length=2, choices=System, default=System.SMSIR)

    flag = models.CharField(max_length=2, choices=Flag, default=Flag.PENDING)

    request_sender = models.CharField(max_length=256)

    tries = models.IntegerField(default=0)

    phone = models.CharField(max_length=15, blank=True, null=True)
    token_value = models.JSONField(blank=True, null=True)
    template_id = models.CharField(max_length=255, blank=True, null=True)