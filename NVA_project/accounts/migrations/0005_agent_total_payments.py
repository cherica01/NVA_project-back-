# Generated by Django 5.1.4 on 2024-12-20 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_agent_age_alter_agent_gender_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='total_payments',
            field=models.FloatField(default=0.0),
        ),
    ]
