# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_auto_20150116_0825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='scores',
            field=models.CommaSeparatedIntegerField(max_length=200),
            preserve_default=True,
        ),
    ]
