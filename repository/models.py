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


##################################
### Non-project related models ###
##################################


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
    ('Completed', 'Completed'),
)


##############################
### Project related models ###
##############################


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
        return Compensation.objects.filter(site_panel__site__project=self).count()

    def get_bead_sample_count(self):
        return BeadSample.objects.filter(cytometer__site__project=self).count()

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

    def clean(self):
        """
        Check for duplicate subset labels in a project.
        Returns ValidationError if any duplicates are found.
        """

        # count labels with matching name and parent project,
        # which don't have this pk
        try:
            Project.objects.get(id=self.project_id)
        except ObjectDoesNotExist:
            return  # Project is required and will get caught by Form.is_valid()

        duplicates = CellSubsetLabel.objects.filter(
            name=self.name,
            project=self.project).exclude(id=self.id)
        if duplicates.count() > 0:
            raise ValidationError(
                "CellSubsetLabel name already exists in this project."
            )

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

    def clean(self):
        """
        Check for duplicate stimulations in a project.
        Returns ValidationError if any duplicates are found.
        """

        # count stims with matching name and parent project,
        # which don't have this pk
        try:
            Project.objects.get(id=self.project_id)
        except ObjectDoesNotExist:
            return  # Project is required and will get caught by Form.is_valid()

        stim_duplicates = Stimulation.objects.filter(
            stimulation_name=self.stimulation_name,
            project=self.project).exclude(
                id=self.id)
        if stim_duplicates.count() > 0:
            raise ValidationError(
                "Stimulation name already exists in this project."
            )

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

    def get_bead_sample_count(self):
        site_panels = SitePanel.objects.filter(panel_template=self)
        sample_count = BeadSample.objects.filter(
            site_panel__in=site_panels).count()
        return sample_count

    def get_compensation_count(self):
        site_panels = SitePanel.objects.filter(panel_template=self)
        compensations = Compensation.objects.filter(
            site_panel__in=site_panels).count()
        return compensations

    def clean(self):
        """
        Check for duplicate panel names within a project.
        Returns ValidationError if any duplicates are found.
        """

        # count panels with matching panel_name and parent project,
        # which don't have this pk
        try:
            Project.objects.get(id=self.project_id)
        except ObjectDoesNotExist:
            return  # Project is required and will get caught by Form.is_valid()

        duplicates = PanelTemplate.objects.filter(
            panel_name=self.panel_name,
            project=self.project).exclude(
                id=self.id)
        if duplicates.count() > 0:
            raise ValidationError(
                "A template with this name already exists in this project."
            )

    def __unicode__(self):
        return u'%s' % self.panel_name


class PanelTemplateParameter(ProtectedModel):
    panel_template = models.ForeignKey(PanelTemplate)
    parameter_type = models.CharField(
        max_length=3,
        choices=PARAMETER_TYPE_CHOICES)
    parameter_value_type = models.CharField(
        max_length=1,
        choices=PARAMETER_VALUE_TYPE_CHOICES,
        null=True,
        blank=True)
    fluorochrome = models.ForeignKey(
        Fluorochrome,
        null=True,
        blank=True)

    def _get_name(self):
        """
        Returns the parameter name with value type.
        """
        name_string = '%s_%s' % (
            self.parameter_type,
            self.parameter_value_type)
        if self.paneltemplateparametermarker_set.count() > 0:
            marker_string = "_".join(sorted([m.marker.marker_abbreviation for m in self.paneltemplateparametermarker_set.all()]))
            name_string += '_' + marker_string
        if self.fluorochrome:
            name_string += '_' + self.fluorochrome.fluorochrome_abbreviation
        return name_string

    name = property(_get_name)

    class Meta:
        ordering = ['parameter_type', 'parameter_value_type']

    def clean(self):
        """
        Check for duplicate parameter/value_type combos in a panel.
        Returns ValidationError if any duplicates are found.
        """

        # first check that there are no empty values
        error_message = []
        if not hasattr(self, 'panel_template'):
            error_message.append("Panel template is required")
        if not hasattr(self, 'parameter_type'):
            error_message.append("Parameter type is required")

        if len(error_message) > 0:
            raise ValidationError(error_message)

        # count panel mappings with matching parameter and value_type,
        # which don't have this pk
        # This is a little tricky since we need to match the marker set
        # but in any order (for multiplex channels)
        # i.e. these are duplicates: CD3+CD8 & CD8+CD3
        # We're using a an annotation approach by combining
        # '__in' with a matching count of the markers
        ppm_duplicates = PanelTemplateParameter.objects.filter(
            panel_template=self.panel_template,
            fluorochrome=self.fluorochrome,
            paneltemplateparametermarker__in=self.paneltemplateparametermarker_set.all(),
            parameter_type=self.parameter_type,
            parameter_value_type=self.parameter_value_type).exclude(
                id=self.id)
        ppm_duplicates = ppm_duplicates.annotate(
            num_markers=models.Count('paneltemplateparametermarker')).filter(
                num_markers=self.paneltemplateparametermarker_set.all().count())

        if ppm_duplicates.count() > 0:
            raise ValidationError(
                "This combination already exists in this panel"
            )

    def __unicode__(self):
        return u'Panel: %s, Parameter: %s-%s' % (
            self.panel_template,
            self.parameter_type,
            self.parameter_value_type
        )


