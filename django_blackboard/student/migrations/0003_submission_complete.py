# Generated by Django 3.0.6 on 2020-05-16 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_auto_20200508_2300'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='complete',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
