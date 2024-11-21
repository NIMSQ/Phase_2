# Generated by Django 5.1.1 on 2024-10-30 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfferedService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_type', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('device_id', models.CharField(max_length=100, unique=True)),
            ],
        ),
    ]
