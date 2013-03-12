from string import join
import cStringIO
import hashlib
import io
from tempfile import TemporaryFile
import base64

import os
import re
import numpy
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
import fcm

from reflow.settings import MEDIA_ROOT


class Project(models.Model):
    project_name = models.CharField("Project Name", unique=True, null=False, blank=False, max_length=128)
    project_desc = models.TextField(
        "Project Description",
        null=True,
        blank=True,
        help_text="A short description of the project")

    def get_visit_type_count(self):
        return ProjectVisitType.objects.filter(project=self).count()

    def get_panel_count(self):
        return Panel.objects.filter(site__project=self).count()

    def get_subject_count(self):
        return Subject.objects.filter(project=self).count()

    def get_sample_count(self):
        return Sample.objects.filter(subject__project=self).count()

    def __unicode__(self):
        return u'Project: %s' % self.project_name


class ProjectUserManager(models.Manager):
    def get_user_projects(self, user):
        return Project.objects.select_related().filter(projectusermap__user=user)

    def get_project_users(self, project):
        return User.objects.select_related().filter(projectusermap__project=project)

    def is_project_user(self, project, user):
        return super(ProjectUserManager, self).filter(project=project, user=user).exists()


class ProjectUserMap(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)

    objects = ProjectUserManager()


class Site(models.Model):
    project = models.ForeignKey(Project)
    site_name = models.CharField(unique=False, null=False, blank=False, max_length=128)

    def clean(self):
        """
        Check for duplicate site names within a project. Returns ValidationError if any duplicates are found.
        """

        # count sites with matching site_name and parent project, which don't have this pk
        site_duplicates = Site.objects.filter(
            site_name=self.site_name,
            project=self.project).exclude(
                id=self.id)

        if site_duplicates.count() > 0:
            raise ValidationError("Site name already exists in this project.")

    def __unicode__(self):
        return u'%s' % self.site_name


class Panel(models.Model):
    site = models.ForeignKey(Site, null=False, blank=False)
    panel_name = models.CharField(unique=False, null=False, blank=False, max_length=128)

    def clean(self):
        """
        Check for duplicate panel names within a project site. Returns ValidationError if any duplicates are found.
        """

        # count panels with matching panel_name and parent site, which don't have this pk
        try:
            site = Site.objects.get(id=self.site.id)
        except:
            site = None

        if site:
            duplicates = Panel.objects.filter(
                panel_name=self.panel_name,
                site=self.site).exclude(
                    id=self.id)
            if duplicates.count() > 0:
                raise ValidationError("A panel with this name already exists in this site.")
        else:
            pass  # Site is required and will get caught by Form.is_valid()

    def __unicode__(self):
        return u'%s (Project: %s, Site: %s)' % (self.panel_name, self.site.project.project_name, self.site.site_name)


class Parameter(models.Model):
    parameter_short_name = models.CharField(unique=True, max_length=32, null=False, blank=False)

    PARAMETER_TYPE_CHOICES = (
        ('FS', 'Forward Scatter'),
        ('SS', 'Side Scatter'),
        ('FL', 'Fluoroscence'),
        ('TM', 'Time'),
        ('UN', 'Unknown'),
    )

    parameter_type = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        choices=PARAMETER_TYPE_CHOICES)

    def __unicode__(self):
        return u'%s' % self.parameter_short_name


class ParameterValueType(models.Model):
    value_type_name = models.CharField(max_length=32, null=False, blank=False)
    value_type_short_name = models.CharField(max_length=2, null=False, blank=False)

    def __unicode__(self):
        return u'%s' % self.value_type_short_name


