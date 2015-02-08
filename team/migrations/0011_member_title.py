# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0010_auto_20150204_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='title',
            field=models.CharField(default=b'', max_length=100),
            preserve_default=True,
        ),
    ]
