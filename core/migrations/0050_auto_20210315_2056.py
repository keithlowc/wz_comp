# Generated by Django 3.1.3 on 2021-03-15 20:56

import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_auto_20210315_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffcustomcompetition',
            name='competition_name',
            field=models.CharField(max_length=150, null=True, unique=True, validators=[core.validators.validate_competition_name]),
        ),
    ]
