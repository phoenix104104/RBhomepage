# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0005_auto_20150116_1018'),
    ]

    operations = [
        migrations.RenameField(
            model_name='batting',
            old_name='so',
            new_name='k',
        ),
    ]
