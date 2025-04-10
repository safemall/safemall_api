# Generated by Django 5.0.1 on 2025-01-31 18:42

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0061_alter_vendorprofile_vendor_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='transaction_pin',
            field=models.CharField(default='', max_length=4),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='vendor_id',
            field=models.UUIDField(default=uuid.UUID('98e9078f-8d5b-44f1-8e4f-05ff99caf5b0')),
        ),
    ]
