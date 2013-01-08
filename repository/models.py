from string import join
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from reflow.settings import MEDIA_ROOT

class Project(models.Model):
    project_name = models.CharField("Project Name", unique=True, null=False, blank=False, max_length=128)
    project_desc = models.TextField("Project Description", null=True, blank=True)
    
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

    def __unicode__(self):
        return u'Panel: %s, Parameter: %s=%s' % (self.panel, self.parameter, self.value_type)

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
    subject_id = models.CharField(null=False, blank=False, max_length=128)

    def clean(self):
        "Check for duplicate subject ID in a project. Returns ValidationError if any duplicates are found."

        # count subjects with matching subject_id and parent project, which don't have this pk
        subject_duplicates = Subject.objects.filter(
                subject_id=self.subject_id,
                site__project=self.site.project).exclude(
                        id=self.id)

        if subject_duplicates.count() > 0:
            raise ValidationError("Subject ID already exists in this project.")

    def __unicode__(self):
        return u'Project: %s, Subject: %s' % (self.site.project.project_name, self.subject_id)

def fcs_file_path(instance, filename):
    project_id = instance.subject.site.project.id
    site_id    = instance.subject.site.id
    subject_id = instance.subject.id
    
    upload_dir = join([MEDIA_ROOT, str(project_id), str(site_id), str(subject_id), str(filename)], "/")
    
    print "Upload dir is: %s" % upload_dir
    
    return upload_dir

class Sample(models.Model):
    subject = models.ForeignKey(Subject)
    sample_file = models.FileField(upload_to=fcs_file_path)

    def __unicode__(self):
        return u'Project: %s, Subject: %s, Sample File: %s' % (
            self.subject.site.project.project_name,
            self.subject.subject_id,
            self.sample_file.name.split('/')[-1])

class SampleParameterMap(models.Model):
    sample = models.ForeignKey(Sample)
    parameter = models.ForeignKey(Parameter)
    channel_number = models.IntegerField(null=False, blank=False)
    value_type = models.ForeignKey(ParameterValueType)

    def __unicode__(self):
        return u'SampleID: %s, Parameter: %s-%s, Channel: %d' % (
            self.sample.id,
            self.parameter,
            self.value_type,
            self.channel_number)

