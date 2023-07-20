# Generated by Django 3.0.14 on 2023-07-19 18:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campi', '0004_auto_20230214_1012'),
        ('unifilar_diagram', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='campi.Campus')),
            ],
        ),
        migrations.CreateModel(
            name='PowerSwitch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('switched_on', models.BooleanField(default=True)),
                ('destination_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='switches_destination', to='unifilar_diagram.Location')),
                ('origin_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='switches_origin', to='unifilar_diagram.Location')),
            ],
        ),
        migrations.CreateModel(
            name='TransmissionLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('destination_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines_destination', to='unifilar_diagram.Location')),
                ('origin_station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines_origin', to='unifilar_diagram.Location')),
            ],
        ),
        migrations.DeleteModel(
            name='Line',
        ),
    ]
