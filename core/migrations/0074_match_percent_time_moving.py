# Generated by Django 3.1.3 on 2021-04-02 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0073_auto_20210402_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='percent_time_moving',
            field=models.FloatField(null=True),
        ),
    ]
