# Generated by Django 4.2.7 on 2023-12-20 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analitics', '0005_userwatchdata_content_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useractivity',
            name='device_type',
        ),
        migrations.RemoveField(
            model_name='useractivity',
            name='location',
        ),
    ]
