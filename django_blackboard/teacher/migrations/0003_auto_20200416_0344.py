# Generated by Django 3.0.4 on 2020-04-16 03:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0002_auto_20200416_0308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
