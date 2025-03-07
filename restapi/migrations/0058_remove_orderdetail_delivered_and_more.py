# Generated by Django 5.0.1 on 2025-01-24 13:17

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0057_pending_quantity_alter_vendorprofile_vendor_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdetail',
            name='delivered',
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='order_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')], default='Pending', max_length=50),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='payment_status',
            field=models.CharField(choices=[('Paid, Pending Confirmation', 'Paid, Pending Confirmation'), ('Paid and Confirmed', 'Paid and Confirmed'), ('Payment Reversed', 'Payment Reversed')], default='Paid, Pending Confirmation', max_length=60),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='vendor_id',
            field=models.UUIDField(default=uuid.UUID('a083fced-0fcf-4a4d-ae24-4f99a0202d34')),
        ),
    ]
