# Generated by Django 5.1.1 on 2024-09-15 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0003_verifyrequests_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verifyrequests',
            name='token_value',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
