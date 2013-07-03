from operator import attrgetter

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.forms.models import inlineformset_factory

from guardian.shortcuts import assign_perm
from guardian.forms import UserObjectPermissionsForm

from repository.models import *
from repository.forms import *
from repository.utils import apply_panel_to_sample


@login_required
def permission_denied(request):
    raise PermissionDenied


@login_required
def home(request):

    projects = Project.objects.get_projects_user_can_view(request.user)

    return render_to_response(
        'home.html',
        {
            'projects': sorted(projects, key=attrgetter('project_name')),
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_antibodies(request):

    antibodies = Antibody.objects.all().values(
        'id',
        'antibody_short_name',
        'antibody_name',
        'antibody_description',
    )

    pa_maps = ParameterAntibodyMap.objects.filter(
        antibody_id__in=[i['id'] for i in antibodies]).values(
            'id',
            'antibody_id',
            'parameter__parameter_short_name',
            'parameter__parameter_type',
        )

    for antibody in antibodies:
        antibody['parameters'] = [
            i for i in pa_maps if i['antibody_id'] == antibody['id']
        ]

    return render_to_response(
        'view_antibodies.html',
        {
            'antibodies': antibodies,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def add_antibody(request):
    if request.method == 'POST':
        form = AntibodyForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_antibodies'))
    else:
        form = AntibodyForm()

    return render_to_response(
        'add_antibody.html',
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def edit_antibody(request, antibody_id):
    antibody = get_object_or_404(Antibody, pk=antibody_id)

    if request.method == 'POST':
        form = AntibodyForm(request.POST, instance=antibody)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_antibodies'))
    else:
        form = AntibodyForm(instance=antibody)

    return render_to_response(
        'edit_antibody.html',
        {
            'antibody': antibody,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_fluorochromes(request):

    fluorochromes = Fluorochrome.objects.all().values(
        'id',
        'fluorochrome_short_name',
        'fluorochrome_name',
        'fluorochrome_description',
    )

    pf_maps = ParameterFluorochromeMap.objects.filter(
        fluorochrome_id__in=[i['id'] for i in fluorochromes]).values(
            'id',
            'fluorochrome_id',
            'parameter__parameter_short_name',
            'parameter__parameter_type',
        )

    for fluorochrome in fluorochromes:
        fluorochrome['parameters'] = [
            i for i in pf_maps if i['fluorochrome_id'] == fluorochrome['id']
        ]

    return render_to_response(
        'view_fluorochromes.html',
        {
            'fluorochromes': fluorochromes,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def add_fluorochrome(request):
    if request.method == 'POST':
        form = FluorochromeForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_fluorochromes'))
    else:
        form = FluorochromeForm()

    return render_to_response(
        'add_fluorochrome.html',
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def edit_fluorochrome(request, fluorochrome_id):
    fluorochrome = get_object_or_404(Fluorochrome, pk=fluorochrome_id)

    if request.method == 'POST':
        form = FluorochromeForm(request.POST, instance=fluorochrome)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_fluorochromes'))
    else:
        form = FluorochromeForm(instance=fluorochrome)

    return render_to_response(
        'edit_fluorochrome.html',
        {
            'fluorochrome': fluorochrome,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_parameters(request):

    parameters = Parameter.objects.all()

    return render_to_response(
        'view_parameters.html',
        {
            'parameters': parameters,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def add_parameter(request):
    if request.method == 'POST':
        form = ParameterForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_parameters'))
    else:
        form = ParameterForm()

    return render_to_response(
        'add_parameter.html',
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def associate_antibody_to_parameter(request, parameter_id):
    parameter = get_object_or_404(Parameter, pk=parameter_id)
    pa_map = ParameterAntibodyMap(parameter_id=parameter_id)

    if request.method == 'POST':
        form = ParameterAntibodyMapForm(request.POST, instance=pa_map)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_parameters'))
    else:
        form = ParameterAntibodyMapForm(instance=pa_map)

    return render_to_response(
        'associate_antibody_to_parameter.html',
        {
            'parameter': parameter,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def remove_parameter_antibody(request, pa_map_id):
    pa_map = get_object_or_404(ParameterAntibodyMap, pk=pa_map_id)

    pa_map.delete()

    return HttpResponseRedirect(reverse('view_parameters',))


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def associate_fluorochrome_to_parameter(request, parameter_id):
    parameter = get_object_or_404(Parameter, pk=parameter_id)
    pf_map = ParameterFluorochromeMap(parameter_id=parameter_id)

    if request.method == 'POST':
        form = ParameterFluorochromeMapForm(request.POST, instance=pf_map)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_parameters'))
    else:
        form = ParameterFluorochromeMapForm(instance=pf_map)

    return render_to_response(
        'associate_fluorochrome_to_parameter.html',
        {
            'parameter': parameter,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def remove_parameter_fluorochrome(request, pf_map_id):
    pf_map = get_object_or_404(ParameterFluorochromeMap, pk=pf_map_id)

    pf_map.delete()

    return HttpResponseRedirect(reverse('view_parameters',))


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def edit_parameter(request, parameter_id):
    parameter = get_object_or_404(Parameter, pk=parameter_id)

    if request.method == 'POST':
        form = ParameterForm(request.POST, instance=parameter)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_parameters'))
    else:
        form = ParameterForm(instance=parameter)

    return render_to_response(
        'edit_parameter.html',
        {
            'parameter': parameter,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_specimens(request):

    specimens = Specimen.objects.all().values(
        'id',
        'specimen_name',
        'specimen_description',
    )

    return render_to_response(
        'view_specimens.html',
        {
            'specimens': specimens,
        },
        context_instance=RequestContext(request)
    )

@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def add_specimen(request):
    if request.method == 'POST':
        form = SpecimenForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_specimens'))
    else:
        form = SpecimenForm()

    return render_to_response(
        'add_specimen.html',
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def edit_specimen(request, specimen_id):
    specimen = get_object_or_404(Specimen, pk=specimen_id)

    if request.method == 'POST':
        form = SpecimenForm(request.POST, instance=specimen)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_specimens'))
    else:
        form = SpecimenForm(instance=specimen)

    return render_to_response(
        'edit_specimen.html',
        {
            'specimen': specimen,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user_sites = Site.objects.get_sites_user_can_view(request.user, project=project)

    if not (project.has_view_permission(request.user) or user_sites.count() > 0):
        raise PermissionDenied

    can_add_project_data = project.has_add_permission(request.user)
    can_modify_project_data = project.has_modify_permission(request.user)
    can_manage_project_users = project.has_user_management_permission(request.user)

    return render_to_response(
        'view_project.html',
        {
            'project': project,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
            'can_manage_project_users': can_manage_project_users,
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save()

            # Automatically add the request user to the project with all
            # permissions...it's the polite thing to do
            assign_perm('view_project_data', request.user, project)
            assign_perm('add_project_data', request.user, project)
            assign_perm('modify_project_data', request.user, project)
            assign_perm('manage_project_users', request.user, project)

            return HttpResponseRedirect(reverse('view_project', args=(project.id,)))
    else:
        form = ProjectForm()

    return render_to_response(
        'add_project.html',
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if not project.has_modify_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            project = form.save()
            return HttpResponseRedirect(reverse('view_project', args=(project.id,)))
    else:
        form = ProjectForm(instance=project)

    return render_to_response(
        'edit_project.html',
        {
            'project': project,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_project_users(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    can_manage_project_users = project.has_user_management_permission(request.user)

    if not can_manage_project_users:
        raise PermissionDenied

    project_users = project.get_project_users()

    return render_to_response(
        'view_project_users.html',
        {
            'project': project,
            'project_users': project_users,
            'can_manage_project_users': can_manage_project_users,
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_user_permissions(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if not project.has_user_management_permission(request.user):
        raise PermissionDenied

    form = UserSelectForm(request.POST or None, project_id=project_id)

    if request.method == 'POST' and form.is_valid():
        if request.POST['site']:
            return HttpResponseRedirect(reverse(
                'manage_site_user',
                args=(request.POST['site'], request.POST['user'])))
        else:
            return HttpResponseRedirect(reverse(
                'manage_project_user',
                args=(project.id, request.POST['user'])))

    return render_to_response(
        'add_user_permissions.html',
        {
            'project': project,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def manage_project_user(request, project_id, user_id):
    project = get_object_or_404(Project, pk=project_id)
    project_user = get_object_or_404(User, pk=user_id)

    if not project.has_user_management_permission(request.user):
        raise PermissionDenied

    form = UserObjectPermissionsForm(project_user, project, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save_obj_perms()
        return HttpResponseRedirect(reverse('view_project_users', args=(project.id,)))

    return render_to_response(
        'manage_project_user.html',
        {
            'project': project,
            'project_user': project_user,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def manage_site_user(request, site_id, user_id):
    site = get_object_or_404(Site, pk=site_id)
    user = get_object_or_404(User, pk=user_id)

    if not site.project.has_user_management_permission(request.user) or site.has_user_management_permission(request.user):
        raise PermissionDenied

    form = UserObjectPermissionsForm(user, site, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save_obj_perms()
        return HttpResponseRedirect(reverse('view_project_users', args=(site.project_id,)))

    return render_to_response(
        'manage_site_user.html',
        {
            'site': site,
            'site_user': user,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_subjects(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    user_sites = Site.objects.get_sites_user_can_view(request.user, project=project)

    if not (project.has_view_permission(request.user) or user_sites.count() > 0):
        raise PermissionDenied

    subjects = Subject.objects.filter(project=project).order_by('subject_id')

    can_add_project_data = project.has_add_permission(request.user)
    can_modify_project_data = project.has_modify_permission(request.user)

    return render_to_response(
        'view_project_subjects.html',
        {
            'project': project,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
            'subjects': subjects,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_samples(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user_view_sites = Site.objects.get_sites_user_can_view(request.user, project=project)

    # get user's sites based on their site_view_permission,
    # unless they have full project view permission
    if project.has_view_permission(request.user):
        samples = Sample.objects.filter(subject__project=project).values(
            'id',
            'subject__subject_id',
            'site__site_name',
            'site__id',
            'visit__visit_type_name',
            'sample_group__group_name',
            'specimen__specimen_name',
            'original_filename'
        )
    elif user_view_sites.count() > 0:
        samples = Sample.objects.filter(
            subject__project=project, site__in=user_view_sites).values(
                'id',
                'subject__subject_id',
                'site__site_name',
                'site__id',
                'visit__visit_type_name',
                'sample_group__group_name',
                'specimen__specimen_name',
                'original_filename'
            )
    else:
        raise PermissionDenied

    spm_maps = SampleParameterMap.objects.filter(
        sample_id__in=[i['id'] for i in samples]).values(
            'id',
            'sample_id',
            'fcs_number',
            'fcs_text',
            'fcs_opt_text',
            'parameter__parameter_short_name',
            'value_type__value_type_short_name',
        )

    for sample in samples:
        sample['parameters'] = [i for i in spm_maps if i['sample_id'] == sample['id']]

    can_add_project_data = project.has_add_permission(request.user)
    can_modify_project_data = project.has_modify_permission(request.user)
    user_add_sites = Site.objects.get_sites_user_can_add(
        request.user, project).values_list('id', flat=True)
    user_modify_sites = Site.objects.get_sites_user_can_modify(
        request.user, project).values_list('id', flat=True)

    return render_to_response(
        'view_project_samples.html',
        {
            'project': project,
            'samples': samples,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
            'user_add_sites': user_add_sites,
            'user_modify_sites': user_modify_sites
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_sites(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    sites = Site.objects.get_sites_user_can_view(request.user, project=project)

    if not (project.has_view_permission(request.user) or sites.count() > 0):
        raise PermissionDenied

    can_add_project_data = project.has_add_permission(request.user)
    can_modify_project_data = project.has_modify_permission(request.user)

    return render_to_response(
        'view_project_sites.html',
        {
            'project': project,
            'sites': sites,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_site(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if not project.has_add_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        site = Site(project=project)
        form = SiteForm(request.POST, instance=site)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('project_sites', args=project_id))
    else:
        form = SiteForm()

    return render_to_response(
        'add_site.html',
        {
            'form': form,
            'project': project,
        },
        context_instance=RequestContext(request)
    )


@login_required
def edit_site(request, project_id, site_id):
    site = get_object_or_404(Site, pk=site_id, project_id=project_id)

    if not site.project.has_modify_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = SiteForm(request.POST, instance=site)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_sites', args=str(site.project_id)))
    else:
        form = SiteForm(instance=site)

    return render_to_response(
        'edit_site.html',
        {
            'form': form,
            'site': site,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_site(request, site_id):
    site = get_object_or_404(Site, pk=site_id)
    project = site.project

    # get user's sites based on their site_view_permission,
    # unless they have full project view permission
    if project.has_view_permission(request.user) or site.has_view_permission(request.user):
        samples = Sample.objects.filter(site=site).values(
            'id',
            'subject__subject_id',
            'site__site_name',
            'site__id',
            'visit__visit_type_name',
            'sample_group__group_name',
            'specimen__specimen_name',
            'original_filename'
        )
    else:
        raise PermissionDenied

    spm_maps = SampleParameterMap.objects.filter(
        sample_id__in=[i['id'] for i in samples]).values(
            'id',
            'sample_id',
            'fcs_number',
            'fcs_text',
            'fcs_opt_text',
            'parameter__parameter_short_name',
            'value_type__value_type_short_name',
        )

    # this is done to avoid hitting the database too hard in templates
    for sample in samples:
        sample['parameters'] = [i for i in spm_maps if i['sample_id'] == sample['id']]

    can_add_project_data = project.has_add_permission(request.user)
    can_modify_project_data = project.has_modify_permission(request.user)
    user_add_sites = Site.objects.get_sites_user_can_add(
        request.user, project).values_list('id', flat=True)
    user_modify_sites = Site.objects.get_sites_user_can_modify(
        request.user, project).values_list('id', flat=True)

    return render_to_response(
        'view_site.html',
        {
            'project': project,
            'site': site,
            'samples': samples,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
            'user_add_sites': user_add_sites,
            'user_modify_sites': user_modify_sites
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_site_uncategorized_samples(request, site_id):
    site = get_object_or_404(Site, pk=site_id)
    project = site.project

    # get user's sites based on their site_view_permission,
    # unless they have full project view permission
    if project.has_view_permission(request.user) or site.has_view_permission(request.user):
        uncat_spm = SampleParameterMap.objects.filter(parameter=None, sample__site_id=site_id)
        uncat_sample_ids = uncat_spm.values_list('sample__id').distinct()
        samples = Sample.objects.filter(id__in=uncat_sample_ids).values(
            'id',
            'subject__subject_id',
            'site__site_name',
            'site__id',
            'visit__visit_type_name',
            'sample_group__group_name',
            'specimen__specimen_name',
            'original_filename'
        )
    else:
        raise PermissionDenied

    spm_maps = SampleParameterMap.objects.filter(
        sample_id__in=[i['id'] for i in samples]).values(
            'id',
            'sample_id',
            'fcs_number',
            'fcs_text',
            'fcs_opt_text',
            'parameter__parameter_short_name',
            'value_type__value_type_short_name',
        )

    # this is done to avoid hitting the database too hard in templates
    for sample in samples:
        sample['parameters'] = [i for i in spm_maps if i['sample_id'] == sample['id']]

    can_add_project_data = project.has_add_permission(request.user)
    can_modify_project_data = project.has_modify_permission(request.user)
    user_add_sites = Site.objects.get_sites_user_can_add(
        request.user, project).values_list('id', flat=True)
    user_modify_sites = Site.objects.get_sites_user_can_modify(
        request.user, project).values_list('id', flat=True)

    return render_to_response(
        'view_site_uncategorized.html',
        {
            'project': project,
            'site': site,
            'samples': samples,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
            'user_add_sites': user_add_sites,
            'user_modify_sites': user_modify_sites
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_compensations(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user_view_sites = Site.objects.get_sites_user_can_view(request.user, project=project)

    if project.has_view_permission(request.user):
        compensations = Compensation.objects\
            .select_related()\
            .filter(site__project=project)\
            .order_by('original_filename')
    elif user_view_sites.count() > 0:
        compensations = Compensation.objects\
            .select_related()\
            .filter(site__in=user_view_sites)\
            .order_by('original_filename')
    else:
        raise PermissionDenied

    can_add_project_data = project.has_add_permission(request.user)
    can_modify_project_data = project.has_modify_permission(request.user)
    user_add_sites = Site.objects.get_sites_user_can_add(
        request.user, project).values_list('id', flat=True)
    user_modify_sites = Site.objects.get_sites_user_can_modify(
        request.user, project).values_list('id', flat=True)

    return render_to_response(
        'view_project_compensations.html',
        {
            'project': project,
            'compensations': compensations,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
            'user_add_sites': user_add_sites,
            'user_modify_sites': user_modify_sites
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_compensation(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    user_sites = Site.objects.get_sites_user_can_add(request.user, project)

    if not (project.has_add_permission(request.user) or user_sites.count() > 0):
        raise PermissionDenied

    if request.method == 'POST':
        form = CompensationForm(
            request.POST,
            request.FILES,
            project_id=project_id,
            request=request)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_compensations', args=project_id))
    else:
        form = CompensationForm(project_id=project_id, request=request)

    return render_to_response(
        'add_compensation.html',
        {
            'form': form,
            'project': project,
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_site_compensation(request, site_id):
    site = get_object_or_404(Subject, pk=site_id)

    if not site.has_add_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        compensation = Compensation(site=site)
        form = CompensationForm(
            request.POST,
            request.FILES,
            instance=compensation,
            request=request)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_site', args=site_id))
    else:
        form = CompensationForm(request=request)

    return render_to_response(
        'add_compensation.html',
        {
            'form': form,
            'project': site.project,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_visit_types(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user_sites = Site.objects.get_sites_user_can_view(request.user, project=project)

    if not (project.has_view_permission(request.user) or user_sites.count() > 0):
        raise PermissionDenied

    visit_types = ProjectVisitType.objects.filter(project=project).order_by('visit_type_name')

    can_add_project_data = project.has_add_permission(request.user)
    can_modify_project_data = project.has_modify_permission(request.user)

    return render_to_response(
        'view_project_visit_types.html',
        {
            'project': project,
            'visit_types': visit_types,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_visit_type(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if not project.has_add_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        visit_type = ProjectVisitType(project=project)
        form = ProjectVisitTypeForm(request.POST, instance=visit_type)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_visit_types', args=project_id))
    else:
        form = ProjectVisitTypeForm()

    return render_to_response(
        'add_visit_type.html',
        {
            'form': form,
            'project': project,
        },
        context_instance=RequestContext(request)
    )


@login_required
def edit_visit_type(request, project_id, visit_type_id):
    visit_type = get_object_or_404(ProjectVisitType, pk=visit_type_id, project_id=project_id)

    if not visit_type.project.has_modify_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = ProjectVisitTypeForm(request.POST, instance=visit_type)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(
                'project_visit_types',
                args=str(visit_type.project_id)))
    else:
        form = ProjectVisitTypeForm(instance=visit_type)

    return render_to_response(
        'edit_visit_type.html',
        {
            'form': form,
            'visit_type': visit_type,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_project_panels(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user_view_sites = Site.objects.get_sites_user_can_view(request.user, project=project)

    if request.method == 'POST':
        if 'panel' in request.POST:

            panel = get_object_or_404(Panel, pk=request.POST['panel'])
            ppm = PanelParameterMap(panel=panel)
            form = PanelParameterMapForm(request.POST, instance=ppm)

            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse(
                    'project_panels',
                    args=str(panel.site.project_id)))
            else:
                json = simplejson.dumps(form.errors)
                return HttpResponseBadRequest(json, mimetype='application/json')

    # get user's panels based on their site_view_permission,
    # unless they have full project view permission
    if project.has_view_permission(request.user):
        panels = Panel.objects.filter(site__project=project).values(
            'id',
            'panel_name',
            'panel_description',
            'site__site_name',
            'site__id'
        )
    elif user_view_sites.count() > 0:
        panels = Panel.objects.filter(site__project=project, site__in=user_view_sites).values(
            'id',
            'panel_name',
            'panel_description',
            'site__site_name',
            'site__id'
        )
    else:
        raise PermissionDenied

    ppm_maps = PanelParameterMap.objects.filter(panel_id__in=[i['id'] for i in panels]).values(
        'id',
        'panel_id',
        'fcs_text',
        'parameter__parameter_short_name',
        'value_type__value_type_name',
    )

    for panel in panels:
        panel['parameters'] = [i for i in ppm_maps if i['panel_id'] == panel['id']]

    # for adding new parameters to panels
    form = PanelParameterMapForm()

    can_add_project_data = project.has_add_permission(request.user)
    can_modify_project_data = project.has_modify_permission(request.user)
    user_add_sites = Site.objects.get_sites_user_can_add(
        request.user, project).values_list('id', flat=True)
    user_modify_sites = Site.objects.get_sites_user_can_modify(
        request.user, project).values_list('id', flat=True)

    return render_to_response(
        'view_project_panels.html',
        {
            'project': project,
            'panels': panels,
            'form': form,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
            'user_add_sites': user_add_sites,
            'user_modify_sites': user_modify_sites
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_panel(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user_sites = Site.objects.get_sites_user_can_add(request.user, project)

    if not (project.has_add_permission(request.user) or user_sites.count() > 0):
        raise PermissionDenied

    # need to check if the project has any sites, since panels have a required site relation
    if request.method == 'POST' and project.site_set.exists():
        form = PanelForm(request.POST, project_id=project_id)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_panels', args=project_id))

    elif not project.site_set.exists():
        messages.warning(
            request,
            'This project has no sites. A panel must be associated with a specific site.')
        return HttpResponseRedirect(reverse('warning_page',))

    else:
        form = PanelForm(project_id=project_id)

    return render_to_response(
        'add_panel.html',
        {
            'form': form,
            'project': project,
        },
        context_instance=RequestContext(request)
    )


@login_required
def edit_panel(request, panel_id):
    panel = get_object_or_404(Panel, pk=panel_id)

    if not panel.site.has_modify_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = PanelEditForm(request.POST, instance=panel)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(
                'project_panels',
                args=str(panel.site.project_id)))
    else:
        form = PanelEditForm(instance=panel)

    return render_to_response(
        'edit_panel.html',
        {
            'form': form,
            'panel': panel,
        },
        context_instance=RequestContext(request)
    )


@login_required
def remove_panel_parameter(request, panel_parameter_id):
    ppm = get_object_or_404(PanelParameterMap, pk=panel_parameter_id)

    if not ppm.panel.site.has_modify_permission(request.user):
        raise PermissionDenied

    project = ppm.panel.site.project
    ppm.delete()

    return HttpResponseRedirect(reverse('project_panels', args=str(project.id)))


@login_required
def create_panel_from_sample(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)

    if not sample.site.has_add_permission(request.user):
        raise PermissionDenied

    ParameterFormSet = inlineformset_factory(
        Panel,
        PanelParameterMap,
        form=PanelParameterMapFromSampleForm,
        extra=sample.sampleparametermap_set.count(),
        can_delete=False,
    )
    parameter_formset = None

    if request.method == 'POST':
        panel_form = PanelFromSampleForm(request.POST, instance=Panel(site=sample.site))

        if panel_form.is_valid():
            panel = panel_form.save(commit=False)
            parameter_formset = ParameterFormSet(request.POST, instance=panel)

            if parameter_formset.is_valid():
                panel.save()
                parameter_formset.save()

                return HttpResponseRedirect(reverse(
                    'project_panels',
                    args=str(sample.subject.project_id)))

    else:
        # need to check if the sample is associated with a site,
        # since panels have a required site relation
        if sample.site:
            panel = Panel(site=sample.site, panel_name=sample.original_filename)
            panel_form = PanelFromSampleForm(instance=panel)

            initial_param_data = list()
            for param in sample.sampleparametermap_set.all().order_by('fcs_text'):
                initial_param_data.append({
                    'fcs_text': param.fcs_text,
                    'fcs_opt_text': param.fcs_opt_text
                })

            parameter_formset = ParameterFormSet(instance=panel, initial=initial_param_data)

        else:
            messages.warning(
                request,
                'This sample is not associated with a site.')
            return HttpResponseRedirect(reverse('warning_page', ))

    return render_to_response(
        'create_panel_from_sample.html',
        {
            'panel_form': panel_form,
            'parameter_formset': parameter_formset,
            'sample': sample,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_subject_groups(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user_sites = Site.objects.get_sites_user_can_view(request.user, project=project)

    if not (project.has_view_permission(request.user) or user_sites.count() > 0):
        raise PermissionDenied

    subject_groups = SubjectGroup.objects.filter(project=project).order_by('group_name')

    can_add_project_data = project.has_add_permission(request.user)
    can_modify_project_data = project.has_modify_permission(request.user)

    return render_to_response(
        'view_subject_groups.html',
        {
            'project': project,
            'subject_groups': subject_groups,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_subject_group(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if not project.has_add_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        subject_group = SubjectGroup(project=project)
        form = SubjectGroupForm(request.POST, instance=subject_group)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('subject_groups', args=project_id))
    else:
        form = SubjectGroupForm()

    return render_to_response(
        'add_subject_group.html',
        {
            'form': form,
            'project': project,
        },
        context_instance=RequestContext(request)
    )


@login_required
def edit_subject_group(request, project_id, subject_group_id):
    subject_group = get_object_or_404(SubjectGroup, pk=subject_group_id, project_id=project_id)

    if not subject_group.project.has_modify_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = SubjectGroupForm(request.POST, instance=subject_group)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(
                'subject_groups',
                args=str(subject_group.project_id)))
    else:
        form = SubjectGroupForm(instance=subject_group)

    return render_to_response(
        'edit_subject_group.html',
        {
            'form': form,
            'subject_group': subject_group,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    project = subject.project
    user_sites = Site.objects.get_sites_user_can_view(request.user, project=project)

    # get user's sites based on their site_view_permission,
    # unless they have full project view permission
    if project.has_view_permission(request.user):
        samples = Sample.objects.filter(subject=subject).values(
            'id',
            'subject__subject_id',
            'site__site_name',
            'site__id',
            'visit__visit_type_name',
            'sample_group__group_name',
            'specimen__specimen_name',
            'original_filename'
        )
    elif user_sites.count() > 0:
        user_view_sites = Site.objects.get_sites_user_can_view(request.user, project=project)
        samples = Sample.objects.filter(subject=subject, site__in=user_view_sites).values(
            'id',
            'subject__subject_id',
            'site__site_name',
            'site__id',
            'visit__visit_type_name',
            'sample_group__group_name',
            'specimen__specimen_name',
            'original_filename'
        )
    else:
        raise PermissionDenied

    spm_maps = SampleParameterMap.objects.filter(
        sample_id__in=[i['id'] for i in samples]).values(
            'id',
            'sample_id',
            'fcs_number',
            'fcs_text',
            'fcs_opt_text',
            'parameter__parameter_short_name',
            'value_type__value_type_short_name',
        )

    # this is done to avoid hitting the database too hard in templates
    for sample in samples:
        sample['parameters'] = [i for i in spm_maps if i['sample_id'] == sample['id']]

    can_add_project_data = project.has_add_permission(request.user)
    can_modify_project_data = project.has_modify_permission(request.user)
    user_add_sites = Site.objects.get_sites_user_can_add(
        request.user, project).values_list('id', flat=True)
    user_modify_sites = Site.objects.get_sites_user_can_modify(
        request.user, project).values_list('id', flat=True)

    return render_to_response(
        'view_subject.html',
        {
            'project': project,
            'subject': subject,
            'samples': samples,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
            'user_add_sites': user_add_sites,
            'user_modify_sites': user_modify_sites
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_subject(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if not project.has_add_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        subject = Subject(project=project)
        form = SubjectForm(request.POST, instance=subject, project_id=project_id)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_subjects', args=project_id))

    else:
        form = SubjectForm(project_id=project_id)

    return render_to_response(
        'add_subject.html',
        {
            'form': form,
            'project': project,
        },
        context_instance=RequestContext(request)
    )


@login_required
def edit_subject(request, project_id, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id, project_id=project_id)

    if not subject.project.has_modify_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject, project_id=project_id)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_subject', args=subject_id))
    else:
        form = SubjectForm(instance=subject, project_id=project_id)

    return render_to_response(
        'edit_subject.html',
        {
            'form': form,
            'subject': subject,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_sample_groups(request):
    sample_groups = SampleGroup.objects.all().order_by('group_name')

    return render_to_response(
        'view_sample_groups.html',
        {
            'sample_groups': sample_groups,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def add_sample_group(request):
    if request.method == 'POST':
        sample_group = SampleGroup()
        form = SampleGroupForm(request.POST, instance=sample_group)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_sample_groups'))
    else:
        form = SampleGroupForm()

    return render_to_response(
        'add_sample_group.html',
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda user: user.is_superuser, login_url='/403', redirect_field_name=None)
def edit_sample_group(request, sample_group_id):
    sample_group = get_object_or_404(SampleGroup, pk=sample_group_id)

    if request.method == 'POST':
        form = SampleGroupForm(request.POST, instance=sample_group)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_sample_groups'))
    else:
        form = SampleGroupForm(instance=sample_group)

    return render_to_response(
        'edit_sample_group.html',
        {
            'form': form,
            'sample_group': sample_group,
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_sample(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user_sites = Site.objects.get_sites_user_can_add(request.user, project)

    if not (project.has_add_permission(request.user) or user_sites.count() > 0):
        raise PermissionDenied

    if request.method == 'POST':
        form = SampleForm(request.POST, request.FILES, project_id=project_id, request=request)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_samples', args=project_id))
    else:
        form = SampleForm(project_id=project_id, request=request)

    return render_to_response(
        'add_sample.html',
        {
            'form': form,
            'project': project,
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_subject_sample(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    user_sites = Site.objects.get_sites_user_can_add(request.user, subject.project)

    if not (subject.project.has_add_permission(request.user) or user_sites.count() > 0):
        raise PermissionDenied

    if request.method == 'POST':
        sample = Sample(subject=subject)
        form = SampleSubjectForm(request.POST, request.FILES, instance=sample, request=request)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_subject', args=subject_id))
    else:
        form = SampleSubjectForm(project_id=subject.project_id, request=request)

    return render_to_response(
        'add_subject_sample.html',
        {
            'form': form,
            'subject': subject,
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_site_sample(request, site_id):
    site = get_object_or_404(Site, pk=site_id)

    if not (site.project.has_add_permission(request.user) or site.has_view_permission(request.user)):
        raise PermissionDenied

    if request.method == 'POST':
        sample = Sample(site=site)
        form = SampleSiteForm(request.POST, request.FILES, instance=sample, request=request)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_site', args=site_id))
    else:
        form = SampleSiteForm(project_id=site.project_id, request=request)

    return render_to_response(
        'add_site_sample.html',
        {
            'form': form,
            'site': site,
        },
        context_instance=RequestContext(request)
    )


@login_required
def edit_sample(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)

    if not sample.site.has_modify_permission(request.user):
        raise PermissionDenied

    if request.method == 'POST':
        form = SampleEditForm(request.POST, request.FILES, instance=sample, request=request)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_subject', args=str(sample.subject_id)))
    else:
        form = SampleEditForm(
            instance=sample,
            project_id=sample.subject.project_id,
            request=request)

    return render_to_response(
        'edit_sample.html',
        {
            'form': form,
            'sample': sample,
        },
        context_instance=RequestContext(request)
    )


@login_required
def select_panel(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)

    if not sample.site.has_add_permission(request.user):
        raise PermissionDenied

    site_panels = Panel.objects.filter(site=sample.site)

    if request.method == 'POST':
        if 'panel' in request.POST:

            # Get the user selection
            selected_panel = get_object_or_404(Panel, pk=request.POST['panel'])

            try:
                status = apply_panel_to_sample(selected_panel, sample)
            except ValidationError as e:
                status = e.messages

            # if everything saved ok, then the status should be 0,
            # but might be an array of errors
            if status != 0:
                if isinstance(status, list):
                    json = simplejson.dumps(status)
                    return HttpResponseBadRequest(json, mimetype='application/json')
            else:
                return HttpResponseRedirect(reverse(
                    'view_subject',
                    args=str(sample.subject_id)))

    return render_to_response(
        'select_panel.html',
        {
            'sample': sample,
            'site_panels': site_panels,
        },
        context_instance=RequestContext(request)
    )


@login_required
def retrieve_sample(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)

    if not sample.site.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(sample.sample_file, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % sample.original_filename
    return response


@login_required
def retrieve_compensation(request, compensation_id):
    compensation = get_object_or_404(Compensation, pk=compensation_id)

    if not compensation.site.has_view_permission(request.user):
        raise PermissionDenied

    response = HttpResponse(compensation.compensation_file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % compensation.original_filename
    return response

# Disabled b/c get_fcs_data() won't work if FCS files are not local
# @login_required
# def sample_data(request, sample_id):
#     sample = get_object_or_404(Sample, pk=sample_id)
#
#     if not sample.site.has_view_permission(request.user):
#         raise PermissionDenied
#
#     return HttpResponse(sample.get_fcs_data(), content_type='text/csv')
#
#
# @login_required
# def view_sample_scatterplot(request, sample_id):
#     sample = get_object_or_404(Sample, pk=sample_id)
#
#     if not sample.site.has_view_permission(request.user):
#         raise PermissionDenied
#
#     return render_to_response(
#         'view_sample_scatterplot.html',
#         {
#             'sample': sample,
#         },
#         context_instance=RequestContext(request)
#     )