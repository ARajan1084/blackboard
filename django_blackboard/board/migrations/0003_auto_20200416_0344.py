# Generated by Django 3.0.4 on 2020-04-16 03:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0002_auto_20200416_0308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='id',
            field=models.UUIDField(default=uuid.UUID('ebc5de31-ad03-4967-8805-331196ba4a3f'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='class',
            name='id',
            field=models.UUIDField(default=uuid.UUID('fc2efe9f-01ae-4cb5-b483-ac45c39530f4'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]