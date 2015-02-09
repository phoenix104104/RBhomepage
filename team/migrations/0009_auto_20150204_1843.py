# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0008_auto_20150203_1821'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='away',
            new_name='away_name',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='home',
            new_name='home_name',
        ),
        migrations.RemoveField(
            model_name='game',
            name='batter_table',
        ),
        migrations.RemoveField(
            model_name='game',
            name='pitcher_table',
        ),
        migrations.AlterField(
            model_name='game',
            name='date',
            field=models.DateField(),
            preserve_default=True,
        ),
    ]
