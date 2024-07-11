# Generated by Django 5.0.6 on 2024-06-22 05:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='event_type',
        ),
        migrations.RemoveField(
            model_name='trigger',
            name='event_type',
        ),
        migrations.RemoveField(
            model_name='event',
            name='measurement_trigger',
        ),
        migrations.RemoveField(
            model_name='trigger',
            name='notes',
        ),
        migrations.AddField(
            model_name='event',
            name='trigger',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events_trigger', to='events.trigger'),
        ),
        migrations.AddField(
            model_name='trigger',
            name='category',
            field=models.IntegerField(blank=True, choices=[(1, 'Voltage'), (2, 'Connection'), (3, 'Consumption'), (4, 'Generation'), (5, 'Measurement'), (6, 'Other')], null=True),
        ),
        migrations.AddField(
            model_name='trigger',
            name='notification_message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='trigger',
            name='severity',
            field=models.IntegerField(blank=True, choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical')], null=True),
        ),
        migrations.AddField(
            model_name='cumulativemeasurementtrigger',
            name='operator',
            field=models.CharField(blank=True, choices=[('gt', '> (Greater Than)'), ('gte', '>= (Greater Than or Equal)'), ('lt', '< (Less Than)'), ('lte', '<= (Less Than or Equal)'), ('exact', '== (Equal)'), ('ne', '!= (Not Equal)')], max_length=5, null=True),
        ),
        migrations.DeleteModel(
            name='EventType',
        ),
    ]
