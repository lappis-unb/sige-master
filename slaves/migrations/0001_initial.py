# Generated by Django 2.1.5 on 2019-04-08 13:22

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Slave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(default='0.0.0.0', max_length=15, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_ip_address', message='Incorrect IP address format', regex='^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$')])),
                ('location', models.CharField(default='', max_length=50)),
                ('transductor_list', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), size=None)),
            ],
        ),
    ]
