# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0005_rename_project_panel_parameter_fields'),
    ]

    operations = [
        migrations.RenameModel('ProjectPanelParameterMarker', 'PanelTemplateParameterMarker')
    ]
