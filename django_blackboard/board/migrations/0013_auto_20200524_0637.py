# Generated by Django 3.0.6 on 2020-05-24 06:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0012_auto_20200524_0636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='date_posted',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
