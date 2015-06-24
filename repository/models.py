from string import join
import hashlib
import io
import datetime
from tempfile import TemporaryFile
from cStringIO import StringIO

import os
import re
from django.core.exceptions import \
    ValidationError, \
    ObjectDoesNotExist, \
    MultipleObjectsReturned
from django.core.files import File
from django.db import models
from django.contrib.auth.models import User
from guardian.shortcuts import \
    get_perms, get_objects_for_user, get_users_with_perms
from rest_framework.authtoken.models import Token

import flowio
import numpy as np


class ProtectedModel(models.Model):
    class Meta:
        abstract = True

    def has_view_permission(self, user):
        return False

    def has_add_permission(self, user):
        return False

    def has_modify_permission(self, user):
        return False

    def has_process_permission(self, user):
        return False

    def has_user_management_permission(self, user):
        return False


##############################
# Non-project related models #
##############################


class Specimen(models.Model):
    specimen_name = models.CharField(
        unique=True,
        max_length=32,
        null=False,
        blank=False)
    specimen_description = models.CharField(
        unique=True,
        max_length=256,
        null=False,
        blank=False)

    def __unicode__(self):
        return u'%s' % self.specimen_name


PARAMETER_TYPE_CHOICES = (
    ('FSC', 'Forward Scatter'),
    ('SSC', 'Side Scatter'),
    ('FLR', 'Fluorescence'),
    ('TIM', 'Time')
)

PARAMETER_VALUE_TYPE_CHOICES = (
    ('H', 'Height'),
    ('W', 'Width'),
    ('A', 'Area'),
    ('T', 'Time')
)

STAINING_CHOICES = (
    ('FULL', 'Full Stain'),
    ('FMO', 'Fluorescence Minus One'),
    ('ISO', 'Isotype Control'),
    ('UNS', 'Unstained')
)

PRETREATMENT_CHOICES = (
    ('In vitro', 'In vitro'),
    ('Ex vivo', 'Ex vivo')
)

STORAGE_CHOICES = (
    ('Fresh', 'Fresh'),
    ('Cryopreserved', 'Cryopreserved')
)

PREDEFINED_PROCESS_CHOICES = (
    ('1', 'Subsampled, asinh, HDP'),
    ('2', 'Subsampled, logicle, HDP'),
)

PROCESS_INPUT_VALUE_TYPE_CHOICES = (
    ('Boolean', 'Boolean'),
    ('Integer', 'Integer'),
    ('PositiveInteger', 'Positive Integer'),
    ('Decimal', 'Decimal'),
    ('String', 'String'),
    ('Date', 'Date')
)

STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Working', 'Working'),
    ('Error', 'Error'),
    ('Complete', 'Complete'),
)


##########################
# Project related models #
##########################


class ProjectManager(models.Manager):
    @staticmethod
    def get_projects_user_can_view(user):
        """
        Return a list of projects for which the given user has view permissions,
        including any view access to even a single site in the project.
        Do NOT use this method to determine whether a user has access to a
        particular project resource.
        """
        if hasattr(user, 'worker'):
            # Workers need to be able to view all data
            projects = Project.objects.all()
        else:
            projects = get_objects_for_user(
                user,
                'view_project_data',
                klass=Project)
        sites = get_objects_for_user(user, 'view_site_data', klass=Site)
        site_projects = Project.objects\
            .filter(id__in=[i.project_id for i in sites])\
            .exclude(id__in=[p.id for p in projects])

        return projects | site_projects

    @staticmethod
    def get_projects_user_can_manage_users(user):
        """
        Return a list of projects for which the given user has user management
        permissions.
        """
        projects = get_objects_for_user(
            user,
            'manage_project_users',
            klass=Project)

        return projects


class Project(ProtectedModel):
    project_name = models.CharField(
        "Project Name",
        unique=True,
        null=False,
        blank=False,
        max_length=128)
    project_desc = models.TextField(
        "Project Description",
        null=True,
        blank=True,
        help_text="A short description of the project")

    objects = ProjectManager()

    class Meta:
        permissions = (
            ('view_project_data', 'View Project Data'),
            ('add_project_data', 'Add Project Data'),
            ('modify_project_data', 'Modify/Delete Project Data'),
            ('submit_process_requests', 'Submit Process Requests'),
            ('manage_project_users', 'Manage Project Users'),
        )

    def has_view_permission(self, user):
        if user.has_perm('view_project_data', self):
            return True
        elif hasattr(user, 'worker'):
            # Workers need to be able to retrieve samples
            return True
        return False

    def has_add_permission(self, user):
        if user.has_perm('add_project_data', self):
            return True
        return False

    def has_modify_permission(self, user):
        if user.has_perm('modify_project_data', self):
            return True
        return False

    def has_process_permission(self, user):
        if user.has_perm('submit_process_requests', self):
            return True
        return False

    def has_user_management_permission(self, user):
        if user.has_perm('manage_project_users', self):
            return True
        return False

    def get_project_users(self):
        user_set = set()
        user_set.update(get_users_with_perms(self, with_superusers=False))
        for site in self.site_set.all():
            user_set.update(get_users_with_perms(site, with_superusers=False))

        return user_set

    def get_user_permissions(self, user):
        return get_perms(user, self)

    def get_cytometer_count(self):
        return Cytometer.objects.filter(site__project=self).count()

    def get_sample_count(self):
        return Sample.objects.filter(subject__project=self).count()

    def get_compensation_count(self):
        return Compensation.objects.filter(
            site_panel__site__project=self).count()

    def __unicode__(self):
        return u'Project: %s' % self.project_name


class Marker(ProtectedModel):
    project = models.ForeignKey(Project)
    marker_abbreviation = models.CharField(
        null=False,
        blank=False,
        max_length=32
    )

    def has_view_permission(self, user):
        if user.has_perm('view_project_data', self.project):
            return True

        return False

    def has_modify_permission(self, user):
        if user.has_perm('modify_project_data', self.project):
            return True
        return False

    def __unicode__(self):
        return u'%s' % self.marker_abbreviation

    class Meta:
        unique_together = (('project', 'marker_abbreviation'),)
        ordering = ['marker_abbreviation']


