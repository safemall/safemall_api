# Generated by Django 5.0.1 on 2024-11-17 00:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0004_sellerprofile'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SellerProfile',
            new_name='VendorProfile',
        ),
        migrations.AlterModelOptions(
            name='vendorprofile',
            options={'verbose_name': 'vendorprofile', 'verbose_name_plural': 'vendorprofiles'},
        ),
    ]