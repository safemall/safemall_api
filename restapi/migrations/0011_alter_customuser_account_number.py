# Generated by Django 5.0.1 on 2024-11-30 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0010_customuser_account_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='account_number',
            field=models.CharField(default='2498575711', max_length=10),
        ),
    ]
