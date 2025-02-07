# Generated by Django 5.1.4 on 2025-02-07 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0005_alter_event_end_date_alter_event_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='company_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_code',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(),
        ),
    ]
