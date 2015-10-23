# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='avatar',
            unique_together=set([('user', 'primary')]),
        ),
    ]
