# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-25 13:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cryptofolio', '0019_addressinput'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fiat',
            fields=[
                ('name', models.CharField(max_length=10, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Investment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(blank=True, default=None, null=True)),
                ('fiat', models.CharField(default='USD', max_length=10)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(default='BTC', max_length=10)),
                ('fiat', models.CharField(db_index=True, default='USD', max_length=10)),
                ('rate', models.FloatField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='currency',
            name='crypto',
        ),
        migrations.AlterField(
            model_name='addressinput',
            name='currency',
            field=models.CharField(default='BTC', max_length=10),
        ),
        migrations.AlterField(
            model_name='exchangebalance',
            name='currency',
            field=models.CharField(default='BTC', max_length=10),
        ),
        migrations.AlterField(
            model_name='manualinput',
            name='currency',
            field=models.CharField(default='BTC', max_length=10),
        ),
    ]
