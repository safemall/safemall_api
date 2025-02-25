# Generated by Django 5.0.1 on 2024-12-20 21:12

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0032_alter_customuser_fcm_token_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetail',
            name='vendor_id',
            field=models.CharField(blank=True, max_length=90, null=True),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='vendor_id',
            field=models.UUIDField(default=uuid.UUID('afe8694b-b0e3-42e2-aade-0a43c7136496')),
        ),
    ]
