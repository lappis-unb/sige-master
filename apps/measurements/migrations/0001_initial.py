# Generated by Django 5.0.4 on 2024-05-15 18:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('transductors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_consumption', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('active_generated', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('reactive_inductive', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('reactive_capacitive', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('transductor', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='reference_measurement', to='transductors.transductor')),
            ],
            options={
                'verbose_name': 'Reference Measurement',
                'verbose_name_plural': 'Reference Measurements',
            },
        ),
        migrations.CreateModel(
            name='CumulativeMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_consumption', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('active_generated', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('reactive_inductive', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('reactive_capacitive', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('is_calculated', models.BooleanField(default=False)),
                ('collection_date', models.DateTimeField(blank=True, null=True)),
                ('transductor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cumulative_measurements', to='transductors.transductor')),
            ],
            options={
                'verbose_name': 'Cumulative measurement',
                'verbose_name_plural': 'Cumulative Measurements',
                'ordering': ['-collection_date'],
                'indexes': [models.Index(fields=['transductor', 'collection_date'], name='cumu_transductor_date_idx')],
            },
        ),
        migrations.CreateModel(
            name='InstantMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frequency_a', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('frequency_b', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('frequency_c', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('frequency_iec', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('voltage_a', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('voltage_b', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('voltage_c', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('current_a', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('current_b', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('current_c', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('active_power_a', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('active_power_b', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('active_power_c', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('total_active_power', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('reactive_power_a', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('reactive_power_b', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('reactive_power_c', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('total_reactive_power', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('apparent_power_a', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('apparent_power_b', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('apparent_power_c', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('total_apparent_power', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('power_factor_a', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('power_factor_b', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('power_factor_c', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('total_power_factor', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('dht_voltage_a', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('dht_voltage_b', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('dht_voltage_c', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('dht_current_a', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('dht_current_b', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('dht_current_c', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('collection_date', models.DateTimeField(blank=True, null=True)),
                ('transductor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='instant_measurements', to='transductors.transductor')),
            ],
            options={
                'verbose_name': 'Instantaneous measurement',
                'verbose_name_plural': 'Instantaneous Measurements',
                'ordering': ['-collection_date'],
                'indexes': [models.Index(fields=['transductor', 'collection_date'], name='inst_transductor_date_idx')],
            },
        ),
    ]
