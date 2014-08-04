# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0003_rename_project_panel_fields'),
    ]

    operations = [
        migrations.RenameField('ProjectPanelParameter', 'project_panel', 'panel_template'),
        migrations.RenameField('SitePanel', 'project_panel', 'panel_template')
    ]
