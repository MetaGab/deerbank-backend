# Generated by Django 3.2.9 on 2021-12-09 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_auto_20211208_2037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='auth_number',
            field=models.CharField(max_length=16),
        ),
    ]
