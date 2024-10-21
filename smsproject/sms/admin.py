from django.contrib import admin
from .models import VerifyRequests, Engine, Templates, TemplatesEngine

# Register your models here.

admin.site.register(Engine)
admin.site.register(Templates)
admin.site.register(TemplatesEngine)
admin.site.register(VerifyRequests)