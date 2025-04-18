# Generated by Django 5.2 on 2025-04-07 14:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('has_voted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('votes', models.IntegerField(default=0)),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidates', to='polls.position')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.candidate')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.position')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='polls.student')),
            ],
            options={
                'unique_together': {('student', 'position')},
            },
        ),
    ]