class Fluorochrome(ProtectedModel):
    project = models.ForeignKey(Project)
    fluorochrome_abbreviation = models.CharField(
        null=False,
        blank=False,
        max_length=32
    )

    def has_view_permission(self, user):
        if user.has_perm('view_project_data', self.project):
            return True

        return False

    def has_modify_permission(self, user):
        if user.has_perm('modify_project_data', self.project):
            return True
        return False

    def __unicode__(self):
        return u'%s' % self.fluorochrome_abbreviation

    class Meta:
        unique_together = (('project', 'fluorochrome_abbreviation'),)
        ordering = ['fluorochrome_abbreviation']


class CellSubsetLabel(ProtectedModel):
    project = models.ForeignKey(Project)
    name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=96)
    description = models.TextField(null=True, blank=True)

    def has_view_permission(self, user):
        if user.has_perm('view_project_data', self.project):
            return True

        return False

    def has_modify_permission(self, user):
        if user.has_perm('modify_project_data', self.project):
            return True
        return False

    class Meta:
        unique_together = (('project', 'name'),)

    def __unicode__(self):
        return u'%s' % self.name


class Stimulation(ProtectedModel):
    project = models.ForeignKey(Project)
    stimulation_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=128)
    stimulation_description = models.TextField(null=True, blank=True)

    def has_view_permission(self, user):
        if user.has_perm('view_project_data', self.project):
            return True

        return False

    def has_modify_permission(self, user):
        if user.has_perm('modify_project_data', self.project):
            return True
        return False

    class Meta:
        unique_together = (('project', 'stimulation_name'),)

    def __unicode__(self):
        return u'%s' % self.stimulation_name


class PanelTemplate(ProtectedModel):
    project = models.ForeignKey(Project, null=False, blank=False)
    panel_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=128)
    panel_description = models.TextField(
        "Panel Description",
        null=True,
        blank=True,
        help_text="A short description of the panel")

    def has_view_permission(self, user):

        if user.has_perm('view_project_data', self.project):
            return True

        return False

    def get_sample_count(self):
        site_panels = SitePanel.objects.filter(panel_template=self)
        sample_count = Sample.objects.filter(site_panel__in=site_panels).count()
        return sample_count

    def get_compensation_count(self):
        site_panels = SitePanel.objects.filter(panel_template=self)
        compensations = Compensation.objects.filter(
            site_panel__in=site_panels).count()
        return compensations

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(PanelTemplate, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('project', 'panel_name'),)

    def __unicode__(self):
        return u'%s' % self.panel_name


class PanelTemplateParameter(ProtectedModel):
    panel_template = models.ForeignKey(PanelTemplate)
    parameter_type = models.CharField(
        max_length=3,
        choices=PARAMETER_TYPE_CHOICES,
        null=False,
        blank=False,
    )
    parameter_value_type = models.CharField(
        max_length=1,
        choices=PARAMETER_VALUE_TYPE_CHOICES,
        null=False,
        blank=False,
    )
    fluorochrome = models.ForeignKey(
        Fluorochrome,
        null=True,
        blank=True
    )

    def _get_name(self):
        """
        Returns the parameter name with value type.
        """
        name_string = '%s_%s' % (
            self.parameter_type,
            self.parameter_value_type)
        if self.paneltemplateparametermarker_set.count() > 0:
            markers = self.paneltemplateparametermarker_set.all()
            marker_string = "_".join(
                sorted(
                    [m.marker.marker_abbreviation for m in markers]
                )
            )
            name_string += '_' + marker_string
        if self.fluorochrome:
            name_string += '_' + self.fluorochrome.fluorochrome_abbreviation
        return name_string

    name = property(_get_name)

    class Meta:
        ordering = ['parameter_type', 'parameter_value_type']

    def __unicode__(self):
        return u'Panel: %s, Parameter: %s-%s' % (
            self.panel_template,
            self.parameter_type,
            self.parameter_value_type
        )


class PanelTemplateParameterMarker(models.Model):
    panel_template_parameter = models.ForeignKey(PanelTemplateParameter)
    marker = models.ForeignKey(Marker)

    class Meta:
        unique_together = (('panel_template_parameter', 'marker'),)

    def __unicode__(self):
        return u'%s: %s' % (self.panel_template_parameter, self.marker)


class PanelVariant(ProtectedModel):
    panel_template = models.ForeignKey(PanelTemplate)
    staining_type = models.CharField(
        max_length=4,
        null=False,
        blank=False,
        choices=STAINING_CHOICES
    )
    name = models.CharField(
        max_length=32,
        null=True,
        blank=True
    )

    def has_view_permission(self, user):

        if user.has_perm('view_project_data', self.panel_template.project):
            return True

        return False

    def __unicode__(self):
        return u'%s' % (self.name,)


class SiteManager(models.Manager):
    @staticmethod
    def get_sites_user_can_view(user, project=None):
        """
        Returns project sites for which the given user has view permissions
        """

        if project is None:
            # get all projects the user has at least one viewable site for,
            # then we'll iterate through the projects and figure out
            # the sites that are viewable
            projects = Project.objects.get_projects_user_can_view(user)

            # will use this to get the final Site queryset
            site_id_list = []

            for project in projects:
                if project.has_view_permission(user):
                    site_id_list.extend([s.id for s in project.site_set.all()])
                else:
                    site_id_list.extend([
                        s.id for s in get_objects_for_user(
                            user,
                            'view_site_data',
                            klass=Site
                        ).filter(
                            project=project
                        )
                    ])

            sites = Site.objects.filter(id__in=site_id_list)
        else:
            if project.has_view_permission(user):
                sites = Site.objects.filter(project=project)
            else:
                sites = get_objects_for_user(
                    user, 'view_site_data',
                    klass=Site).filter(
                        project=project)

        return sites

    @staticmethod
    def get_sites_user_can_add(user, project):
        """
        Returns project sites for which the given user has add permissions
        """
        if project.has_add_permission(user):
            sites = Site.objects.filter(project=project)
        else:
            sites = get_objects_for_user(
                user,
                'add_site_data',
                klass=Site).filter(
                    project=project)

        return sites

    @staticmethod
    def get_sites_user_can_modify(user, project):
        """
        Returns project sites for which the given user has modify permissions
        """
        if project.has_modify_permission(user):
            sites = Site.objects.filter(project=project)
        else:
            sites = get_objects_for_user(
                user,
                'modify_site_data',
                klass=Site).filter(
                    project=project)

        return sites


