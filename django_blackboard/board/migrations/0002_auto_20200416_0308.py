# Generated by Django 3.0.4 on 2020-04-16 03:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment.html',
            name='id',
            field=models.UUIDField(default=uuid.UUID('e607315c-ac47-4283-9bc0-880b0b1fc0d8'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='class',
            name='id',
            field=models.UUIDField(default=uuid.UUID('dc8c9fbd-8821-47a2-a76d-659ff059fdcf'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
