# Generated by Django 2.1.4 on 2019-01-01 15:28

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parserapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DdmSlTable',
            fields=[
                ('sl_tables_id', models.AutoField(primary_key=True, serialize=False)),
                ('sl', models.CharField(max_length=10)),
                ('original_table_name', models.CharField(max_length=80)),
                ('mapped_table_name', models.CharField(max_length=80)),
                ('original_column_name', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(max_length=100), size=None)),
                ('mapped_column_name', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(max_length=100), size=None)),
            ],
        ),
    ]
