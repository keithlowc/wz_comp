# Generated by Django 3.1.3 on 2021-04-27 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0112_auto_20210427_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='invite_code',
            field=models.CharField(default='013DDB', max_length=50),
        ),
    ]
