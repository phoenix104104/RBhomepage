# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0006_auto_20150116_1020'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='member',
            options={'ordering': ['number']},
        ),
        migrations.AddField(
            model_name='batting',
            name='field',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='game',
            name='batter_table',
            field=models.TextField(default=[]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='game',
            name='pitcher_table',
            field=models.TextField(default=[]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='game',
            name='record',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
