# Generated by Django 3.1.3 on 2021-04-02 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0072_match_longest_streak'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='duration',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='utc_start_time',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