class PanelTemplateParameterMarker(models.Model):
    panel_template_parameter = models.ForeignKey(PanelTemplateParameter)
    marker = models.ForeignKey(Marker)

    # override clean to prevent duplicate Ab's for a parameter...
    # unique_together doesn't work for forms with the parameter excluded
    def clean(self):
        """
        Verify the parameter & marker combo doesn't already exist
        """

        qs = PanelTemplateParameterMarker.objects.filter(
            panel_template_parameter=self.panel_template_parameter,
            marker=self.marker).exclude(id=self.id)

        if qs.exists():
            raise ValidationError(
                "This marker is already included in this parameter."
            )

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
        permissions = (
            ('view_site_data', 'View Site'),
            ('add_site_data', 'Add Site Data'),
            ('modify_site_data', 'Modify/Delete Site Data')
        )

    def get_sample_count(self):
        site_panels = SitePanel.objects.filter(site=self)
        sample_count = Sample.objects.filter(site_panel__in=site_panels).count()
        return sample_count

    def get_bead_sample_count(self):
        site_panels = SitePanel.objects.filter(site=self)
        sample_count = BeadSample.objects.filter(
            site_panel__in=site_panels).count()
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

    def clean(self):
        """
        Check for duplicate site names within a project.
        Returns ValidationError if any duplicates are found.
        """

        # count sites with matching site_name and parent project,
        # which don't have this pk
        site_duplicates = Site.objects.filter(
            site_name=self.site_name,
            project=self.project).exclude(
                id=self.id)

        if site_duplicates.count() > 0:
            raise ValidationError("Site name already exists in this project.")

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

    def clean(self):
        """
        Check for duplicate cytometer names within a site.
        Returns ValidationError if any duplicates are found.
        """
        if not hasattr(self, 'site'):
            return  # site is required and will get caught
        # count cytos with matching name and parent site,
        # which don't have this pk
        duplicates = Cytometer.objects.filter(
            cytometer_name=self.cytometer_name,
            site=self.site).exclude(
                id=self.id)

        if duplicates.count() > 0:
            raise ValidationError("Cytometer already exists in this site.")

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

    def clean(self):
        try:
            Site.objects.get(id=self.site_id)
            PanelTemplate.objects.get(id=self.panel_template_id)
        except ObjectDoesNotExist:
            # site & panel template are required...
            # will get caught by Form.is_valid()
            return

        # panel template must be in the same project as the site
        if self.site.project_id != self.panel_template.project_id:
            raise ValidationError(
                "Chosen panel is not in site's project.")

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

    def clean(self):
        """
        Check for duplicate parameter/value_type combos in a panel.
        Returns ValidationError if any duplicates are found.
        """

        # first check that there are no empty values
        error_message = []
        if not hasattr(self, 'site_panel'):
            error_message.append("Site Panel is required")
        if not hasattr(self, 'parameter_type'):
            error_message.append("Parameter type is required")
        if not hasattr(self, 'parameter_value_type'):
            error_message.append("Value type is required")
        if not hasattr(self, 'fcs_text'):
            error_message.append("FCS Text is required")
        if not hasattr(self, 'fcs_number'):
            error_message.append("FCS channel number is required")

        if len(error_message) > 0:
            raise ValidationError(error_message)

        # count panel mappings with matching parameter and value_type,
        # which don't have this pk
        spp_duplicates = SitePanelParameter.objects.filter(
            site_panel=self.site_panel,
            fluorochrome=self.fluorochrome,
            parameter_type=self.parameter_type,
            parameter_value_type=self.parameter_value_type).exclude(
                id=self.id).exclude(parameter_type='NUL')

        if spp_duplicates.count() > 0:
            raise ValidationError(
                "This combination already exists in this panel"
            )

        panel_fcs_text_duplicates = SitePanelParameter.objects.filter(
            site_panel=self.site_panel,
            fcs_text=self.fcs_text).exclude(id=self.id)

        if panel_fcs_text_duplicates.count() > 0:
            raise ValidationError("A site panel cannot have duplicate FCS text")

        panel_fcs_number_duplicates = SitePanelParameter.objects.filter(
            site_panel=self.site_panel,
            fcs_number=self.fcs_number).exclude(id=self.id)

        if panel_fcs_number_duplicates.count() > 0:
            raise ValidationError("Channel numbers must be unique.")

        if self.fcs_text == '':
            raise ValidationError("FCS Text is required")

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

    # override clean to prevent duplicate Ab's for a parameter...
    # unique_together doesn't work for forms with the parameter excluded
    def clean(self):
        """
        Verify the parameter & marker combo doesn't already exist
        """

        qs = SitePanelParameterMarker.objects.filter(
            site_panel_parameter=self.site_panel_parameter,
            marker=self.marker)

        if qs.exists():
            raise ValidationError(
                "This marker is already included in this parameter."
            )

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
        sample_count = Sample.objects.filter(subject__in=self.subject_set.all()).count()
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
        Check for duplicate subject code in a project.
        Returns ValidationError if any duplicates are found.
        """

        # count subjects with matching subject_code and parent project,
        # which don't have this pk
        try:
            Project.objects.get(id=self.project_id)
        except ObjectDoesNotExist:
            return  # Project is required and will get caught by Form.is_valid()

        if self.subject_group is not None:
            if self.subject_group.project_id != self.project_id:
                raise ValidationError("Group chosen is not in this Project")

        subject_duplicates = Subject.objects.filter(
            subject_code=self.subject_code,
            project=self.project).exclude(
                id=self.id)
        if subject_duplicates.count() > 0:
            raise ValidationError(
                "Subject code already exists in this project."
            )

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
        Check for duplicate visit types in a project.
        Returns ValidationError if any duplicates are found.
        """

        # count visit types with matching visit_type_name and parent project,
        # which don't have this pk
        try:
            Project.objects.get(id=self.project_id)
        except ObjectDoesNotExist:
            return  # Project is required and will get caught by Form.is_valid()

        duplicates = VisitType.objects.filter(
            visit_type_name=self.visit_type_name,
            project=self.project).exclude(
                id=self.id)
        if duplicates.count() > 0:
            raise ValidationError("Visit Name already exists in this project.")

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
            compensation_array[1:,:],
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
        duplicates = Compensation.objects.filter(
            name=self.name,
            site_panel__site=self.site_panel.site_id).exclude(
                id=self.id)

        if duplicates.count() > 0:
            raise ValidationError(
                "Compensation with this name already exists in this site.")

        # get site panel parameter fcs_text, but just for the fluoro params
        # 'Null', scatter and time don't get compensated
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
            raise ValidationError("Too many parameters")

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
        numpy_data = n = np.reshape(fcm_obj.events, (-1, fcm_obj.channel_count))
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
        # 'Null', scatter and time don't get compensated
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