class Site(ProtectedModel):
    project = models.ForeignKey(Project)
    site_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=128)

    objects = SiteManager()

    class Meta:
        unique_together = (('project', 'site_name'),)
        permissions = (
            ('view_site_data', 'View Site'),
            ('add_site_data', 'Add Site Data'),
            ('modify_site_data', 'Modify/Delete Site Data')
        )

    def get_sample_count(self):
        site_panels = SitePanel.objects.filter(site=self)
        sample_count = Sample.objects.filter(site_panel__in=site_panels).count()
        return sample_count

    def get_compensation_count(self):
        site_panels = SitePanel.objects.filter(site=self)
        compensations = Compensation.objects.filter(
            site_panel__in=site_panels).count()
        return compensations

    def get_user_permissions(self, user):
        perms = get_perms(user, self)
        # we don't want the global perms, just the object-perms
        perms_to_remove = ['add_site', 'change_site', 'delete_site']
        for p in perms_to_remove:
            try:
                perms.remove(p)
            except ValueError:
                continue
        return perms

    def has_view_permission(self, user):
        if user.has_perm('view_project_data', self.project):
            return True
        elif user.has_perm('view_site_data', self):
            return True
        return False

    def has_add_permission(self, user):
        if user.has_perm('add_project_data', self.project):
            return True
        elif user.has_perm('add_site_data', self):
            return True
        return False

    def has_modify_permission(self, user):
        if user.has_perm('modify_project_data', self.project):
            return True
        elif user.has_perm('modify_site_data', self):
            return True
        return False

    def __unicode__(self):
        return u'%s' % self.site_name


class Cytometer(ProtectedModel):
    site = models.ForeignKey(Site, null=False, blank=False)
    cytometer_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=128)
    serial_number = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=256)

    class Meta:
        unique_together = (('site', 'cytometer_name'),)

    def has_view_permission(self, user):
        if user.has_perm('view_project_data', self.site.project):
            return True
        elif user.has_perm('view_site_data', self.site):
            return True
        return False

    def has_add_permission(self, user):
        if self.site.has_add_permission(user):
            return True
        return False

    def has_modify_permission(self, user):
        if self.site.has_modify_permission(user):
            return True
        return False

    def __unicode__(self):
        return u'%s: %s' % (self.site.site_name, self.cytometer_name)


class SitePanel(ProtectedModel):
    # a SitePanel must be "based" off of a PanelTemplate
    # and is required to have at least the parameters specified in the
    # its PanelTemplate
    panel_template = models.ForeignKey(PanelTemplate, null=False, blank=False)
    site = models.ForeignKey(Site, null=False, blank=False)

    # We don't allow site panels to have their own name,
    # so we use implementation version to differentiate site panels
    # which are based on the same panel template for the same site
    implementation = models.IntegerField(editable=False, null=False)
    site_panel_comments = models.TextField(
        "Site Panel Comments",
        null=True,
        blank=True,
        help_text="A short description of the site panel")

    def _get_name(self):
        """
        Returns the parameter name with value type.
        """
        return '%s (%d)' % (
            self.panel_template.panel_name,
            self.implementation)

    name = property(_get_name)

    def has_view_permission(self, user):

        if self.site.project.has_view_permission(user):
            return True
        elif self.site is not None:
            if user.has_perm('view_site_data', self.site):
                return True

        return False

    def has_modify_permission(self, user):
        if self.site.has_modify_permission(user):
            return True
        return False

    def save(self, *args, **kwargs):
        # Get count of site panels for the panel template / site combo
        # to figure out the implementation number
        if not self.implementation:
            current_implementations = SitePanel.objects.filter(
                site=self.site,
                panel_template=self.panel_template).values_list(
                    'implementation', flat=True)

            proposed_number = len(current_implementations) + 1

            if proposed_number not in current_implementations:
                self.implementation = proposed_number
            else:
                raise ValidationError(
                    "Could not calculate implementation version.")

        super(SitePanel, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s: %s (%d)' % (
            self.site.site_name,
            self.panel_template.panel_name,
            self.implementation)


class SitePanelParameter(ProtectedModel):
    site_panel = models.ForeignKey(SitePanel)
    parameter_type = models.CharField(
        max_length=3,
        choices=PARAMETER_TYPE_CHOICES)
    parameter_value_type = models.CharField(
        max_length=1,
        choices=PARAMETER_VALUE_TYPE_CHOICES)
    fluorochrome = models.ForeignKey(
        Fluorochrome,
        null=True,
        blank=True)

    # fcs_text must match the FCS required keyword $PnN,
    # the short name for parameter n.
    fcs_text = models.CharField(
        "FCS Text",
        max_length=32,
        null=False,
        blank=False)

    # fcs_opt_text matches the optional FCS keyword $PnS
    fcs_opt_text = models.CharField(
        "FCS Optional Text",
        max_length=32,
        null=True,
        blank=True)

    # fcs_number represents the parameter number in the FCS file
    # Ex. If the fcs_number == 3, then fcs_text should be in P3N.
    fcs_number = models.IntegerField()

    def _get_name(self):
        """
        Returns the parameter name with value type.
        """
        return '%s: %s-%s' % (
            self.fcs_number,
            self.parameter_type,
            self.parameter_value_type)

    name = property(_get_name)

    class Meta:
        ordering = ['fcs_number']

    def __unicode__(self):
        return u'%s, %s: %s-%s' % (
            self.site_panel,
            self.fcs_number,
            self.parameter_type,
            self.parameter_value_type
        )


