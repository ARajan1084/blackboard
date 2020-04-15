# Generated by Django 3.0.4 on 2020-04-14 20:45

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0007_auto_20200414_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='id',
            field=models.UUIDField(default=uuid.UUID('63b661ce-b4fe-4936-8a87-b258e407aa76'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterOrderWithRespectTo(
            name='assignment',
            order_with_respect_to='id',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='assignment_id',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='category_id',
        ),
    ]
