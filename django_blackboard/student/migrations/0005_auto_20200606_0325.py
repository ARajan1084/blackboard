# Generated by Django 3.0.6 on 2020-06-06 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0004_auto_20200531_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='score',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=8, null=True),
        ),
    ]