class PanelParameterMap(models.Model):
    panel = models.ForeignKey(Panel)
    parameter = models.ForeignKey(Parameter)
    value_type = models.ForeignKey(ParameterValueType)
    # fcs_text should match the FCS required keyword $PnN, the short name for parameter n.
    fcs_text = models.CharField("FCS Text", max_length=32, null=False, blank=False)

    def _get_name(self):
        """
        Returns the parameter name with value type.
        """
        return '%s-%s' % (self.parameter.parameter_short_name, self.value_type.value_type_short_name)

    name = property(_get_name)

    def clean(self):
        """
        Check for duplicate parameter/value_type combos in a panel. Returns ValidationError if any duplicates are found.
        """

        # first check that there are no empty values
        error_message = []
        if not hasattr(self, 'panel'):
            error_message.append("Panel is required")
        if not hasattr(self, 'parameter'):
            error_message.append("Parameter is required")
        if not hasattr(self, 'value_type'):
            error_message.append("Value type is required")
        if not hasattr(self, 'fcs_text'):
            error_message.append("FCS Text is required")

        if len(error_message) > 0:
            raise ValidationError(error_message)

        # count panel mappings with matching parameter and value_type, which don't have this pk
        ppm_duplicates = PanelParameterMap.objects.filter(
            panel=self.panel,
            parameter=self.parameter,
            value_type=self.value_type).exclude(id=self.id)

        if ppm_duplicates.count() > 0:
            raise ValidationError("This combination already exists in this panel")

        panel_fcs_text_duplicates = PanelParameterMap.objects.filter(
            panel=self.panel,
            fcs_text=self.fcs_text).exclude(id=self.id)

        if panel_fcs_text_duplicates.count() > 0:
            raise ValidationError("A panel cannot have duplicate FCS text")

        if self.fcs_text == '':
            raise ValidationError("FCS Text is required")

    def __unicode__(self):
        return u'Panel: %s, Parameter: %s-%s' % (self.panel, self.parameter, self.value_type)


class Antibody(models.Model):
    antibody_name = models.CharField(unique=True, null=False, blank=False, max_length=128)
    antibody_short_name = models.CharField(unique=True, null=False, blank=False, max_length=32)
    antibody_description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.antibody_short_name


class ParameterAntibodyMap(models.Model):
    parameter = models.ForeignKey(Parameter)
    antibody = models.ForeignKey(Antibody)

    def __unicode__(self):
        return u'%s: %s' % (self.parameter, self.antibody)


class Fluorochrome(models.Model):
    fluorochrome_name = models.CharField(unique=False, null=False, blank=False, max_length=128)
    fluorochrome_short_name = models.CharField(unique=False, null=False, blank=False, max_length=32)
    fluorochrome_description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.fluorochrome_short_name


class ParameterFluorochromeMap(models.Model):
    parameter = models.ForeignKey(Parameter)
    fluorochrome = models.ForeignKey(Fluorochrome)

    def __unicode__(self):
        return u'%s: %s' % (self.parameter, self.fluorochrome)


class Subject(models.Model):
    project = models.ForeignKey(Project)
    subject_id = models.CharField("Subject ID", null=False, blank=False, max_length=128)

    def clean(self):
        """
        Check for duplicate subject ID in a project. Returns ValidationError if any duplicates are found.
        """

        # count subjects with matching subject_id and parent project, which don't have this pk
        try:
            project = Project.objects.get(id=self.project.id)
        except:
            project = None

        if project:
            subject_duplicates = Subject.objects.filter(
                subject_id=self.subject_id,
                project=self.project).exclude(
                    id=self.id)
            if subject_duplicates.count() > 0:
                raise ValidationError("Subject ID already exists in this project.")
        else:
            pass  # Project is required and will get caught by Form.is_valid()

    def __unicode__(self):
        return u'%s' % (self.subject_id)


class ProjectVisitType(models.Model):
    project = models.ForeignKey(Project)
    visit_type_name = models.CharField(unique=False, null=False, blank=False, max_length=128)
    visit_type_description = models.TextField(null=True, blank=True)

    def clean(self):
        """
        Check for duplicate visit types in a project. Returns ValidationError if any duplicates are found.
        """

        # count visit types with matching visit_type_name and parent project, which don't have this pk
        try:
            project = Project.objects.get(id=self.project.id)
        except:
            project = None

        if project:
            duplicates = ProjectVisitType.objects.filter(
                visit_type_name=self.visit_type_name,
                project=self.project).exclude(
                    id=self.id)
            if duplicates.count() > 0:
                raise ValidationError("Visit Name already exists in this project.")
        else:
            pass  # Project is required and will get caught by Form.is_valid()

    def __unicode__(self):
        return u'%s' % self.visit_type_name


