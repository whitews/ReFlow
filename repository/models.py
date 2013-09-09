from string import join
import cStringIO
import hashlib
import io

import os
import re
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.db import models
from guardian.shortcuts import get_objects_for_user, get_users_with_perms
from guardian.models import UserObjectPermission
import numpy
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
        return ProjectVisitType.objects.filter(project=self).count()

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


class Parameter(models.Model):
    parameter_short_name = models.CharField(
        unique=True,
        max_length=32,
        null=False,
        blank=False)

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
    value_type_name = models.CharField(
        max_length=32,
        null=False,
        blank=False)
    value_type_short_name = models.CharField(
        max_length=2,
        null=False,
        blank=False)

    def __unicode__(self):
        return u'%s' % self.value_type_short_name


class Antibody(models.Model):
    antibody_name = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=128)
    antibody_short_name = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=32)
    antibody_description = models.TextField(
        null=True,
        blank=True)

    def __unicode__(self):
        return u'%s' % self.antibody_short_name

    class Meta:
        verbose_name_plural = 'Antibodies'


class ParameterAntibodyMap(models.Model):
    parameter = models.ForeignKey(Parameter)
    antibody = models.ForeignKey(Antibody)

    # override clean to prevent duplicate Ab's for a parameter...
    # unique_together doesn't work for forms with the parameter excluded
    def clean(self):
        """
        Verify the parameter & antibody combo doesn't already exist
        """

        qs = ParameterAntibodyMap.objects.filter(
            parameter=self.parameter,
            antibody=self.antibody)

        if qs.exists():
            raise ValidationError(
                "This antibody is already included in this parameter."
            )

    def __unicode__(self):
        return u'%s: %s' % (self.parameter, self.antibody)


class Fluorochrome(models.Model):
    fluorochrome_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=128)
    fluorochrome_short_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=32)
    fluorochrome_description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.fluorochrome_short_name


class ParameterFluorochromeMap(models.Model):
    parameter = models.ForeignKey(Parameter)
    fluorochrome = models.ForeignKey(Fluorochrome)

    # override clean to prevent duplicate Fl's for a parameter...
    # unique_together doesn't work for forms with the parameter excluded
    def clean(self):
        """
        Verify the parameter & fluorochrome combo doesn't already exist
        """

        qs = ParameterFluorochromeMap.objects.filter(
            parameter=self.parameter,
            fluorochrome=self.fluorochrome)

        if qs.exists():
            raise ValidationError(
                "This fluorochrome is already included in this parameter."
            )

    def __unicode__(self):
        return u'%s: %s' % (self.parameter, self.antibody)

    def __unicode__(self):
        return u'%s: %s' % (self.parameter, self.fluorochrome)


class ProjectPanel(ProtectedModel):
    project = models.ForeignKey(Project, null=False, blank=False)
    panel_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=128)
    panel_description = models.TextField(
        "Project Panel Description",
        null=True,
        blank=True,
        help_text="A short description of the project panel")

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
        return u'%s (Project: %s)' % (
            self.panel_name,
            self.project.project_name)


class ProjectPanelParameterMap(ProtectedModel):
    project_panel = models.ForeignKey(ProjectPanel)
    parameter = models.ForeignKey(Parameter)
    value_type = models.ForeignKey(ParameterValueType)

    def _get_name(self):
        """
        Returns the parameter name with value type.
        """
        return '%s-%s' % (
            self.parameter.parameter_short_name,
            self.value_type.value_type_short_name)

    name = property(_get_name)

    class Meta:
        ordering = ['parameter']

    def clean(self):
        """
        Check for duplicate parameter/value_type combos in a panel.
        Returns ValidationError if any duplicates are found.
        """

        # first check that there are no empty values
        error_message = []
        if not hasattr(self, 'project_panel'):
            error_message.append("Project Panel is required")
        if not hasattr(self, 'parameter'):
            error_message.append("Parameter is required")
        if not hasattr(self, 'value_type'):
            error_message.append("Value type is required")

        if len(error_message) > 0:
            raise ValidationError(error_message)

        # count panel mappings with matching parameter and value_type,
        # which don't have this pk
        ppm_duplicates = ProjectPanelParameterMap.objects.filter(
            project_panel=self.project_panel,
            parameter=self.parameter,
            value_type=self.value_type).exclude(id=self.id)

        if ppm_duplicates.count() > 0:
            raise ValidationError(
                "Parameter & value type combination already exists in this panel"
            )

    def __unicode__(self):
        return u'Panel: %s, Parameter: %s-%s' % (
            self.project_panel,
            self.parameter,
            self.value_type
        )


