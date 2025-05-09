# Generated by Django 5.0.1 on 2025-04-21 22:13

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0074_product_updated_at_transactionhistory_transaction_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetail',
            name='product_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='vendor_id',
            field=models.UUIDField(default=uuid.UUID('be51c6e7-ee65-4cbb-985a-e3cc0c3cf2e1')),
        ),
    ]
