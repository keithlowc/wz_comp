# Generated by Django 3.1.3 on 2021-04-16 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0095_rocketleague'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rocketleague',
            name='player_1_rank',
            field=models.CharField(choices=[('Gold', 'Gold'), ('Platinum', 'Platinum')], max_length=50),
        ),
        migrations.AlterField(
            model_name='rocketleague',
            name='player_2_rank',
            field=models.CharField(choices=[('Gold', 'Gold'), ('Platinum', 'Platinum')], max_length=50),
        ),
        migrations.AlterField(
            model_name='rocketleague',
            name='player_3_rank',
            field=models.CharField(choices=[('Gold', 'Gold'), ('Platinum', 'Platinum')], max_length=50),
        ),
    ]