class SitePanel(ProtectedModel):
    # a SitePanel must be "based" off of a ProjectPanel
    # and is required to have at least the parameters specified in the
    # its ProjectPanel
    project_panel = models.ForeignKey(ProjectPanel, null=False, blank=False)
    site = models.ForeignKey(Site, null=False, blank=False)
    panel_name = models.CharField(
        unique=False,
        null=False,
        blank=False,
        max_length=128)
    panel_description = models.TextField(
        "Site Panel Description",
        null=True,
        blank=True,
        help_text="A short description of the site panel")

    def has_view_permission(self, user):

        if user.has_perm('view_project_data', self.site.project):
            return True
        elif self.site is not None:
            if user.has_perm('view_site_data', self.site):
                return True

        return False

    def clean(self):
        """
        Check for duplicate panel names within a project site.
        Returns ValidationError if any duplicates are found.
        """

        # count panels with matching panel_name and parent site,
        # which don't have this pk
        try:
            Site.objects.get(id=self.site_id)
        except ObjectDoesNotExist:
            return  # Site is required and will get caught by Form.is_valid()

        duplicates = SitePanel.objects.filter(
            panel_name=self.panel_name,
            site=self.site).exclude(
                id=self.id)
        if duplicates.count() > 0:
            raise ValidationError(
                "A panel with this name already exists in this site."
            )

        # project panel must be in the same project as the site
        if self.site.project_id != self.project_panel.project_id:
            raise ValidationError("Project Panel chosen is not in site's project.")

    def __unicode__(self):
        return u'%s (Project: %s, Site: %s)' % (
            self.panel_name,
            self.site.project.project_name,
            self.site.site_name)


class SitePanelParameterMap(ProtectedModel):
    site_panel = models.ForeignKey(SitePanel)
    parameter = models.ForeignKey(Parameter)
    value_type = models.ForeignKey(ParameterValueType)
    # fcs_text should match the FCS required keyword $PnN,
    # the short name for parameter n.
    fcs_text = models.CharField(
        "FCS Text",
        max_length=32,
        null=False,
        blank=False)

    fcs_opt_text = models.CharField(
        "FCS Optional Text",
        max_length=32,
        null=True,
        blank=True)

    def _get_name(self):
        """
        Returns the parameter name with value type.
        """
        return '%s-%s' % (
            self.parameter.parameter_short_name,
            self.value_type.value_type_short_name)

    name = property(_get_name)

    class Meta:
        ordering = ['fcs_text']

    def clean(self):
        """
        Check for duplicate parameter/value_type combos in a panel.
        Returns ValidationError if any duplicates are found.
        """

        # first check that there are no empty values
        error_message = []
        if not hasattr(self, 'site_panel'):
            error_message.append("Site Panel is required")
        if not hasattr(self, 'parameter'):
            error_message.append("Parameter is required")
        if not hasattr(self, 'value_type'):
            error_message.append("Value type is required")
        if not hasattr(self, 'fcs_text'):
            error_message.append("FCS Text is required")

        if len(error_message) > 0:
            raise ValidationError(error_message)

        # count panel mappings with matching parameter and value_type,
        # which don't have this pk
        ppm_duplicates = SitePanelParameterMap.objects.filter(
            site_panel=self.site_panel,
            parameter=self.parameter,
            value_type=self.value_type).exclude(id=self.id)

        if ppm_duplicates.count() > 0:
            raise ValidationError(
                "This combination already exists in this panel"
            )

        panel_fcs_text_duplicates = SitePanelParameterMap.objects.filter(
            site_panel=self.site_panel,
            fcs_text=self.fcs_text).exclude(id=self.id)

        if panel_fcs_text_duplicates.count() > 0:
            raise ValidationError("A site panel cannot have duplicate FCS text")

        if self.fcs_text == '':
            raise ValidationError("FCS Text is required")

    def __unicode__(self):
        return u'Panel: %s, Parameter: %s-%s' % (
            self.site_panel,
            self.parameter,
            self.value_type
        )


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
        return u'%s (Project: %s)' % (self.group_name, self.project.project_name)