class SitePanelParameterMarker(models.Model):
    site_panel_parameter = models.ForeignKey(SitePanelParameter)
    marker = models.ForeignKey(Marker)

    def __unicode__(self):
        return u'%s: %s' % (self.site_panel_parameter, self.marker)


class SubjectGroup(ProtectedModel):
    project = models.ForeignKey(Project)
    group_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=128)
    group_description = models.TextField(null=True, blank=True)

    def has_view_permission(self, user):
        if self.project in Project.objects.get_projects_user_can_view(user):
            return True
        return False

    def has_modify_permission(self, user):
        if user.has_perm('modify_project_data', self.project):
            return True
        return False

    def get_sample_count(self):
        sample_count = Sample.objects.filter(
            subject__in=self.subject_set.all()).count()
        return sample_count

    class Meta:
        unique_together = (('project', 'group_name'),)

    def __unicode__(self):
        return u'%s' % self.group_name


class Subject(ProtectedModel):
    project = models.ForeignKey(Project)
    subject_group = models.ForeignKey(
        SubjectGroup,
        null=True,
        blank=True)
    subject_code = models.CharField(
        "Subject Code",
        null=False,
        blank=False,
        max_length=128)
    batch_control = models.BooleanField(
        null=False,
        blank=False,
        default=False)

    class Meta:
        unique_together = (('project', 'subject_code'),)

    def has_view_permission(self, user):
        if self.project in Project.objects.get_projects_user_can_view(user):
            return True
        return False

    def has_modify_permission(self, user):
        if user.has_perm('modify_project_data', self.project):
            return True
        return False

    def clean(self):
        """
        Check that project for both subject and subject group matches
        Returns ValidationError if a mis-match is found.
        """
        if self.subject_group is not None:
            if self.subject_group.project_id != self.project_id:
                raise ValidationError("Group chosen is not in this Project")

    def __unicode__(self):
        return u'%s' % self.subject_code


class VisitType(ProtectedModel):
    project = models.ForeignKey(Project)
    visit_type_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=128)
    visit_type_description = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (('project', 'visit_type_name'),)

    def has_view_permission(self, user):
        if self.project in Project.objects.get_projects_user_can_view(user):
            return True
        return False

    def has_modify_permission(self, user):
        if user.has_perm('modify_project_data', self.project):
            return True
        return False

    def __unicode__(self):
        return u'%s' % self.visit_type_name


def compensation_file_path(instance, filename):
    project_id = instance.site_panel.site.project_id
    site_id = instance.site_panel.site_id

    upload_dir = join(
        [
            'ReFlow-data',
            str(project_id),
            'compensation',
            str(site_id),
            str(filename + ".npy")
        ],
        "/"
    )

    return upload_dir


class Compensation(ProtectedModel):
    name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=256)
    site_panel = models.ForeignKey(SitePanel)
    compensation_file = models.FileField(
        upload_to=compensation_file_path,
        null=False,
        blank=False,
        max_length=256)
    matrix_text = models.TextField(
        null=False,
        blank=False)
    acquisition_date = models.DateField(
        null=False,
        blank=False
    )

    def has_view_permission(self, user):
        if self.site_panel.site.project.has_view_permission(user):
            return True
        elif self.site_panel.site.has_view_permission(user):
            return True
        return False

    def has_modify_permission(self, user):
        if self.site_panel.site.has_modify_permission(user):
            return True
        return False

    def get_compensation_as_csv(self):
        csv_string = StringIO()
        compensation_array = np.load(self.compensation_file.file)

        header = ','.join(["%d" % n for n in compensation_array[0]])
        csv_string.write(header + '\n')

        np.savetxt(
            csv_string,
            compensation_array[1:, :],
            fmt='%f',
            delimiter=','
        )
        csv_string.seek(0)
        return csv_string

    def clean(self):
        """
        Check for duplicate comp names within a site.
        Returns ValidationError if any duplicates are found.
        Also, save the numpy compensation_file
        """

        # get comps with matching name and parent site,
        # which don't have this pk
        # This should be a redundant check, as the matrix should have
        # been vetted in the API view
        duplicates = Compensation.objects.filter(
            name=self.name,
            site_panel__site=self.site_panel.site_id).exclude(
                id=self.id)

        if duplicates.count() > 0:
            raise ValidationError(
                "Compensation with this name already exists in this site.")

        # get site panel parameter fcs_text, but just for the fluoro params
        # null, scatter and time don't get compensated
        params = SitePanelParameter.objects.filter(
            site_panel_id=self.site_panel_id).exclude(
                parameter_type__in=['FSC', 'SSC', 'TIM', 'NUL'])

        # parse the matrix text and validate the number of params match
        # the number of fluoro params in the site panel and that the matrix
        # values are numbers (can be exp notation)
        matrix_text = self.matrix_text.splitlines(False)
        if not len(matrix_text) > 1:
            raise ValidationError("Too few rows.")

        # first row should be headers matching the PnN value (fcs_text field)
        # may be tab or comma delimited
        # (spaces can't be delimiters b/c they are allowed in the PnN value)
        headers = re.split('\t|,\s*', matrix_text[0])

        missing_fields = list()
        for p in params:
            if p.fcs_text not in headers:
                missing_fields.append(p.fcs_text)

        if len(missing_fields) > 0:
            raise ValidationError(
                "Missing fields: %s" % ", ".join(missing_fields))

        if len(headers) > params.count():
            raise ValidationError("Too many parameters: " + ",".join(headers))

        # the header of matrix text adds a row
        if len(matrix_text) > params.count() + 1:
            raise ValidationError("Too many rows")
        elif len(matrix_text) < params.count() + 1:
            raise ValidationError("Too few rows")

        # we need to store the channel number in the first row of the numpy
        # array, more reliable to identify parameters than some concatenation
        # of parameter attributes
        channel_header = list()
        for h in headers:
            for p in params:
                if p.fcs_text == h:
                    channel_header.append(p.fcs_number)

        np_array = np.array(channel_header)
        np_width = np_array.shape[0]

        # convert the matrix text to numpy array and
        for line in matrix_text[1:]:
            line_values = re.split('\t|,', line)
            for i, value in enumerate(line_values):
                try:
                    line_values[i] = float(line_values[i])
                except ValueError:
                    self._errors["matrix_text"] = \
                        "%s is an invalid matrix value" % line_values[i]
            if len(line_values) > np_width:
                raise ValidationError("Too many values in line: %s" % line)
            elif len(line_values) < np_width:
                raise ValidationError("Too few values in line: %s" % line)
            else:
                np_array = np.vstack([np_array, line_values])

        # save numpy array in the self.compensation_file field
        np_array_file = TemporaryFile()
        np.save(np_array_file, np_array)

        self.compensation_file.save(
            self.name,
            File(np_array_file),
            save=False)

    def __unicode__(self):
        return u'%s' % self.name


