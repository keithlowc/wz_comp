# Generated by Django 3.1.3 on 2021-04-28 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0124_regiment_invite_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regiment',
            name='name',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
