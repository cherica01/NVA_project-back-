# Generated by Django 5.1.4 on 2025-05-05 14:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0001_initial'),
        ('event', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agentreport',
            name='agent',
        ),
        migrations.RemoveField(
            model_name='agentreport',
            name='submitted_by',
        ),
        migrations.AlterModelOptions(
            name='monthlyranking',
            options={'ordering': ['rank']},
        ),
        migrations.AlterUniqueTogether(
            name='monthlyranking',
            unique_together={('agent', 'month')},
        ),
        migrations.AlterField(
            model_name='monthlyranking',
            name='month',
            field=models.DateField(),
        ),
        migrations.CreateModel(
            name='AIAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField()),
                ('analysis_json', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-month'],
                'unique_together': {('month',)},
            },
        ),
        migrations.CreateModel(
            name='EventPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('revenue', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('products_sold', models.IntegerField(default=0)),
                ('client_satisfaction', models.IntegerField(choices=[(0, 'Non évalué'), (1, 'Insatisfait'), (2, 'Peu satisfait'), (3, 'Neutre'), (4, 'Satisfait'), (5, 'Très satisfait')], default=0)),
                ('notes', models.TextField(blank=True, null=True)),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='performance', to='event.event')),
            ],
            options={
                'verbose_name': "Performance d'événement",
                'verbose_name_plural': "Performances d'événements",
            },
        ),
        migrations.DeleteModel(
            name='AgentPerformance',
        ),
        migrations.DeleteModel(
            name='AgentReport',
        ),
        migrations.RemoveField(
            model_name='monthlyranking',
            name='highlights',
        ),
        migrations.RemoveField(
            model_name='monthlyranking',
            name='year',
        ),
    ]