def fcs_file_path(instance, filename):
    project_id = instance.subject.project_id
    site_id = instance.site_panel.site_id
    
    upload_dir = join([
        'ReFlow-data',
        str(project_id),
        'sample',
        str(site_id),
        str(filename)],
        "/")

    return upload_dir


def subsample_file_path(instance, filename):
    project_id = instance.subject.project_id
    site_id = instance.site_panel.site_id

    upload_dir = join([
        'ReFlow-data',
        str(project_id),
        'subsample',
        str(site_id),
        str(filename + ".npy")],
        "/")

    return upload_dir


class Sample(ProtectedModel):
    subject = models.ForeignKey(
        Subject,
        null=False,
        blank=False)
    visit = models.ForeignKey(
        VisitType,
        null=False,
        blank=False)
    specimen = models.ForeignKey(
        Specimen,
        null=False,
        blank=False)
    stimulation = models.ForeignKey(
        Stimulation,
        null=False,
        blank=False)
    pretreatment = models.CharField(
        max_length=32,
        choices=PRETREATMENT_CHOICES,
        null=False,
        blank=False)
    storage = models.CharField(
        max_length=32,
        choices=STORAGE_CHOICES,
        null=False,
        blank=False)
    site_panel = models.ForeignKey(
        SitePanel,
        null=False,
        blank=False)
    cytometer = models.ForeignKey(
        Cytometer,
        null=False,
        blank=False)
    panel_variant = models.ForeignKey(PanelVariant)
    acquisition_date = models.DateField(
        null=False,
        blank=False
    )
    sample_file = models.FileField(
        upload_to=fcs_file_path,
        null=False,
        blank=False,
        max_length=256)
    original_filename = models.CharField(
        unique=False,
        null=False,
        blank=False,
        editable=False,
        max_length=256)
    subsample = models.FileField(
        upload_to=subsample_file_path,
        null=False,
        blank=False,
        max_length=256)
    sha1 = models.CharField(
        unique=False,
        null=False,
        blank=False,
        editable=False,
        max_length=40)
    upload_date = models.DateTimeField(
        editable=False,
        null=False,
        blank=False)
    exclude = models.BooleanField(
        null=False,
        blank=False,
        default=False
    )

    def _has_compensation(self):
        """
        Returns the True if a compensation matches the sample's site panel &
        acquisition date
        """
        comps = Compensation.objects.filter(
            site_panel=self.site_panel,
            acquisition_date=self.acquisition_date
        )

        return comps.count() > 0

    has_compensation = property(_has_compensation)

    def has_view_permission(self, user):

        if self.subject.project.has_view_permission(user):
            return True
        elif self.site_panel is not None:
            if user.has_perm('view_site_data', self.site_panel.site):
                return True

        return False

    def has_modify_permission(self, user):

        if self.subject.project.has_modify_permission(user):
            return True
        elif self.site_panel is not None:
            if user.has_perm('modify_site_data', self.site_panel.site):
                return True

        return False

    def get_subsample_as_csv(self):
        csv_string = StringIO()
        subsample_array = np.load(self.subsample.file)
        # return the array as integers, the extra precision is questionable
        np.savetxt(csv_string, subsample_array, fmt='%d', delimiter=',')
        csv_string.seek(0)
        return csv_string

    def get_clean_fcs(self):
        channel_names = []
        params = self.site_panel.sitepanelparameter_set.order_by('fcs_number')
        for param in params:
            name_components = [
                param.parameter_type, param.parameter_value_type
            ]
            markers = param.sitepanelparametermarker_set.order_by(
                'marker__marker_abbreviation'
            )

            for m in markers:
                name_components.append(m.marker.marker_abbreviation)

            if param.fluorochrome is not None:
                name_components.append(
                    param.fluorochrome.fluorochrome_abbreviation
                )
            channel_names.append(
                " ".join(name_components)
            )

        flow_data = flowio.FlowData(
            io.BytesIO(self.sample_file.read())
        )
        event_list = flow_data.events

        clean_file = TemporaryFile()
        flowio.create_fcs(event_list, channel_names, clean_file)
        clean_file.seek(0)

        return clean_file

    def clean(self):
        """
        Overriding clean to do the following:
            - Verify specified subject exists (subject is required)
            - Use subject to get the project (project is required for Subject)
            - Verify visit_type and site belong to the subject project
            - Save  original file name, since it may already exist on our side.
            - Save SHA-1 hash and check for duplicate FCS files in this project.
        """

        try:
            Subject.objects.get(id=self.subject_id)
            self.original_filename = self.sample_file.name.split('/')[-1]
            # get the hash
            file_hash = hashlib.sha1(self.sample_file.read())
        except (ObjectDoesNotExist, ValueError):
            # Subject & sample_file are required...
            # will get caught by Form.is_valid()
            return

        # Verify subject project is the same as the site and
        # visit project (if either site or visit is specified)
        if hasattr(self, 'site'):
            if self.site is not None:
                if self.subject.project != self.site_panel.site.project:
                    raise ValidationError(
                        "Subject and Site Panel must belong to the same project"
                    )

        if hasattr(self, 'visit'):
            if self.visit is not None:
                if self.subject.project != self.visit.project:
                    raise ValidationError(
                        "Subject and Visit must belong to the same project"
                    )

        # Check if the project already has this file,
        # if so delete the temp file and raise ValidationError
        # but the user may be trying to edit an existing sample, so we
        # need to allow that case
        if self.id:
            # existing sample
            if self.sha1 != file_hash.hexdigest():
                raise ValidationError(
                    "You cannot replace an existing FCS file."
                )
        else:
            self.sha1 = file_hash.hexdigest()
        other_sha_values_in_project = Sample.objects.filter(
            subject__project=self.subject.project).exclude(
                id=self.id).values_list('sha1', flat=True)
        if self.sha1 in other_sha_values_in_project:
            if hasattr(self.sample_file.file, 'temporary_file_path'):
                temp_file_path = self.sample_file.file.temporary_file_path()
                os.unlink(temp_file_path)

            raise ValidationError(
                "This FCS file already exists in this Project."
            )

        if self.site_panel is not None and \
                self.site_panel.site.project_id != self.subject.project_id:
            raise ValidationError("Site panel chosen is not in this Project")

        if self.visit is not None and \
                self.visit.project_id != self.subject.project_id:
            raise ValidationError("Visit Type chosen is not in this Project")

        # Verify the file is an FCS file
        if hasattr(self.sample_file.file, 'temporary_file_path'):
            try:
                fcm_obj = flowio.FlowData(
                    self.sample_file.file.temporary_file_path(),
                )
            except:
                raise ValidationError(
                    "Chosen file does not appear to be an FCS file."
                )
        else:
            self.sample_file.seek(0)
            try:
                fcm_obj = flowio.FlowData(io.BytesIO(
                    self.sample_file.read()))
            except:
                raise ValidationError(
                    "Chosen file does not appear to be an FCS file."
                )

        # Read the FCS text segment and get the number of parameters
        # save the dictionary for saving SampleMetadata instances
        # after saving the Sample instance
        self.sample_metadata_dict = fcm_obj.text

        if 'par' in self.sample_metadata_dict:
            if not self.sample_metadata_dict['par'].isdigit():
                raise ValidationError(
                    "FCS file reports non-numeric parameter count"
                )
        else:
            raise ValidationError("No parameters found in FCS file")

        # Get our parameter numbers from all the PnN matches
        sample_params = {}  # parameter_number: PnN text
        for key in self.sample_metadata_dict:
            matches = re.search('^P(\d+)([N,S])$', key, flags=re.IGNORECASE)
            if matches:
                channel_number = matches.group(1)
                n_or_s = str.lower(matches.group(2))
                if channel_number not in sample_params:
                    sample_params[channel_number] = {}
                sample_params[channel_number][n_or_s] = \
                    self.sample_metadata_dict[key]

        # Now check parameters against the chosen site panel
        # First, simply check the counts
        panel_params = self.site_panel.sitepanelparameter_set.all()
        if len(sample_params) != panel_params.count():
            raise ValidationError(
                "FCS parameter count does not match chosen site panel")
        for channel_number in sample_params.keys():
            try:
                panel_param = panel_params.get(fcs_number=channel_number)
            except ObjectDoesNotExist:
                raise ValidationError(
                    "Channel number '%s' not found in chosen site panel" %
                    str(channel_number))
            except MultipleObjectsReturned:
                raise ValidationError(
                    "Multiple channels found in chosen site panel " +
                    "for channel number '%s'" % str(channel_number))

            # Compare PnN field, this field is required so error if not found
            if 'n' in sample_params[channel_number]:
                if sample_params[channel_number]['n'] != panel_param.fcs_text:
                    raise ValidationError(
                        "FCS PnN text for channel '%s' does not match panel"
                        % str(channel_number))
            else:
                raise ValidationError(
                    "Required FCS field PnN not found in file for channel '%s'"
                    % str(channel_number))

            # Compare PnS field, not required but if panel version exists
            # and file version doesn't we'll still error
            if 's' in sample_params[channel_number]:
                if sample_params[channel_number]['s'] != \
                        panel_param.fcs_opt_text:
                    raise ValidationError(
                        "FCS PnS text for channel '%s' does not match panel"
                        % str(channel_number))
            else:
                # file doesn't have PnS field, so panel param must be
                # empty string
                if panel_param.fcs_opt_text != '':
                    raise ValidationError(
                        "FCS PnS text for channel '%s' does not match panel"
                        % str(channel_number))

        # Save a sub-sample of the FCS data for more efficient retrieval
        # We'll save a random 10,000 events (non-duplicated) if possible
        # We'll also store the indices of the randomly chosen events for
        # reproducibility. The indices will be inserted as the first column.
        # The result is stored as a numpy object in a file field.
        # To ensure room for the indices and preserve precision for values,
        # we save as float32
        numpy_data = np.reshape(fcm_obj.events, (-1, fcm_obj.channel_count))
        index_array = np.arange(len(numpy_data))
        np.random.shuffle(index_array)
        random_subsample = numpy_data[index_array[:10000]]
        random_subsample_indexed = np.insert(
            random_subsample,
            0,
            index_array[:10000],
            axis=1)
        subsample_file = TemporaryFile()
        np.save(subsample_file, random_subsample_indexed)
        self.subsample.save(
            self.original_filename,
            File(subsample_file),
            save=False)

    def save(self, *args, **kwargs):
        """ Populate upload date on save """
        if not self.id:
            self.upload_date = datetime.datetime.today()

        super(Sample, self).save(*args, **kwargs)

        # save metadata
        for k, v in self.sample_metadata_dict.items():
            try:
                SampleMetadata(
                    sample=self,
                    key=k,
                    value=v.decode('utf-8', 'ignore')).save()
            except Exception, e:
                print e

    def __unicode__(self):
        return u'Project: %s, Subject: %s, Sample File: %s' % (
            self.subject.project.project_name,
            self.subject.subject_code,
            self.original_filename)