def fcs_file_path(instance, filename):
    project_id = instance.subject.project.id
    subject_id = instance.subject.id
    
    upload_dir = join([str(project_id), str(subject_id), str(filename)], "/")
    upload_dir = join([MEDIA_ROOT, upload_dir], '')

    return upload_dir


class Sample(models.Model):
    subject = models.ForeignKey(Subject, null=False, blank=False)
    site = models.ForeignKey(Site, null=True, blank=True)
    visit = models.ForeignKey(ProjectVisitType, null=True, blank=True)
    sample_file = models.FileField(upload_to=fcs_file_path, null=False, blank=False)
    original_filename = models.CharField(unique=False, null=False, blank=False, editable=False, max_length=256)
    sha1 = models.CharField(unique=False, null=False, blank=False, editable=False, max_length=40)
    _data = models.TextField(
        db_column='data',
        blank=True,
        editable=False)

    def set_data(self, data):
        self._data = base64.encodestring(data)

    def get_data(self):
        return base64.decodestring(self._data)

    data = property(get_data, set_data)

    def get_data_as_numpy(self):
        return numpy.load(io.BytesIO(self.get_data()))

    def get_channel_as_numpy(self, fcs_channel_number):
        # Verify fcs_channel_number not zero or negative
        if fcs_channel_number < 1:
            return ''

        # Remember, fcs channels indexed at 1, numpy cols 0 indexed
        numpy_data = self.get_data_as_numpy()
        try:
            return numpy_data[:,(fcs_channel_number-1)].dumps()
        except:
            return ''

    def get_fcs_data(self):
        data = self.get_data_as_numpy()
        header = []
        if self.sampleparametermap_set.count():
            params = self.sampleparametermap_set.all()
            for param in params.order_by('fcs_number'):
                if param.parameter and param.value_type:
                    header.append('%s-%s' % (param.parameter.parameter_short_name, param.value_type.value_type_short_name))
                else:
                    header.append('%s' % (param.fcs_text))

        # Need a category column for the d3 selection to work
        data_with_cat = numpy.zeros((data.shape[0], data.shape[1] + 1))
        data_with_cat[:, :-1] = data

        # need to convert it to csv-style string with header row
        csv_data = cStringIO.StringIO()
        csv_data.write(','.join(header) + ',category\n')

        # currently limiting to 100 rows b/c the browser can't handle too much
        numpy.savetxt(csv_data, data_with_cat[:100, :], fmt='%d', delimiter=',')

        return csv_data.getvalue()

    def clean(self):
        """
        Overriding clean to do the following:
            - Verify specified subject exists (subject is required)
            - Use subject to get the project (project is required for Subject)
            - Verify visit_type and site belong to the subject project
            - Save the original file name, since it may already exist on our side.
            - Save the SHA-1 hash and check for duplicate FCS files in this project.
            - Extract the FCS data as a numpy array to the _data field
        """

        try:
            subject = Subject.objects.get(id = self.subject.id)
            self.original_filename = self.sample_file.name.split('/')[-1]
            # get the hash
            file_hash = hashlib.sha1(self.sample_file.read())
            self.sha1 = file_hash.hexdigest()
        except Exception, e:
            return  # Subject & sample_file are required...will get caught by Form.is_valid()

        # Check if the project already has this file, if so delete the temp file and raise ValidationError
        if self.sha1 in Sample.objects.filter(subject__project=self.subject.project).exclude(id=self.id).values_list('sha1', flat=True):
            if hasattr(self.sample_file.file, 'temporary_file_path'):
                temp_file_path = self.sample_file.file.temporary_file_path()
                os.unlink(temp_file_path)

            raise ValidationError("An FCS file with this SHA-1 hash already exists for this Project.")

        if self.site is not None and self.site.project.id != self.subject.project.id:
            raise ValidationError("Site chosen is not in this Project")

        if self.visit is not None and self.visit.project.id != self.subject.project.id:
            raise ValidationError("Visit Type chosen is not in this Project")

        # Verify the file is an FCS file, and get the numpy array to save to _data
        if hasattr(self.sample_file.file, 'temporary_file_path'):
            fcm_obj = fcm.loadFCS(self.sample_file.file.temporary_file_path(), transform=None, auto_comp=False)
        else:
            self.sample_file.seek(0)
            fcm_obj = fcm.loadFCS(io.BytesIO(self.sample_file.read()), transform=None, auto_comp=False)

        # Now that we have the fcm object, save numpy data array and create SampleParameters
        numpy_array = fcm_obj.view()
        temp_file = TemporaryFile()
        numpy.save(temp_file, numpy_array)
        temp_file.seek(0)
        self.set_data(temp_file.read())

        # Now we have the data, start collecting channel info even though no Panel is
        # associated yet...note, the SampleParameterMap instances are saved in overridden save

        # Read the FCS text segment and get the number of parameters
        sample_text_segment = fcm_obj.notes.text

        if 'par' in sample_text_segment:
            if sample_text_segment['par'].isdigit():
                sample_param_count = int(sample_text_segment['par'])
            else:
                raise ValidationError("FCS file reports non-numeric parameter count")
        else:
            raise ValidationError("No parameters found in FCS file")

        # Get our parameter numbers from all the PnN matches
        sample_parameters = {}  # parameter_number: PnN text
        for key in sample_text_segment:
            matches = re.search('^P(\d+)N$', key, flags=re.IGNORECASE)
            if matches:
                sample_parameters[matches.group(1)] = sample_text_segment[key]

        # Verify the number of data columns matches the number of params we found
        if len(sample_parameters) != numpy_array.shape[1]:
            raise ValidationError("FCS file parameter count and the number of data columns differ.")
        else:
            self._sample_parameters = sample_parameters

    def save(self, *args, **kwargs):
        if hasattr(self.sample_file.file, 'temporary_file_path'):
            # part of the crazy hack to avoid accumulating temp files in /tmp
            # must be done before parent save() or else the FileField file is no longer a TemporaryUploadFile
            self.temp_file_path = self.sample_file.file.temporary_file_path()
        super(Sample, self).save(*args, **kwargs)

        # Save all the parameters as SampleParameterMap instances if we have _sample_parameters
        if hasattr(self, '_sample_parameters'):
            for key in self._sample_parameters:
                spm = SampleParameterMap()
                spm.sample = self
                spm.fcs_number = key
                spm.fcs_text = self._sample_parameters[key]
                spm.save()

    def __unicode__(self):
        return u'Project: %s, Subject: %s, Sample File: %s' % (
            self.subject.project.project_name,
            self.subject.subject_id,
            self.sample_file.name.split('/')[-1])

