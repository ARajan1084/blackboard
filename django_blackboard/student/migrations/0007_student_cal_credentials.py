# Generated by Django 3.0.4 on 2020-04-30 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0006_auto_20200417_0830'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='cal_credentials',
            field=models.FileField(default=None, upload_to='tokens/5171991'),
            preserve_default=False,
        ),
    ]
