# Generated by Django 3.1.3 on 2021-04-26 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0097_profile'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'User Profile', 'verbose_name_plural': 'User Profiles'},
        ),
        migrations.AddField(
            model_name='profile',
            name='profile_name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