def bead_file_path(instance, filename):
    project_id = instance.site_panel.panel_template.project_id
    site_id = instance.site_panel.site_id

    upload_dir = join([
        'ReFlow-data',
        str(project_id),
        'bead_data',
        str(site_id),
        str(filename)],
        "/")

    return upload_dir


def bead_subsample_file_path(instance, filename):
    project_id = instance.site_panel.panel_template.project_id
    site_id = instance.site_panel.site_id

    upload_dir = join([
        'ReFlow-data',
        str(project_id),
        'bead_subsample',
        str(site_id),
        str(filename + ".npy")],
        "/")

    return upload_dir


class BeadSample(ProtectedModel):
    site_panel = models.ForeignKey(
        SitePanel,
        null=False,
        blank=False)
    cytometer = models.ForeignKey(
        Cytometer,
        null=False,
        blank=False)
    acquisition_date = models.DateField(
        null=False,
        blank=False
    )
    includes_negative_control = models.BooleanField(
        null=False,
        blank=False,
        default=False
    )
    negative_control = models.BooleanField(
        null=False,
        blank=False,
        default=False
    )
    compensation_channel = models.ForeignKey(
        Fluorochrome,
        null=True,
        blank=False)
    bead_file = models.FileField(
        upload_to=bead_file_path,
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
        upload_to=bead_subsample_file_path,
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

    def has_view_permission(self, user):

        if self.site_panel.panel_template.project.has_view_permission(user):
            return True
        elif user.has_perm('view_site_data', self.site_panel.site):
            return True

        return False

    def has_modify_permission(self, user):
        if self.site_panel.panel_template.project.has_modify_permission(user):
            return True
        elif user.has_perm('modify_site_data', self.site_panel.site):
            return True

        return False

    def get_subsample_as_csv(self):
        csv_string = StringIO()
        subsample_array = np.load(self.subsample.file)
        # return the array as integers, the extra precision is questionable
        np.savetxt(csv_string, subsample_array, fmt='%d', delimiter=',')
        csv_string.seek(0)
        return csv_string

    def clean(self):
        """
        Overriding clean to do the following:
            - Save  original file name, since it may already exist on our side.
            - Save SHA-1 hash and check for duplicate FCS files in this project.
        """

        self.original_filename = self.bead_file.name.split('/')[-1]
        # get the hash
        file_hash = hashlib.sha1(self.bead_file.read())

        # Verify cytometer and site panel share same site
        if hasattr(self, 'cytometer'):
            if self.cytometer is not None:
                if self.cytometer.site != self.site_panel.site:
                    raise ValidationError(
                        "Cytometer and Site Panel must belong to the same site"
                    )

        # Check if the project already has this file,
        # if so delete the temp file and raise ValidationError
        self.sha1 = file_hash.hexdigest()
        other_sha_values_in_project = BeadSample.objects.filter(
            site_panel__panel_template__project=self.site_panel.panel_template.project).exclude(
                id=self.id).values_list('sha1', flat=True)
        if self.sha1 in other_sha_values_in_project:
            if hasattr(self.bead_file.file, 'temporary_file_path'):
                temp_file_path = self.bead_file.file.temporary_file_path()
                os.unlink(temp_file_path)

            raise ValidationError(
                "This FCS file already exists in this Project."
            )

        # Verify the file is an FCS file
        if hasattr(self.bead_file.file, 'temporary_file_path'):
            try:
                fcm_obj = flowio.FlowData(
                    self.bead_file.file.temporary_file_path(),
                )
            except:
                raise ValidationError(
                    "Chosen file does not appear to be an FCS file."
                )
        else:
            self.bead_file.seek(0)
            try:
                fcm_obj = flowio.FlowData(io.BytesIO(
                    self.bead_file.read()))
            except:
                raise ValidationError(
                    "Chosen file does not appear to be an FCS file."
                )

        # Read the FCS text segment and get the number of parameters
        # save the dictionary for saving BeadSampleMetadata instances
        # after saving the Sample instance
        self.metadata_dict = fcm_obj.text

        if 'par' in self.metadata_dict:
            if not self.metadata_dict['par'].isdigit():
                raise ValidationError(
                    "FCS file reports non-numeric parameter count"
                )
        else:
            raise ValidationError("No parameters found in FCS file")

        # Get our parameter numbers from all the PnN matches
        params = {}  # parameter_number: PnN text
        for key in self.metadata_dict:
            matches = re.search('^P(\d+)([N,S])$', key, flags=re.IGNORECASE)
            if matches:
                channel_number = matches.group(1)
                n_or_s = str.lower(matches.group(2))
                if channel_number not in params:
                    params[channel_number] = {}
                params[channel_number][n_or_s] = \
                    self.metadata_dict[key]

        # Now check parameters against the chosen site panel
        # First, simply check the counts
        panel_params = self.site_panel.sitepanelparameter_set.all()
        if len(params) != panel_params.count():
            raise ValidationError(
                "FCS parameter count does not match chosen site panel")
        for channel_number in params.keys():
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
            if 'n' in params[channel_number]:
                if params[channel_number]['n'] != panel_param.fcs_text:
                    raise ValidationError(
                        "FCS PnN text for channel '%s' does not match panel"
                        % str(channel_number))
            else:
                raise ValidationError(
                    "Required FCS field PnN not found in file for channel '%s'"
                    % str(channel_number))

            # We don't compare PnS field as this field typically identifies
            # which channel is the signal channel, and we only want one site
            # panel per comp bead data set.

        # Save a sub-sample of the FCS data for more efficient retrieval
        # We'll save a random 10,000 events (non-duplicated) if possible
        # We'll also store the indices of the randomly chosen events for
        # reproducibility. The indices will be inserted as the first column.
        # The result is stored as a numpy object in a file field.
        # To ensure room for the indices and preserve precision for values,
        # we save as float32
        numpy_data = n = np.reshape(fcm_obj.events, (-1, fcm_obj.channel_count))
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

        super(BeadSample, self).save(*args, **kwargs)

        # save metadata
        for k, v in self.metadata_dict.items():
            try:
                BeadSampleMetadata(
                    bead_sample=self,
                    key=k,
                    value=v.decode('utf-8', 'ignore')).save()
            except Exception, e:
                print e

    def __unicode__(self):
        return u'Project: %s, Bead File: %s' % (
            self.site_panel.panel_template.project.project_name,
            self.original_filename)


class BeadSampleMetadata(ProtectedModel):
    """
    Key-value pairs for the metadata found in FCS samples
    """
    bead_sample = models.ForeignKey(BeadSample)
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
                self.bead_sample.site_panel.site.project):
            return True
        elif self.bead_sample.site_panel.site is not None:
            if user.has_perm(
                    'view_site_data',
                    self.bead_sample.site_panel.site):
                return True

        return False

    def __unicode__(self):
        return u'%s: %s' % (self.key, self.value)


