# Generated by Django 3.0.2 on 2020-04-16 16:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('measurements', '0004_auto_20200416_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tax',
            name='registration_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 16, 16, 47, 21, 188463), verbose_name='registration date'),
        ),
    ]