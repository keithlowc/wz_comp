# Generated by Django 3.1.3 on 2021-04-04 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0083_auto_20210404_1912'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='competition',
        ),
        migrations.AddField(
            model_name='player',
            name='competition',
            field=models.ManyToManyField(related_name='players', to='core.StaffCustomCompetition'),
        ),
        migrations.AlterField(
            model_name='player',
            name='team',
            field=models.ManyToManyField(related_name='players', to='core.StaffCustomTeams'),
        ),
    ]