class Subject(ProtectedModel):
    project = models.ForeignKey(Project)
    subject_group = models.ForeignKey(
        SubjectGroup,
        null=True,
        blank=True)
    subject_id = models.CharField(
        "Subject ID",
        null=False,
        blank=False,
        max_length=128)

    def has_view_permission(self, user):
        if self.project in Project.objects.get_projects_user_can_view(user):
            return True
        return False

    def clean(self):
        """
        Check for duplicate subject ID in a project.
        Returns ValidationError if any duplicates are found.
        """

        # count subjects with matching subject_id and parent project,
        # which don't have this pk
        try:
            Project.objects.get(id=self.project_id)
        except ObjectDoesNotExist:
            return  # Project is required and will get caught by Form.is_valid()

        if self.subject_group is not None and self.subject_group.project_id != self.project_id:
            raise ValidationError("Group chosen is not in this Project")

        subject_duplicates = Subject.objects.filter(
            subject_id=self.subject_id,
            project=self.project).exclude(
                id=self.id)
        if subject_duplicates.count() > 0:
            raise ValidationError(
                "Subject ID already exists in this project."
            )

    def __unicode__(self):
        return u'%s' % self.subject_id


class ProjectVisitType(ProtectedModel):
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

        duplicates = ProjectVisitType.objects.filter(
            visit_type_name=self.visit_type_name,
            project=self.project).exclude(
                id=self.id)
        if duplicates.count() > 0:
            raise ValidationError("Visit Name already exists in this project.")

    def __unicode__(self):
        return u'%s' % self.visit_type_name


def fcs_file_path(instance, filename):
    project_id = instance.subject.project_id
    subject_id = instance.subject_id
    
    upload_dir = join(['ReFlow-data', str(project_id), str(subject_id), str(filename)], "/")

    return upload_dir


# SampleGroup is used mainly for grouping samples by stimulation (site global)
class SampleGroup(models.Model):
    group_name = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=128)
    group_description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.group_name


class Sample(ProtectedModel):
    subject = models.ForeignKey(
        Subject,
        null=False,
        blank=False)
    site = models.ForeignKey(
        Site,
        null=False,
        blank=False)
    visit = models.ForeignKey(
        ProjectVisitType,
        null=False,
        blank=False)
    specimen = models.ForeignKey(
        Specimen,
        null=False,
        blank=False)
    sample_group = models.ForeignKey(
        SampleGroup,
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

    def has_view_permission(self, user):

        if user.has_perm('view_project_data', self.subject.project):
            return True
        elif self.site is not None:
            if user.has_perm('view_site_data', self.site):
                return True

        return False

    # Disabled b/c sample_file may not be local...S3 storage, etc.
    # def get_data_as_numpy(self):
    #     fcs = fcm.loadFCS(self.sample_file.file.name)
    #     return fcs.view()
    #
    # def get_fcs_data(self):
    #     data = self.get_data_as_numpy()
    #     header = []
    #     if self.sampleparametermap_set.count():
    #         params = self.sampleparametermap_set.all()
    #         for param in params.order_by('fcs_number'):
    #             if param.parameter and param.value_type:
    #                 header.append(
    #                     '%s-%s' % (
    #                         param.parameter.parameter_short_name,
    #                         param.value_type.value_type_short_name
    #                     )
    #                 )
    #             else:
    #                 header.append('%s' % param.fcs_text)
    #
    #     # Need a category column for the d3 selection to work
    #     data_with_cat = numpy.zeros((data.shape[0], data.shape[1] + 1))
    #     data_with_cat[:, :-1] = data
    #
    #     # need to convert it to csv-style string with header row
    #     csv_data = cStringIO.StringIO()
    #     csv_data.write(','.join(header) + ',category\n')
    #
    #     # currently limiting to 100 rows b/c the browser can't handle too much
    #     numpy.savetxt(csv_data, data_with_cat[:100, :], fmt='%d', delimiter=',')
    #
    #     return csv_data.getvalue()

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
                "An FCS file with this SHA-1 hash exists in this Project."
            )

        if self.site is not None and self.site.project_id != self.subject.project_id:
            raise ValidationError("Site chosen is not in this Project")

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

        # Start collecting channel info even though we don't know the parameter
        # Note: the SampleParameterMap instances are saved in overridden save

        # Read the FCS text segment and get the number of parameters
        sample_text_segment = fcm_obj.notes.text

        if 'par' in sample_text_segment:
            if not sample_text_segment['par'].isdigit():
                raise ValidationError(
                    "FCS file reports non-numeric parameter count"
                )
        else:
            raise ValidationError("No parameters found in FCS file")

        # Get our parameter numbers from all the PnN matches
        sample_parameters = {}  # parameter_number: PnN text
        for key in sample_text_segment:
            matches = re.search('^P(\d+)([N,S])$', key, flags=re.IGNORECASE)
            if matches:
                channel_number = matches.group(1)
                n_or_s = str.lower(matches.group(2))
                if channel_number not in sample_parameters:
                    sample_parameters[channel_number] = {}
                sample_parameters[channel_number][n_or_s] = sample_text_segment[key]

        self._sample_parameters = sample_parameters

    def save(self, *args, **kwargs):
        super(Sample, self).save(*args, **kwargs)

        # Save all the parameters as SampleParameterMap instances if
        # we have _sample_parameters
        # Check if sample has any parameters, could happen if
        # someone 'edits' an existing sample
        if hasattr(self, '_sample_parameters') and self.sampleparametermap_set.count() == 0:
            for key in self._sample_parameters:
                spm = SampleParameterMap()
                spm.sample = self
                spm.fcs_number = key
                spm.fcs_text = self._sample_parameters[key].get('n')
                spm.fcs_opt_text = self._sample_parameters[key].get('s', '')
                spm.save()

    def __unicode__(self):
        return u'Project: %s, Subject: %s, Sample File: %s' % (
            self.subject.project.project_name,
            self.subject.subject_id,
            self.sample_file.name.split('/')[-1])


