# Generated by Django 5.1.4 on 2025-03-19 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(default='Notification', max_length=255),
        ),
    ]
