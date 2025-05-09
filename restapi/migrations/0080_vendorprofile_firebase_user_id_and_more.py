# Generated by Django 5.0.1 on 2025-04-26 18:22

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0079_customuser_firebase_user_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendorprofile',
            name='firebase_user_id',
            field=models.CharField(default='', max_length=40),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='vendor_id',
            field=models.UUIDField(default=uuid.UUID('cb73a9a9-bb8a-4805-9d49-bc48d26b5c09')),
        ),
    ]
