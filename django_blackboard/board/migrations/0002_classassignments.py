# Generated by Django 3.0.4 on 2020-04-13 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassAssignments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_id', models.CharField(max_length=20)),
                ('assignment_id', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'class_assignments',
                'order_with_respect_to': 'class_id',
            },
        ),
    ]
