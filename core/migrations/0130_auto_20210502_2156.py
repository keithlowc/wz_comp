# Generated by Django 3.1.3 on 2021-05-02 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0129_auto_20210502_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_pic',
            field=models.ImageField(default='', null=True, upload_to='profile_pics'),
        ),
    ]
