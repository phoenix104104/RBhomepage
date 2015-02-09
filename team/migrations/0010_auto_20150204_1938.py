# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0009_auto_20150204_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batting',
            name='order',
            field=models.CharField(default=b'', max_length=10),
            preserve_default=True,
        ),
    ]