class SampleMetadata(ProtectedModel):
    """
    Key-value pairs for the metadata found in FCS samples
    """
    sample = models.ForeignKey(Sample)
    key = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=256
    )
    value = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=2048
    )

    def has_view_permission(self, user):

        if user.has_perm(
                'view_project_data',
                self.sample.site_panel.site.project):
            return True
        elif self.sample.site_panel.site is not None:
            if user.has_perm(
                    'view_site_data',
                    self.sample.site_panel.site):
                return True

        return False

    def __unicode__(self):
        return u'%s: %s' % (self.key, self.value)


class SampleCollection(ProtectedModel):
    """
    A collection of Samples from the same Project
    """
    project = models.ForeignKey(Project)


class FrozenCompensation(models.Model):
    """
    Used to store comp matrices used for an analysis pipeline
    and are not allowed to be modified.
    """
    matrix_text = models.TextField(editable=False)
    sha1 = models.CharField(
        unique=True,
        null=False,
        blank=False,
        editable=False,
        max_length=40
    )

    def save(self, *args, **kwargs):
        self.sha1 = hashlib.sha1(self.matrix_text).hexdigest()
        super(FrozenCompensation, self).save(*args, **kwargs)


class SampleCollectionMember(ProtectedModel):
    """
    A member of a sample set (i.e. an FCS Sample). However the Samples
    are ForeignKeys which allow null and get set to null on the Sample's
    deletion. This allows deletion of Samples with less hassle.
    It is up to the consumer of SampleCollections to verify
    SampleCollectionMember integrity.
    Also, a compensation matrix is required, as w/o one the sample
    data is not interpretable. However, we don't simply link to a
    Compensation record as a user may change it in the future. So,
    we save a "frozen" compensation matrix
    """
    sample_collection = models.ForeignKey(SampleCollection)
    sample = models.ForeignKey(
        Sample,
        null=True,
        on_delete=models.SET_NULL
    )
    compensation = models.ForeignKey(FrozenCompensation)

    class Meta:
        unique_together = (('sample_collection', 'sample'),)

    def clean(self):
        """
        verify comp matrix matches sample's channels
        """

        # get site panel parameter fcs_text, but just for the fluoro params
        # scatter and time don't get compensated
        params = SitePanelParameter.objects.filter(
            site_panel_id=self.sample.site_panel_id).exclude(
                parameter_type__in=['FSC', 'SSC', 'TIM', 'NUL'])

        # parse the matrix text and validate the number of params match
        # the number of fluoro params in the site panel and that the matrix
        # values are numbers (can be exp notation)
        matrix_text = self.compensation.matrix_text.splitlines(False)
        if not len(matrix_text) > 1:
            raise ValidationError("Too few rows.")

        # first row should be headers matching the channel number
        # comma delimited
        headers = re.split(',\s*', matrix_text[0])

        missing_fields = list()
        for p in params:
            if str(p.fcs_number) not in headers:
                missing_fields.append(p.fcs_number)

        if len(missing_fields) > 0:
            raise ValidationError(
                "Missing fields: %s" % ", ".join(missing_fields))

        if len(headers) > params.count():
            raise ValidationError("Too many parameters")

        # the header of matrix text adds a row
        if len(matrix_text) > params.count() + 1:
            raise ValidationError("Too many rows")
        elif len(matrix_text) < params.count() + 1:
            raise ValidationError("Too few rows")


