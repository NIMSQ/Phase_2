# Generated by Django 5.1.1 on 2024-11-22 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0017_remove_offeredservice_device_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='offeredservice',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='offeredservice',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]
