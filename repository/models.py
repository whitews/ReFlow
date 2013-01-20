from string import join
import numpy
import cStringIO
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from fcm.io import loadFCS

from reflow.settings import MEDIA_ROOT

class Project(models.Model):
    project_name = models.CharField("Project Name", unique=True, null=False, blank=False, max_length=128)
    project_desc = models.TextField("Project Description", null=True, blank=True)

    def get_visit_type_count(self):
        return ProjectVisitType.objects.filter(project=self).count()

    def get_panel_count(self):
        return Panel.objects.filter(site__project=self).count()

    def get_subject_count(self):
        return Subject.objects.filter(site__project=self).count()

    def get_sample_count(self):
        return Sample.objects.filter(subject__site__project=self).count()

    def __unicode__(self):
        return u'Project: %s' % (self.project_name)

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
    project   = models.ForeignKey(Project)
    site_name = models.CharField(unique=False, null=False, blank=False, max_length=128)

    def clean(self):
        "Check for duplicate site names within a project. Returns ValidationError if any duplicates are found."

        # count sites with matching site_name and parent project, which don't have this pk
        site_duplicates = Site.objects.filter(
            site_name=self.site_name,
            project=self.project).exclude(
            id=self.id)

        if site_duplicates.count() > 0:
            raise ValidationError("Site name already exists in this project.")

    def __unicode__(self):
        return u'%s' % (self.site_name)

class Panel(models.Model):
    site = models.ForeignKey(Site, null=False, blank=False)
    panel_name = models.CharField(unique=False, null=False, blank=False, max_length=128)

    def clean(self):
        "Check for duplicate panel names within a project site. Returns ValidationError if any duplicates are found."

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
            pass # Site is required and will get caught by Form.is_valid()

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
        return u'%s' % (self.parameter_short_name)

class ParameterValueType(models.Model):
    value_type_name = models.CharField(max_length=32, null=False, blank=False)
    value_type_short_name = models.CharField(max_length=2, null=False, blank=False)

    def __unicode__(self):
        return u'%s' % (self.value_type_short_name)

class PanelParameterMap(models.Model):
    panel = models.ForeignKey(Panel)
    parameter = models.ForeignKey(Parameter)
    value_type = models.ForeignKey(ParameterValueType)
    # fcs_text should match the FCS required keyword $PnN, the short name for parameter n.
    fcs_text = models.CharField("FCS Text", max_length=32, null=False, blank=False)

    def clean(self):
        "Check for duplicate parameter/value_type combos in a panel. Returns ValidationError if any duplicates are found."

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
        return u'%s' % (self.antibody_short_name)

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
        return u'%s' % (self.fluorochrome_short_name)

class ParameterFluorochromeMap(models.Model):
    parameter = models.ForeignKey(Parameter)
    fluorochrome = models.ForeignKey(Fluorochrome)

    def __unicode__(self):
        return u'%s: %s' % (self.parameter, self.fluorochrome)

class Subject(models.Model):
    site    = models.ForeignKey(Site)    
    subject_id = models.CharField("Subject ID", null=False, blank=False, max_length=128)

    def clean(self):
        "Check for duplicate subject ID in a project. Returns ValidationError if any duplicates are found."

        # count subjects with matching subject_id and parent project, which don't have this pk
        try:
            site = Site.objects.get(id=self.site.id)
        except:
            site = None

        if site:
            subject_duplicates = Subject.objects.filter(
                    subject_id=self.subject_id,
                    site__project=self.site.project).exclude(
                            id=self.id)
            if subject_duplicates.count() > 0:
                raise ValidationError("Subject ID already exists in this project.")
        else:
            pass # Site is required and will get caught by Form.is_valid()

    def __unicode__(self):
        return u'Project: %s, Subject: %s' % (self.site.project.project_name, self.subject_id)

class ProjectVisitType(models.Model):
    project                = models.ForeignKey(Project)
    visit_type_name        = models.CharField(unique=False, null=False, blank=False, max_length=128)
    visit_type_description = models.TextField(null=True, blank=True)

    def clean(self):
        "Check for duplicate visit types in a project. Returns ValidationError if any duplicates are found."

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
            pass # Project is required and will get caught by Form.is_valid()

    def __unicode__(self):
        return u'%s' % (self.visit_type_name)

def fcs_file_path(instance, filename):
    project_id = instance.subject.site.project.id
    site_id    = instance.subject.site.id
    subject_id = instance.subject.id
    
    upload_dir = join([MEDIA_ROOT, str(project_id), str(site_id), str(subject_id), str(filename)], "/")
    
    print "Upload dir is: %s" % upload_dir
    
    return upload_dir

class Sample(models.Model):
    subject = models.ForeignKey(Subject)
    visit = models.ForeignKey(ProjectVisitType, null=True, blank=True)
    sample_file = models.FileField(upload_to=fcs_file_path)
    original_filename = models.CharField(unique=False, null=False, blank=False, max_length=256)

    def get_fcs_text_segment(self):
        fcs = loadFCS(self.sample_file.file.name)
        return fcs.notes.text

    def get_fcs_data(self):
        fcs = loadFCS(self.sample_file.file.name)
        data = fcs.view()

        header = []
        if self.sampleparametermap_set.count():
            params = self.sampleparametermap_set.all()
            for param in params.order_by('fcs_number'):
                header.append('%s-%s' % (param.parameter.parameter_short_name, param.value_type.value_type_short_name))
        else:
            for name in fcs.channels:
                header.append(name)

        # Need a category column for the d3 selection to work
        data_with_cat = numpy.zeros((data.shape[0], data.shape[1]+1))
        data_with_cat[:,:-1] = data

        # need to convert it to csv-style string with header row
        buffer = cStringIO.StringIO()
        buffer.write(','.join(header)+',category\n')
        print buffer.getvalue()
        # currently limiting to 100 rows b/c the browser can't handle too much
        numpy.savetxt(buffer, data_with_cat[:100,:], fmt='%d',delimiter=',')

        return buffer.getvalue()

    def clean(self):
        "Need to save the original file name, since it may already exist on our side"

        self.original_filename = self.sample_file.name.split('/')[-1]

    def __unicode__(self):
        return u'Project: %s, Subject: %s, Sample File: %s' % (
            self.subject.site.project.project_name,
            self.subject.subject_id,
            self.sample_file.name.split('/')[-1])

class SampleParameterMap(models.Model):
    sample = models.ForeignKey(Sample)
    parameter = models.ForeignKey(Parameter)
    value_type = models.ForeignKey(ParameterValueType)

    # fcs_text should match the FCS required keyword $PnN, the short name for parameter n.
    fcs_text = models.CharField("FCS Text", max_length=32, null=False, blank=False)
    # fcs_number represents the parameter number in the FCS file
    # Ex. If the fcs_number == 3, then fcs_text should be in P3N.
    fcs_number = models.IntegerField()

    def __unicode__(self):
            return u'SampleID: %s, Parameter: %s-%s, Number: %s, Text: %s' % (
                self.sample.id,
                self.parameter,
                self.value_type,
                self.fcs_number,
                self.fcs_text)

