from string import join
import hashlib
import io
import datetime

import os
import re
from django.core.exceptions import \
    ValidationError, \
    ObjectDoesNotExist, \
    MultipleObjectsReturned
from django.contrib.contenttypes.models import ContentType
from django.db import models
from guardian.shortcuts import get_objects_for_user, get_users_with_perms
from guardian.models import UserObjectPermission
import fcm


class ProtectedModel(models.Model):
    class Meta:
        abstract = True

    def has_view_permission(self, user):
        return False

    def has_add_permission(self, user):
        return False

    def has_modify_permission(self, user):
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


class Antibody(models.Model):
    antibody_abbreviation = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=32)
    antibody_name = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=128)
    antibody_description = models.TextField(
        null=True,
        blank=True)

    def __unicode__(self):
        return u'%s' % self.antibody_abbreviation

    class Meta:
        verbose_name_plural = 'Antibodies'
        ordering = ['antibody_abbreviation']


class Fluorochrome(models.Model):
    fluorochrome_abbreviation = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=32)
    fluorochrome_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=128)
    fluorochrome_description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.fluorochrome_abbreviation

    class Meta:
        ordering = ['fluorochrome_abbreviation']


PARAMETER_TYPE_CHOICES = (
    ('FSC', 'Forward Scatter'),
    ('SSC', 'Side Scatter'),
    ('FCA', 'Fluorochrome Conjugated Antibody'),
    ('FMO', 'Fluorescence Minus One'),
    ('ISO', 'Isotype Control'),
    ('DMP', 'Dump Channel'),
    ('VIA', 'Viability'),
    ('ICA', 'Isotope Conjugated Antibody'),
    ('TIM', 'Time')
)

PARAMETER_VALUE_TYPE_CHOICES = (
    ('H', 'Height'),
    ('W', 'Width'),
    ('A', 'Area'),
    ('T', 'Time')
)

STAINING_CHOICES = (
    ('FS', 'Full Stain'),
    ('FM', 'Fluorescence minus one'),
    ('IS', 'Isotype Control')
)


##############################
### Project related models ###
##############################


class ProjectManager(models.Manager):
    def get_projects_user_can_view(self, user):
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
        return UserObjectPermission.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(Project),
            object_pk=self.id)

    def get_visit_type_count(self):
        return VisitType.objects.filter(project=self).count()

    def get_panel_count(self):
        return SitePanel.objects.filter(site__project=self).count()

    def get_subject_count(self):
        return Subject.objects.filter(project=self).count()

    def get_sample_count(self):
        return Sample.objects.filter(subject__project=self).count()

    def get_compensation_count(self):
        return Compensation.objects.filter(site__project=self).count()

    def __unicode__(self):
        return u'Project: %s' % self.project_name


class Stimulation(ProtectedModel):
    project = models.ForeignKey(Project)
    stimulation_name = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=128)
    stimulation_description = models.TextField(null=True, blank=True)

    def has_view_permission(self, user):

        if user.has_perm('view_project_data', self.project):
            return True

        return False

    def __unicode__(self):
        return u'%s' % self.stimulation_name


class ProjectPanel(ProtectedModel):
    project = models.ForeignKey(Project, null=False, blank=False)
    panel_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=128)
    staining = models.CharField(
        max_length=2,
        choices=STAINING_CHOICES,
        null=False,
        blank=False)
    parent_panel = models.ForeignKey(
        "self",
        null=True,
        blank=True)

    def has_view_permission(self, user):

        if user.has_perm('view_project_data', self.project):
            return True

        return False

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

        duplicates = ProjectPanel.objects.filter(
            panel_name=self.panel_name,
            project=self.project).exclude(
                id=self.id)
        if duplicates.count() > 0:
            raise ValidationError(
                "A panel with this name already exists in this project."
            )

    def __unicode__(self):
        return u'%s' % self.panel_name


