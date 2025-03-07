# Generated by Django 5.0.1 on 2024-12-02 16:21

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0020_alter_orderdetail_order_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetail',
            name='order_id',
            field=models.UUIDField(default=''),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='order_otp_token',
            field=models.CharField(default='', max_length=8),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='vendor_id',
            field=models.UUIDField(default=uuid.UUID('d0a8004e-4263-4e49-9e5d-ee17b6eed9e6')),
        ),
    ]
