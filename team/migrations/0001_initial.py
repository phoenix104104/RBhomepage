# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Batting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.CharField(default=b'', max_length=10)),
                ('pa', models.IntegerField(default=0)),
                ('single', models.IntegerField(default=0)),
                ('double', models.IntegerField(default=0)),
                ('triple', models.IntegerField(default=0)),
                ('hr', models.IntegerField(default=0)),
                ('rbi', models.IntegerField(default=0)),
                ('run', models.IntegerField(default=0)),
                ('bb', models.IntegerField(default=0)),
                ('k', models.IntegerField(default=0)),
                ('sf', models.IntegerField(default=0)),
                ('field', models.CharField(default=b'', max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Current',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('date', models.DateField()),
                ('location', models.CharField(default=b'', max_length=200)),
                ('away_name', models.CharField(default=b'', max_length=200)),
                ('away_scores', models.CharField(default=b'', max_length=200)),
                ('away_R', models.IntegerField(default=0)),
                ('away_H', models.IntegerField(default=0)),
                ('away_E', models.IntegerField(default=0)),
                ('home_name', models.CharField(default=b'', max_length=200)),
                ('home_scores', models.CharField(default=b'', max_length=200)),
                ('home_R', models.IntegerField(default=0)),
                ('home_H', models.IntegerField(default=0)),
                ('home_E', models.IntegerField(default=0)),
                ('record', models.TextField(default=b'')),
            ],
            options={
                'ordering': ['date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('number', models.IntegerField(default=0)),
                ('title', models.CharField(default=b'', max_length=100, blank=True)),
            ],
            options={
                'ordering': ['number'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pitching',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
                ('outs', models.IntegerField(default=0)),
                ('pa', models.IntegerField(default=0)),
                ('hit', models.IntegerField(default=0)),
                ('hr', models.IntegerField(default=0)),
                ('bb', models.IntegerField(default=0)),
                ('k', models.IntegerField(default=0)),
                ('run', models.IntegerField(default=0)),
                ('er', models.IntegerField(default=0)),
                ('go', models.IntegerField(default=0)),
                ('fo', models.IntegerField(default=0)),
                ('win', models.IntegerField(default=0)),
                ('lose', models.IntegerField(default=0)),
                ('game', models.ForeignKey(to='team.Game')),
                ('member', models.ForeignKey(to='team.Member')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='game',
            name='league',
            field=models.ForeignKey(to='team.League'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='batting',
            name='game',
            field=models.ForeignKey(to='team.Game'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='batting',
            name='member',
            field=models.ForeignKey(to='team.Member'),
            preserve_default=True,
        ),
    ]
