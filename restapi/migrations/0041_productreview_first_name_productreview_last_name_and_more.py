# Generated by Django 5.0.1 on 2024-12-28 23:37

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0040_productreview_image_alter_vendorprofile_vendor_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='productreview',
            name='first_name',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='productreview',
            name='last_name',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='vendorprofile',
            name='vendor_id',
            field=models.UUIDField(default=uuid.UUID('2deb8c1f-a2a1-4df4-a884-695dbdc0714e')),
        ),
    ]
