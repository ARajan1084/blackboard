# Generated by Django 3.0.4 on 2020-04-13 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_id', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('course_name', models.CharField(max_length=25)),
            ],
            options={
                'db_table': 'courses',
                'order_with_respect_to': 'course_id',
            },
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('class_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('course_id', models.CharField(max_length=8)),
                ('teacher_id', models.CharField(max_length=4)),
                ('period', models.IntegerField()),
            ],
            options={
                'db_table': 'classes',
                'order_with_respect_to': 'class_id',
            },
        ),
    ]
