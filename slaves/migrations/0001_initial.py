# Generated by Django 2.1.5 on 2019-10-16 11:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('transductors', '0002_auto_20190930_0943'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator('^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$', 'Incorrect IP address format')])),
                ('port', models.CharField(default='80', max_length=5)),
                ('location', models.CharField(max_length=50)),
                ('broken', models.BooleanField(default=True)),
                ('transductors', models.ManyToManyField(related_name='slave_servers', to='transductors.EnergyTransductor')),
            ],
        ),
    ]
