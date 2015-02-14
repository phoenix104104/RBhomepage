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
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('date', models.DateField(blank=True)),
                ('location', models.CharField(max_length=200)),
                ('away', models.CharField(max_length=200)),
                ('home', models.CharField(max_length=200)),
                ('scores', models.CommaSeparatedIntegerField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('number', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
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
