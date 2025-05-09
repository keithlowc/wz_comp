# Generated by Django 3.1.3 on 2021-02-05 00:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_configcontroller_competition_email_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompetitionCommunicationEmails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=150)),
                ('body', models.TextField()),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.staffcustomcompetition')),
            ],
        ),
    ]