# Crazy hack ahead...needed for some weird bug where temp upload files are getting stuck in /tmp
def remove_temp_sample_file(sender, **kwargs):
    obj = kwargs['instance']
    if hasattr(obj, 'temp_file_path'):
        os.unlink(obj.temp_file_path)

# connect crazy hack to post_save
post_save.connect(remove_temp_sample_file, sender=Sample)


class SampleParameterMap(models.Model):
    sample = models.ForeignKey(Sample)

    # The parameter and value_type may not be known on initial import, thus null, blank = True
    parameter = models.ForeignKey(Parameter, null=True, blank=True)
    value_type = models.ForeignKey(ParameterValueType, null=True, blank=True)

    # fcs_text should match the FCS required keyword $PnN, the short name for parameter n.
    fcs_text = models.CharField("FCS Text", max_length=32, null=False, blank=False)
    # fcs_number represents the parameter number in the FCS file
    # Ex. If the fcs_number == 3, then fcs_text should be in P3N.
    fcs_number = models.IntegerField()

    def _get_name(self):
        """
        Returns the parameter name with value type, or empty string if none
        """
        if self.parameter and self.value_type:
            return '%s-%s' % (self.parameter.parameter_short_name, self.value_type.value_type_short_name)
        else:
            return ''

    name = property(_get_name)

    def __unicode__(self):
            return u'SampleID: %s, Parameter: %s-%s, Number: %s, Text: %s' % (
                self.sample.id,
                self.parameter,
                self.value_type,
                self.fcs_number,
                self.fcs_text)
