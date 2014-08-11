# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0003_rename_project_panel_fields'),
    ]

    operations = [
        migrations.RenameModel('ProjectPanelParameter', 'PanelTemplateParameter')
    ]