class ProjectPanelParameter(ProtectedModel):
    project_panel = models.ForeignKey(ProjectPanel)
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
        return '%s-%s' % (
            self.parameter_type,
            self.parameter_value_type)

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
        if not hasattr(self, 'project_panel'):
            error_message.append("Project Panel is required")
        if not hasattr(self, 'parameter_type'):
            error_message.append("Parameter type is required")

        if len(error_message) > 0:
            raise ValidationError(error_message)

        # count panel mappings with matching parameter and value_type,
        # which don't have this pk
        # TODO: update duplicate check in ProjectPanelParameter
        ppm_duplicates = ProjectPanelParameter.objects.filter(
            project_panel=self.project_panel,
            fluorochrome=self.fluorochrome,
            parameter_type=self.parameter_type,
            parameter_value_type=self.parameter_value_type).exclude(id=self.id)

        if ppm_duplicates.count() > 0:
            raise ValidationError(
                "This combination already exists in this panel"
            )

    def __unicode__(self):
        return u'Panel: %s, Parameter: %s-%s' % (
            self.project_panel,
            self.parameter_type,
            self.parameter_value_type
        )


class ProjectPanelParameterAntibody(models.Model):
    project_panel_parameter = models.ForeignKey(ProjectPanelParameter)
    antibody = models.ForeignKey(Antibody)

    # override clean to prevent duplicate Ab's for a parameter...
    # unique_together doesn't work for forms with the parameter excluded
    def clean(self):
        """
        Verify the parameter & antibody combo doesn't already exist
        """

        qs = ProjectPanelParameterAntibody.objects.filter(
            project_panel_parameter=self.project_panel_parameter,
            antibody=self.antibody)

        if qs.exists():
            raise ValidationError(
                "This antibody is already included in this parameter."
            )

    def __unicode__(self):
        return u'%s: %s' % (self.project_panel_parameter, self.antibody)


class SiteManager(models.Manager):
    def get_sites_user_can_view(self, user, project=None):
        """
        Returns project sites for which the given user has view permissions
        """

        if project is None:
            project_list = Project.objects.get_projects_user_can_view(user)
            project_id_list = []
            for p in project_list:
                project_id_list.append(p.id)
            project_view_sites = Site.objects.filter(
                project_id__in=project_id_list)
            view_sites = get_objects_for_user(
                user, 'view_site_data',
                klass=Site).filter(
                    project__in=project_list)

            sites = project_view_sites | view_sites
        else:
            if project.has_view_permission(user):
                sites = Site.objects.filter(project=project)
            else:
                sites = get_objects_for_user(
                    user, 'view_site_data',
                    klass=Site).filter(
                        project=project)

        return sites

    def get_sites_user_can_add(self, user, project):
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

    def get_sites_user_can_modify(self, user, project):
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

    def get_sites_user_can_manage_users(self, user, project):
        """
        Returns project sites for which the given user has modify permissions
        """
        if project.has_user_management_permission(user):
            sites = Site.objects.filter(project=project)
        else:
            sites = get_objects_for_user(
                user,
                'manage_site_users',
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
            ('modify_site_data', 'Modify/Delete Site Data'),
            ('manage_site_users', 'Manage Site Users')
        )

    def get_user_permissions(self, user):
        return UserObjectPermission.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(Site),
            object_pk=self.id)

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


class SitePanel(ProtectedModel):
    # a SitePanel must be "based" off of a ProjectPanel
    # and is required to have at least the parameters specified in the
    # its ProjectPanel
    project_panel = models.ForeignKey(ProjectPanel, null=False, blank=False)
    site = models.ForeignKey(Site, null=False, blank=False)

    # We don't allow site panels to have their own name,
    # so we use implementation version to differentiate site panels
    # which are based on the same project panel for the same site
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
            self.project_panel.panel_name,
            self.implementation)

    name = property(_get_name)

    def has_view_permission(self, user):

        if user.has_perm('view_project_data', self.site.project):
            return True
        elif self.site is not None:
            if user.has_perm('view_site_data', self.site):
                return True

        return False

    def clean(self):
        try:
            Site.objects.get(id=self.site_id)
            ProjectPanel.objects.get(id=self.project_panel_id)
        except ObjectDoesNotExist:
            # site & project panel are required...
            # will get caught by Form.is_valid()
            return

        # project panel must be in the same project as the site
        if self.site.project_id != self.project_panel.project_id:
            raise ValidationError(
                "Chosen project panel is not in site's project.")

        # Get count of site panels for the project panel / site combo
        # to figure out the implementation number
        if not self.implementation:
            current_implementations = SitePanel.objects.filter(
                site=self.site,
                project_panel=self.project_panel).values_list(
                    'implementation', flat=True)

            proposed_number = len(current_implementations) + 1

            if proposed_number not in current_implementations:
                self.implementation = proposed_number
            else:
                raise ValidationError(
                    "Could not calculate implementation version.")

    def __unicode__(self):
        return u'%s (%d) (Site: %s)' % (
            self.project_panel.panel_name,
            self.implementation,
            self.site.site_name)


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
        # TODO: need better site panel parameter duplicate checking
        spp_duplicates = SitePanelParameter.objects.filter(
            site_panel=self.site_panel,
            fluorochrome=self.fluorochrome,
            parameter_type=self.parameter_type,
            parameter_value_type=self.parameter_value_type).exclude(id=self.id)

        if spp_duplicates.count() > 0:
            raise ValidationError(
                "This combination already exists in this panel"
            )

        panel_fcs_text_duplicates = SitePanelParameter.objects.filter(
            site_panel=self.site_panel,
            fcs_text=self.fcs_text).exclude(id=self.id)

        if panel_fcs_text_duplicates.count() > 0:
            raise ValidationError("A site panel cannot have duplicate FCS text")

        if self.fcs_text == '':
            raise ValidationError("FCS Text is required")

    def __unicode__(self):
        return u'%s, %s: %s-%s' % (
            self.site_panel,
            self.fcs_number,
            self.parameter_type,
            self.parameter_value_type
        )


