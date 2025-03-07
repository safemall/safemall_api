# Generated by Django 5.0.1 on 2024-12-04 23:17

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0023_orderdetail_created_at_alter_vendorprofile_vendor_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_category',
            field=models.CharField(choices=[('clothes', 'clothes'), ('footwears', 'footwears'), ('accessories', 'accessories'), ('beauty', 'beauty'), ('household', 'household'), ('food', 'food')], default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='vendor_id',
            field=models.UUIDField(default=uuid.UUID('7e41be8c-a10c-4840-8c8a-16bbc92092ba')),
        ),
    ]
