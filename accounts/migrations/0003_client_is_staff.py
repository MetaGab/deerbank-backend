# Generated by Django 3.2.9 on 2021-12-06 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_client_is_superuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]