class SampleSet(ProtectedModel):
    """
    An arbitrary collection of Sample instances within a Project
    """
    project = models.ForeignKey(Project)

    # Maybe name should be non-editable and auto-generated based on date/user combo???
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
            raise ValidationError("Could not find specified samples. Check that they exist.")

        for sample in samples_to_add:
            print "Sample Set Project: ", sample_set.project_id
            print "Sample Project: ", sample.subject.project_id
            if sample_set.project_id != sample.subject.project_id:
                raise ValidationError(
                    "Samples must belong to the specified project."
                )

models.signals.m2m_changed.connect(validate_samples, sender=SampleSet.samples.through)


class SampleParameterMap(ProtectedModel):
    sample = models.ForeignKey(Sample)

    # The parameter and value_type may not be known on initial import,
    # thus null, blank = True
    parameter = models.ForeignKey(Parameter, null=True, blank=True)
    value_type = models.ForeignKey(ParameterValueType, null=True, blank=True)

    # fcs_text should match the FCS required keyword $PnN,
    # the short name for parameter n.
    fcs_text = models.CharField(
        "FCS PnN",
        max_length=32,
        null=False,
        blank=False)

    # fcs_opt_text matches the optional FCS keyword $PnS
    fcs_opt_text = models.CharField(
        "FCS PnS",
        max_length=32,
        null=True,
        blank=True)

    # fcs_number represents the parameter number in the FCS file
    # Ex. If the fcs_number == 3, then fcs_text should be in P3N.
    fcs_number = models.IntegerField()

    def _get_name(self):
        """
        Returns the parameter name with value type, or empty string if none
        """
        if self.parameter and self.value_type:
            return '%s-%s' % (
                self.parameter.parameter_short_name,
                self.value_type.value_type_short_name
            )
        else:
            return ''

    name = property(_get_name)

    class Meta:
        unique_together = (('sample', 'fcs_text'),)

    def __unicode__(self):
            return u'SampleID: %s, Parameter: %s-%s, Number: %s, Text: %s' % (
                self.sample_id,
                self.parameter,
                self.value_type,
                self.fcs_number,
                self.fcs_text)


def compensation_file_path(instance, filename):
    project_id = instance.site.project_id
    site_id = instance.site_id

    upload_dir = join(
        ['ReFlow-data', str(project_id), 'compensation', str(site_id), str(filename)],
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


class SampleCompensationMap(ProtectedModel):
    sample = models.ForeignKey(Sample, null=False, blank=False)
    compensation = models.ForeignKey(Compensation, null=False, blank=False)

    class Meta:
        unique_together = (('sample', 'compensation'),)

    def clean(self):
        """
        Verify the compensation and sample belong to the same site
        """

        if self.sample.site != self.compensation.site:
            raise ValidationError(
                "Compensation matrix must belong to the same site as the sample."
            )