class SitePanelParameterAntibody(models.Model):
    site_panel_parameter = models.ForeignKey(SitePanelParameter)
    antibody = models.ForeignKey(Antibody)

    # override clean to prevent duplicate Ab's for a parameter...
    # unique_together doesn't work for forms with the parameter excluded
    def clean(self):
        """
        Verify the parameter & antibody combo doesn't already exist
        """

        qs = SitePanelParameterAntibody.objects.filter(
            site_panel_parameter=self.site_panel_parameter,
            antibody=self.antibody)

        if qs.exists():
            raise ValidationError(
                "This antibody is already included in this parameter."
            )

    def __unicode__(self):
        return u'%s: %s' % (self.site_panel_parameter, self.antibody)


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

    def has_view_permission(self, user):
        if self.project in Project.objects.get_projects_user_can_view(user):
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


# TODO: change to TimePoint ???
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
    project_id = instance.site.project_id
    site_id = instance.site_id

    upload_dir = join(
        [
            'ReFlow-data',
            str(project_id),
            'compensation',
            str(site_id),
            str(filename)],
        "/"
    )

    return upload_dir


class Compensation(ProtectedModel):
    site = models.ForeignKey(Site)
    compensation_file = models.FileField(
        upload_to=compensation_file_path,
        null=False,
        blank=False)
    original_filename = models.CharField(
        unique=False,
        null=False,
        blank=False,
        editable=False,
        max_length=256)
    matrix_text = models.TextField(
        null=False,
        blank=False,
        editable=False)

    def has_view_permission(self, user):

        if user.has_perm('view_project_data', self.site.project):
            return True
        elif self.site is not None:
            if user.has_perm('view_site_data', self.site):
                return True

    def clean(self):
        """
        Overriding clean to do the following:
            - Verify specified site exists (site is required)
            - Save original file name, it may already exist on our side.
            - Save the matrix text
        """

        try:
            Site.objects.get(id=self.site_id)
            self.original_filename = self.compensation_file.name.split('/')[-1]
        except ObjectDoesNotExist:
            # site & compensation file are required...
            # will get caught by Form.is_valid()
            return

        # get the matrix, a bit funky b/c the files may have \r or \n line
        # termination. we'll save the matrix_text with \n line terminators
        self.compensation_file.seek(0)
        text = self.compensation_file.read()
        self.matrix_text = '\n'.join(text.splitlines())

    def __unicode__(self):
        return u'%s' % (self.original_filename)


