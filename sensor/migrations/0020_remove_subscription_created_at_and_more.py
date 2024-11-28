# Generated by Django 5.1.1 on 2024-11-27 16:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0019_rename_data_temperaturedata_humidity_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='temperaturedata',
            name='user',
        ),
        migrations.AddField(
            model_name='temperaturedata',
            name='subscription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sensor.subscription'),
        ),
    ]