####################################
### START PROCESS RELATED MODELS ###
####################################


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

    def has_view_permission(self, user):

        if self.project.has_view_permission(user):
            return True

        return False

    def save(self, *args, **kwargs):
        if self.completion_date:
            # Dissallow editing if marked complete
            # TODO: Figure out the best way to do this and raise a
            # ValidationError...can't prevent saving in clean() :(
            return
        if not self.id:
            self.request_date = datetime.datetime.now()
            self.status = 'Pending'
        if self.worker and self.status != 'Complete':
            self.status = 'Working'
        if self.status == 'Complete' and not self.completion_date:
            self.completion_date = datetime.datetime.now()
        super(ProcessRequest, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.description


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
        Check for duplicate labels for a cluster and ensure that both
        the cluster and the label belong to the same project.
        Returns ValidationError if either of the above requirements are
        not satisfied.
        """

        # ensure both the label and cluster belong to the same project
        if self.cluster.process_request.project != self.label.project:
            raise ValidationError(
                "Label and cluster must belong to the same project."
            )

        # count duplicate label / cluster combos,
        # which don't have this pk
        duplicates = ClusterLabel.objects.filter(
            cluster=self.cluster,
            label=self.label).exclude(id=self.id)
        if duplicates.count() > 0:
            raise ValidationError(
                "This cluster is already tagged with this label."
            )

    class Meta:
        unique_together = (('cluster', 'label'),)

    def __unicode__(self):
        return "%d" % self.label_id


class SampleCluster(ProtectedModel):
    """
    Each sample in a SampleCollection tied to a ProcessRequest will have
    its own version of each cluster. The location of the SampleCluster is
    in the SampleClusterParameter set.
    """
    cluster = models.ForeignKey(Cluster)
    sample = models.ForeignKey(Sample)

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


class EventClassification(ProtectedModel):
    """
    Ties a Sample event index to a particular SampleCluster
    """
    sample_cluster = models.ForeignKey(SampleCluster)
    event_index = models.IntegerField(null=False, blank=False)

    def has_view_permission(self, user):
        if self.sample_cluster.has_view_permission(user):
            return True

        return False

    def __unicode__(self):
        return "%d" % self.event_index