def fcs_file_path(instance, filename):
    project_id = instance.subject.project_id
    subject_id = instance.subject_id
    
    upload_dir = join([
        'ReFlow-data',
        str(project_id),
        str(subject_id),
        str(filename)],
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
    site_panel = models.ForeignKey(
        SitePanel,
        null=False,
        blank=False)
    compensation = models.ForeignKey(
        Compensation,
        null=True,
        blank=True)
    sample_file = models.FileField(
        upload_to=fcs_file_path,
        null=False,
        blank=False)
    original_filename = models.CharField(
        unique=False,
        null=False,
        blank=False,
        editable=False,
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

        if user.has_perm('view_project_data', self.subject.project):
            return True
        elif self.site is not None:
            if user.has_perm('view_site_data', self.site_panel.site):
                return True

        return False

    def clean(self):
        """
        Overriding clean to do the following:
            - Verify specified subject exists (subject is required)
            - Use subject to get the project (project is required for Subject)
            - Verify visit_type and site belong to the subject project
            - Save  original file name, since it may already exist on our side.
            - Save SHA-1 hash and check for duplicate FCS files in this project.
        """

        # TODO: restrict site to ones the requesting user has add perms for
        # but request isn't available in clean() ???

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
                if self.subject.project != self.site.project:
                    raise ValidationError(
                        "Subject and Site must belong to the same project"
                    )

        if hasattr(self, 'visit'):
            if self.visit is not None:
                if self.subject.project != self.visit.project:
                    raise ValidationError(
                        "Subject and Visit must belong to the same project"
                    )

        # Check if the project already has this file,
        # if so delete the temp file and raise ValidationError
        self.sha1 = file_hash.hexdigest()
        other_sha_values_in_project = Sample.objects.filter(
            subject__project=self.subject.project).exclude(
                id=self.id).values_list('sha1', flat=True)
        if self.sha1 in other_sha_values_in_project:
            if hasattr(self.sample_file.file, 'temporary_file_path'):
                temp_file_path = self.sample_file.file.temporary_file_path()
                os.unlink(temp_file_path)
                # TODO: check if this generates an IOError when Django deletes

            raise ValidationError(
                "This FCS file already exists in this Project."
            )

        if self.site_panel is not None and self.site_panel.site.project_id != self.subject.project_id:
            raise ValidationError("Site panel chosen is not in this Project")

        if self.visit is not None and self.visit.project_id != self.subject.project_id:
            raise ValidationError("Visit Type chosen is not in this Project")

        # Verify the file is an FCS file
        if hasattr(self.sample_file.file, 'temporary_file_path'):
            try:
                fcm_obj = fcm.loadFCS(
                    self.sample_file.file.temporary_file_path(),
                    transform=None,
                    auto_comp=False)
            except:
                raise ValidationError(
                    "Chosen file does not appear to be an FCS file."
                )
        else:
            self.sample_file.seek(0)
            try:
                fcm_obj = fcm.loadFCS(io.BytesIO(
                    self.sample_file.read()),
                    transform=None,
                    auto_comp=False)
            except:
                raise ValidationError(
                    "Chosen file does not appear to be an FCS file."
                )

        # Read the FCS text segment and get the number of parameters
        # save the dictionary for saving SampleMetadata instances
        # after saving the Sample instance
        self.sample_metadata_dict = fcm_obj.notes.text

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
                if sample_params[channel_number]['s'] != panel_param.fcs_opt_text:
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


class SampleSet(ProtectedModel):
    """
    An arbitrary collection of Sample instances within a Project
    """
    project = models.ForeignKey(Project)

    # Make non-editable and auto-generated based on date/user combo???
    name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=256)
    description = models.TextField(
        null=True,
        blank=True)
    samples = models.ManyToManyField(Sample)

    class Meta:
        unique_together = (('project', 'name'),)

    def has_view_permission(self, user):
        """
        User must have project permissions to view sample sets
        """
        if user.has_perm('view_project_data', self.project):
            return True

        return False

    def clean(self):
        """
        Verify the project & name combo doesn't already exist
        """

        qs = SampleSet.objects.filter(
            project=self.project,
            name=self.name)

        if qs.exists():
            raise ValidationError(
                "A sample set with this name already exists in this project."
            )

    def __unicode__(self):
        return u'%s (Project: %s)' % (
            self.name,
            self.project.project_name)


def validate_samples(sender, **kwargs):
    """
    Verify all the samples belong to the self.project
    """
    print kwargs
    sample_set = kwargs['instance']
    action = kwargs['action']
    pk_set = kwargs['pk_set']

    if action == 'pre_add':
        try:
            samples_to_add = Sample.objects.filter(pk__in=pk_set)
        except:
            raise ValidationError(
                "Could not find specified samples. Check that they exist.")

        for sample in samples_to_add:
            print "Sample Set Project: ", sample_set.project_id
            print "Sample Project: ", sample.subject.project_id
            if sample_set.project_id != sample.subject.project_id:
                raise ValidationError(
                    "Samples must belong to the specified project."
                )

models.signals.m2m_changed.connect(
    validate_samples,
    sender=SampleSet.samples.through)