# Generated by Django 3.0.4 on 2020-04-30 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0008_auto_20200430_0433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='cal_credentials',
            field=models.FileField(default=None, upload_to='tokens/5171991'),
        ),
    ]
