# Generated by Django 3.0.4 on 2020-04-16 03:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('category_name', models.CharField(max_length=25)),
                ('category_description', models.CharField(default=None, max_length=150, null=True)),
                ('category_weight', models.DecimalField(decimal_places=3, max_digits=3, null=True)),
            ],
            options={
                'db_table': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('947b304b-04e7-4b45-ab40-002f0d45800f'), editable=False, primary_key=True, serialize=False, unique=True)),
                ('course_id', models.CharField(max_length=8)),
                ('teacher_id', models.CharField(max_length=100)),
                ('period', models.IntegerField()),
                ('weighted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'classes',
            },
        ),
        migrations.CreateModel(
            name='ClassAssignments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_id', models.CharField(max_length=100)),
                ('assignment_id', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'class_assignments',
            },
        ),
        migrations.CreateModel(
            name='ClassCategories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_id', models.CharField(max_length=100)),
                ('category_id', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'class_categories',
            },
        ),
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
            name='Assignment',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('829a0074-e76c-4080-b81c-55a6ebf5035a'), editable=False, primary_key=True, serialize=False, unique=True)),
                ('assignment_name', models.CharField(max_length=80)),
                ('category_id', models.CharField(max_length=100)),
                ('assignment_description', models.CharField(max_length=150, null=True)),
                ('points', models.IntegerField()),
                ('created', models.DateTimeField(auto_now=True, null=True)),
                ('updated', models.DateTimeField(null=True)),
                ('assigned', models.DateTimeField(null=True)),
                ('due_date', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'assignments',
                'order_with_respect_to': 'id',
            },
        ),
    ]
