# Generated by Django 5.0.1 on 2024-11-28 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('restapi', '0007_alter_customuser_options_remove_customuser_groups_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='user_set', to='auth.group'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, related_name='user_set', to='auth.permission'),
        ),
    ]