################################
# START PROCESS RELATED MODELS #
################################


class Worker(models.Model):
    """
    The model representation of a client-side worker.
    """
    user = models.OneToOneField(User, null=False, blank=False, editable=False)
    worker_name = models.CharField(
        "Worker Name",
        unique=True,
        null=False,
        blank=False,
        max_length=128)

    worker_hostname = models.CharField(
        "Worker Hostname",
        unique=False,
        null=False,
        blank=False,
        max_length=256)

    def save(self, *args, **kwargs):
        if not User.objects.filter(username=self.worker_name).exists():
            # ok to create user, and w/o password since it will not allow login
            user = User.objects.create_user(username=self.worker_name)
            # create auth token for REST API usage
            Token.objects.create(user=user)
            # associate worker to new user
            self.user = user
        super(Worker, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % (self.worker_name,)


class SubprocessCategory(models.Model):
    name = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=128)
    description = models.TextField(
        null=True,
        blank=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name_plural = 'Sub-process Categories'
        ordering = ['name']


class SubprocessImplementation(models.Model):
    category = models.ForeignKey(SubprocessCategory)
    name = models.CharField(
        null=False,
        blank=False,
        max_length=128)
    description = models.TextField(
        null=True,
        blank=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name_plural = 'Sub-process Implementation'
        ordering = ['category', 'name']


class SubprocessInput(models.Model):
    implementation = models.ForeignKey(SubprocessImplementation)
    name = models.CharField(
        null=False,
        blank=False,
        max_length=128)
    description = models.TextField(
        null=True,
        blank=True)
    value_type = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        choices=PROCESS_INPUT_VALUE_TYPE_CHOICES)
    required = models.BooleanField(
        default=False)
    allow_multiple = models.BooleanField(
        default=False)
    default = models.CharField(
        null=True,
        blank=True,
        max_length=1024)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name_plural = 'Sub-process Input'
        ordering = ['implementation', 'name']


class ProcessRequest(ProtectedModel):
    """
    A request for a Process
    """
    project = models.ForeignKey(Project)
    sample_collection = models.ForeignKey(
        SampleCollection,
        null=False,
        blank=False,
        editable=False)
    description = models.CharField(
        max_length=128,
        null=False,
        blank=False)
    # processing can be done in 2 stages, where the 2nd stage performs
    # clustering on a single cell subset found in the 1st stage.
    # The single cell subset may include one or more clusters.
    # The 2nd stage is essentially a child of the 1st, with a self-referential
    # key back to the parent. 1st stage parent_stage is null
    parent_stage = models.ForeignKey('self', null=True, blank=True)

    # number of events to subsample
    subsample_count = models.IntegerField(null=False, blank=False)

    predefined = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        choices=PREDEFINED_PROCESS_CHOICES)
    request_user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        editable=False)
    request_date = models.DateTimeField(
        editable=False,
        auto_now_add=True)
    assignment_date = models.DateTimeField(
        null=True,
        blank=True)
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        editable=False)
    # Worker assigned or has completed the request, null before any worker
    # takes assignment
    worker = models.ForeignKey(
        Worker,
        null=True,
        blank=True)
    status = models.CharField(
        max_length=32,
        null=False,
        blank=False,
        choices=STATUS_CHOICES)
    status_message = models.CharField(
        max_length=256,
        null=True,
        blank=True)

    def has_view_permission(self, user):

        if self.project.has_view_permission(user):
            return True

        return False

    def save(self, *args, **kwargs):
        if self.completion_date:
            # Disallow editing if marked complete
            return
        if not self.id:
            self.request_date = datetime.datetime.now()
            self.status = 'Pending'
        if self.status == 'Complete' and not self.completion_date:
            self.completion_date = datetime.datetime.now()
        super(ProcessRequest, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.description


class ProcessRequestStage2Cluster(models.Model):
    """
    Stores which clusters from stage 1 to include in stage 2 analysis
    """
    # this process request is the 2nd stage PR:
    process_request = models.ForeignKey(ProcessRequest)
    # but the cluster is from the parent PR:
    cluster = models.ForeignKey('Cluster')


class ProcessRequestInput(models.Model):
    """
    The value for a specific SubprocessInput for a ProcessRequest
    """
    process_request = models.ForeignKey(ProcessRequest)
    subprocess_input = models.ForeignKey(SubprocessInput)

    # all values get transmitted in JSON format via REST,
    # so everything is a string
    value = models.CharField(null=False, blank=False, max_length=1024)

    def __unicode__(self):
        return u'%s: %s=%s' % (
            self.process_request_id,
            self.subprocess_input.name,
            self.value)


class Cluster(ProtectedModel):
    """
    All processes must produce one or more clusters (if they succeed)
    """
    process_request = models.ForeignKey(ProcessRequest)
    index = models.IntegerField(null=False, blank=False)

    def has_view_permission(self, user):
        if self.process_request.has_view_permission(user):
            return True

        return False


class ClusterLabel(ProtectedModel):
    """
    Allows the user to "tag" clusters with a label, specifically
    mapping one or more CellSubsetLabel instances to a Cluster
    """
    cluster = models.ForeignKey(Cluster)
    label = models.ForeignKey(CellSubsetLabel)

    def has_view_permission(self, user):
        if self.cluster.has_view_permission(user):
            return True

        return False

    def clean(self):
        """
        Check that both the cluster and label belong to the same project.
        Returns ValidationError if the above requirements are
        not satisfied.
        """

        # ensure both the label and cluster belong to the same project
        if self.cluster.process_request.project != self.label.project:
            raise ValidationError(
                "Label and cluster must belong to the same project."
            )

    class Meta:
        unique_together = (('cluster', 'label'),)

    def __unicode__(self):
        return "%d" % self.label_id


def cluster_events_file_path(instance, filename):
    project_id = instance.cluster.process_request.project_id
    pr_id = instance.cluster.process_request.id

    upload_dir = join([
        'ReFlow-data',
        str(project_id),
        'process_requests',
        str(pr_id),
        'clusters',
        str(instance.cluster.id),
        filename],
        "/")

    return upload_dir


class SampleCluster(ProtectedModel):
    """
    Each sample in a SampleCollection tied to a ProcessRequest will have
    its own version of each cluster, with its own location & associated
    event indices. The location of the SampleCluster is stored in the
    SampleClusterParameter set.
    """
    cluster = models.ForeignKey(Cluster)
    sample = models.ForeignKey(Sample)

    # events stored with header row indicating channel index (starting at 0),
    # and 1st column is the event's original index in the source FCS file
    events = models.FileField(
        upload_to=cluster_events_file_path,
        null=False,
        blank=False,
        max_length=256
    )

    def _get_weight(self):
        """
        Returns the sum of the component weights as a percentage
        """
        weight = 0
        for comp in self.sampleclustercomponent_set.all():
            weight += comp.weight
        return round(weight * 100.0, 3)

    weight = property(_get_weight)

    def has_view_permission(self, user):
        if self.cluster.has_view_permission(user):
            return True

        return False


class SampleClusterParameter(ProtectedModel):
    """
    Used to store the location of a SampleCluster.
    Each parameter identifies a channel in the Sample along with the
    coordinate for the SampleCluster.
    """
    sample_cluster = models.ForeignKey(SampleCluster)
    channel = models.IntegerField(null=False, blank=False)
    location = models.FloatField(null=False, blank=False)

    def has_view_permission(self, user):
        if self.sample_cluster.has_view_permission(user):
            return True

        return False


class SampleClusterComponent(ProtectedModel):
    """
    A SampleCluster can be considered a mode comprised of one or more
    components. Each component is a gaussian distribution with its own
    location, weight, and covariance. The components are mainly used
    for re-classification of events in 2nd stage processing
    """
    sample_cluster = models.ForeignKey(SampleCluster)
    covariance_matrix = models.TextField(
        null=False,
        blank=False
    )
    # weight is essentially the percentage of events
    weight = models.FloatField(null=False, blank=False)

    def has_view_permission(self, user):
        if self.cluster.has_view_permission(user):
            return True

        return False


class SampleClusterComponentParameter(ProtectedModel):
    """
    Used to store the location of a SampleClusterComponent.
    Each parameter identifies a channel in the Sample along with the
    coordinate for the SampleClusterComponent.
    """
    sample_cluster_component = models.ForeignKey(SampleClusterComponent)
    channel = models.IntegerField(null=False, blank=False)
    location = models.FloatField(null=False, blank=False)

    def has_view_permission(self, user):
        if self.sample_cluster.has_view_permission(user):
            return True

        return False
