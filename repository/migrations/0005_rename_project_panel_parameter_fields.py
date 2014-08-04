# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0004_rename_project_panel_parameter'),
    ]

    operations = [
        migrations.RenameField('ProjectPanelParameterMarker', 'project_panel_parameter', 'panel_template_parameter')
    ]
