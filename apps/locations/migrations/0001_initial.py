# Generated by Django 5.0.4 on 2024-05-15 18:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'City',
                'verbose_name_plural': 'Cities',
            },
        ),
        migrations.CreateModel(
            name='GeographicLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Latitude')),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Longitude')),
                ('zoom_level', models.PositiveSmallIntegerField(default=16, verbose_name='Zoom Level')),
                ('tilt', models.PositiveSmallIntegerField(default=0, verbose_name='Tilt')),
                ('map_type', models.PositiveSmallIntegerField(choices=[(1, 'Roadmap'), (2, 'Satellite'), (3, 'Hybrid'), (4, 'Terrain')], default=1, verbose_name='Map Type')),
            ],
            options={
                'verbose_name': 'Geographic Location',
                'verbose_name_plural': 'Geographic Locations',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.PositiveSmallIntegerField(verbose_name='IBGE Code')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('acronym', models.CharField(max_length=2, verbose_name='Acronym')),
            ],
            options={
                'verbose_name': 'State',
                'verbose_name_plural': 'States',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255, verbose_name='Address')),
                ('number', models.CharField(blank=True, max_length=10, verbose_name='Number')),
                ('complement', models.CharField(blank=True, max_length=255, verbose_name='Complement')),
                ('zip_code', models.CharField(max_length=20, verbose_name='CEP')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locations.city', verbose_name='City')),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
            },
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cities', to='locations.state', verbose_name='State'),
        ),
    ]
