# Generated by Django 5.0.1 on 2025-01-22 18:25

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0052_transactionhistory_sender_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionhistory',
            name='recipient',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='vendor_id',
            field=models.UUIDField(default=uuid.UUID('9d2c6458-e4ab-43a2-b196-36ab6ba801bf')),
        ),
    ]
