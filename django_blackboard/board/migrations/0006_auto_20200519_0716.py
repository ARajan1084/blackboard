# Generated by Django 3.0.6 on 2020-05-19 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0005_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='read',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='link',
            field=models.TextField(max_length=200, null=True),
        ),
    ]