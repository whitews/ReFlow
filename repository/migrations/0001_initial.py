# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import repository.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BeadSample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('acquisition_date', models.DateField()),
                ('includes_negative_control', models.BooleanField(default=False)),
                ('negative_control', models.BooleanField(default=False)),
                ('bead_file', models.FileField(max_length=256, upload_to=repository.models.bead_file_path)),
                ('original_filename', models.CharField(max_length=256, editable=False)),
                ('subsample', models.FileField(max_length=256, upload_to=repository.models.bead_subsample_file_path)),
                ('sha1', models.CharField(max_length=40, editable=False)),
                ('upload_date', models.DateTimeField(editable=False)),
                ('exclude', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BeadSampleMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=256)),
                ('value', models.CharField(max_length=2048)),
                ('bead_sample', models.ForeignKey(to='repository.BeadSample')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Compensation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('compensation_file', models.FileField(max_length=256, upload_to=repository.models.compensation_file_path)),
                ('matrix_text', models.TextField()),
                ('acquisition_date', models.DateField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cytometer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cytometer_name', models.CharField(max_length=128)),
                ('serial_number', models.CharField(max_length=256)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='beadsample',
            name='cytometer',
            field=models.ForeignKey(to='repository.Cytometer'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Fluorochrome',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fluorochrome_abbreviation', models.CharField(unique=True, max_length=32)),
                ('fluorochrome_name', models.CharField(unique=True, max_length=128)),
                ('fluorochrome_description', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': [b'fluorochrome_abbreviation'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='beadsample',
            name='compensation_channel',
            field=models.ForeignKey(to='repository.Fluorochrome', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Marker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('marker_abbreviation', models.CharField(unique=True, max_length=32)),
                ('marker_name', models.CharField(unique=True, max_length=128)),
                ('marker_description', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': [b'marker_abbreviation'],
                'verbose_name_plural': b'Markers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProcessRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=128)),
                ('predefined', models.CharField(blank=True, max_length=64, null=True, choices=[(b'1', b'Subsampled, asinh, HDP'), (b'2', b'Subsampled, logicle, HDP')])),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('assignment_date', models.DateTimeField(null=True, blank=True)),
                ('completion_date', models.DateTimeField(null=True, editable=False, blank=True)),
                ('status', models.CharField(max_length=32, choices=[(b'Pending', b'Pending'), (b'Working', b'Working'), (b'Error', b'Error'), (b'Completed', b'Completed')])),
                ('request_user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProcessRequestInput',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=1024)),
                ('process_request', models.ForeignKey(to='repository.ProcessRequest')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProcessRequestOutput',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=1024)),
                ('value', models.FileField(max_length=256, upload_to=repository.models.pr_output_path)),
                ('process_request', models.ForeignKey(to='repository.ProcessRequest')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_name', models.CharField(unique=True, max_length=128, verbose_name=b'Project Name')),
                ('project_desc', models.TextField(help_text=b'A short description of the project', null=True, verbose_name=b'Project Description', blank=True)),
            ],
            options={
                'permissions': ((b'view_project_data', b'View Project Data'), (b'add_project_data', b'Add Project Data'), (b'modify_project_data', b'Modify/Delete Project Data'), (b'submit_process_requests', b'Submit Process Requests'), (b'manage_project_users', b'Manage Project Users')),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='processrequest',
            name='project',
            field=models.ForeignKey(to='repository.Project'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ProjectPanel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('panel_name', models.CharField(max_length=128)),
                ('panel_description', models.TextField(help_text=b'A short description of the panel', null=True, verbose_name=b'Panel Description', blank=True)),
                ('staining', models.CharField(max_length=2, choices=[(b'FS', b'Full Stain'), (b'US', b'Unstained'), (b'FM', b'Fluorescence Minus One'), (b'IS', b'Isotype Control'), (b'CB', b'Compensation Bead')])),
                ('parent_panel', models.ForeignKey(blank=True, to='repository.ProjectPanel', null=True)),
                ('project', models.ForeignKey(to='repository.Project')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectPanelParameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parameter_type', models.CharField(max_length=3, choices=[(b'FSC', b'Forward Scatter'), (b'SSC', b'Side Scatter'), (b'FCM', b'Fluorochrome Conjugated Marker'), (b'UNS', b'Unstained'), (b'ISO', b'Isotype Control'), (b'EXC', b'Exclusion'), (b'VIA', b'Viability'), (b'ICM', b'Isotope Conjugated Marker'), (b'TIM', b'Time'), (b'BEA', b'Bead'), (b'NUL', b'Null')])),
                ('parameter_value_type', models.CharField(blank=True, max_length=1, null=True, choices=[(b'H', b'Height'), (b'W', b'Width'), (b'A', b'Area'), (b'T', b'Time')])),
                ('fluorochrome', models.ForeignKey(blank=True, to='repository.Fluorochrome', null=True)),
                ('project_panel', models.ForeignKey(to='repository.ProjectPanel')),
            ],
            options={
                'ordering': [b'parameter_type', b'parameter_value_type'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectPanelParameterMarker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('marker', models.ForeignKey(to='repository.Marker')),
                ('project_panel_parameter', models.ForeignKey(to='repository.ProjectPanelParameter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pretreatment', models.CharField(max_length=32, choices=[(b'In vitro', b'In vitro'), (b'Ex vivo', b'Ex vivo')])),
                ('storage', models.CharField(max_length=32, choices=[(b'Fresh', b'Fresh'), (b'Cryopreserved', b'Cryopreserved')])),
                ('acquisition_date', models.DateField()),
                ('sample_file', models.FileField(max_length=256, upload_to=repository.models.fcs_file_path)),
                ('original_filename', models.CharField(max_length=256, editable=False)),
                ('subsample', models.FileField(max_length=256, upload_to=repository.models.subsample_file_path)),
                ('sha1', models.CharField(max_length=40, editable=False)),
                ('upload_date', models.DateTimeField(editable=False)),
                ('exclude', models.BooleanField(default=False)),
                ('compensation', models.ForeignKey(blank=True, to='repository.Compensation', null=True)),
                ('cytometer', models.ForeignKey(to='repository.Cytometer')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SampleCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.ForeignKey(to='repository.Project')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='processrequest',
            name='sample_collection',
            field=models.ForeignKey(editable=False, to='repository.SampleCollection'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='SampleCollectionMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample', models.ForeignKey(to='repository.Sample', on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('sample_collection', models.ForeignKey(to='repository.SampleCollection')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='samplecollectionmember',
            unique_together=set([(b'sample_collection', b'sample')]),
        ),
        migrations.CreateModel(
            name='SampleMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=256)),
                ('value', models.CharField(max_length=2048)),
                ('sample', models.ForeignKey(to='repository.Sample')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site_name', models.CharField(max_length=128)),
                ('project', models.ForeignKey(to='repository.Project')),
            ],
            options={
                'permissions': ((b'view_site_data', b'View Site'), (b'add_site_data', b'Add Site Data'), (b'modify_site_data', b'Modify/Delete Site Data')),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='cytometer',
            name='site',
            field=models.ForeignKey(to='repository.Site'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='SitePanel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('implementation', models.IntegerField(editable=False)),
                ('site_panel_comments', models.TextField(help_text=b'A short description of the site panel', null=True, verbose_name=b'Site Panel Comments', blank=True)),
                ('project_panel', models.ForeignKey(to='repository.ProjectPanel')),
                ('site', models.ForeignKey(to='repository.Site')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sample',
            name='site_panel',
            field=models.ForeignKey(to='repository.SitePanel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='compensation',
            name='site_panel',
            field=models.ForeignKey(to='repository.SitePanel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beadsample',
            name='site_panel',
            field=models.ForeignKey(to='repository.SitePanel'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='SitePanelParameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parameter_type', models.CharField(max_length=3, choices=[(b'FSC', b'Forward Scatter'), (b'SSC', b'Side Scatter'), (b'FCM', b'Fluorochrome Conjugated Marker'), (b'UNS', b'Unstained'), (b'ISO', b'Isotype Control'), (b'EXC', b'Exclusion'), (b'VIA', b'Viability'), (b'ICM', b'Isotope Conjugated Marker'), (b'TIM', b'Time'), (b'BEA', b'Bead'), (b'NUL', b'Null')])),
                ('parameter_value_type', models.CharField(max_length=1, choices=[(b'H', b'Height'), (b'W', b'Width'), (b'A', b'Area'), (b'T', b'Time')])),
                ('fcs_text', models.CharField(max_length=32, verbose_name=b'FCS Text')),
                ('fcs_opt_text', models.CharField(max_length=32, null=True, verbose_name=b'FCS Optional Text', blank=True)),
                ('fcs_number', models.IntegerField()),
                ('fluorochrome', models.ForeignKey(blank=True, to='repository.Fluorochrome', null=True)),
                ('site_panel', models.ForeignKey(to='repository.SitePanel')),
            ],
            options={
                'ordering': [b'fcs_number'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SitePanelParameterMarker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('marker', models.ForeignKey(to='repository.Marker')),
                ('site_panel_parameter', models.ForeignKey(to='repository.SitePanelParameter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Specimen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('specimen_name', models.CharField(unique=True, max_length=32)),
                ('specimen_description', models.CharField(unique=True, max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sample',
            name='specimen',
            field=models.ForeignKey(to='repository.Specimen'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Stimulation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stimulation_name', models.CharField(max_length=128)),
                ('stimulation_description', models.TextField(null=True, blank=True)),
                ('project', models.ForeignKey(to='repository.Project')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sample',
            name='stimulation',
            field=models.ForeignKey(to='repository.Stimulation'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject_code', models.CharField(max_length=128, verbose_name=b'Subject Code')),
                ('batch_control', models.BooleanField(default=False)),
                ('project', models.ForeignKey(to='repository.Project')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sample',
            name='subject',
            field=models.ForeignKey(to='repository.Subject'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='SubjectGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_name', models.CharField(max_length=128)),
                ('group_description', models.TextField(null=True, blank=True)),
                ('project', models.ForeignKey(to='repository.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='subject',
            name='subject_group',
            field=models.ForeignKey(blank=True, to='repository.SubjectGroup', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='subjectgroup',
            unique_together=set([(b'project', b'group_name')]),
        ),
        migrations.CreateModel(
            name='SubprocessCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': [b'name'],
                'verbose_name_plural': b'Sub-process Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubprocessImplementation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
                ('category', models.ForeignKey(to='repository.SubprocessCategory')),
            ],
            options={
                'ordering': [b'category', b'name'],
                'verbose_name_plural': b'Sub-process Implementation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubprocessInput',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
                ('value_type', models.CharField(max_length=64, choices=[(b'Boolean', b'Boolean'), (b'Integer', b'Integer'), (b'PositiveInteger', b'Positive Integer'), (b'Decimal', b'Decimal'), (b'String', b'String'), (b'Date', b'Date')])),
                ('required', models.BooleanField(default=False)),
                ('allow_multiple', models.BooleanField(default=False)),
                ('default', models.CharField(max_length=1024, null=True, blank=True)),
                ('implementation', models.ForeignKey(to='repository.SubprocessImplementation')),
            ],
            options={
                'ordering': [b'implementation', b'name'],
                'verbose_name_plural': b'Sub-process Input',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='processrequestinput',
            name='subprocess_input',
            field=models.ForeignKey(to='repository.SubprocessInput'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='VisitType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('visit_type_name', models.CharField(max_length=128)),
                ('visit_type_description', models.TextField(null=True, blank=True)),
                ('project', models.ForeignKey(to='repository.Project')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sample',
            name='visit',
            field=models.ForeignKey(to='repository.VisitType'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('worker_name', models.CharField(unique=True, max_length=128, verbose_name=b'Worker Name')),
                ('worker_hostname', models.CharField(max_length=256, verbose_name=b'Worker Hostname')),
                ('user', models.OneToOneField(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='processrequest',
            name='worker',
            field=models.ForeignKey(blank=True, to='repository.Worker', null=True),
            preserve_default=True,
        ),
    ]
