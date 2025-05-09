# Generated by Django 5.0.1 on 2024-12-29 17:39

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0041_productreview_first_name_productreview_last_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='product_image',
            new_name='vendor_image',
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='vendor_id',
            field=models.UUIDField(default=uuid.UUID('7b8fe1b8-617a-4e5c-bd1f-c8c473c71ab3')),
        ),
    ]
