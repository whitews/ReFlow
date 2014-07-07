from operator import attrgetter

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from repository.models import *
from repository.forms import *


@login_required
def permission_denied(request):
    raise PermissionDenied


@login_required
def reflow_app(request):
    return render_to_response(
        'reflow_app.html',
        {},
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda u: u.is_superuser)
def process_request_app(request):
    return render_to_response(
        'process_request_app.html',
        {},
        context_instance=RequestContext(request)
    )


##############################
### Project specific views ###
##############################
@login_required
def copy_project_panel(request, project_id, panel_id=None):
    project = get_object_or_404(Project, pk=project_id)
    panel = get_object_or_404(ProjectPanel, pk=panel_id)
    if panel.project != project:
        raise PermissionDenied
    if not (project.has_add_permission(request.user)):
        raise PermissionDenied

    new_panel = panel
    new_panel.id = None
    panel_name_exists = True
    new_panel_name = new_panel.panel_name
    while panel_name_exists:
        new_panel_name += '[copy]'
        if not ProjectPanel.objects.filter(panel_name=new_panel_name).exists():
            new_panel.panel_name = new_panel_name
            break
    new_panel.save()

    # have to re-get the old panel by the ID
    panel = get_object_or_404(ProjectPanel, pk=panel_id)

    for param in panel.projectpanelparameter_set.all():
        # again we need to cache the IDs to re-retrieve
        param_id = param.id
        new_param = param
        new_param.id = None
        new_param.project_panel = new_panel
        new_param.save()

        # and re-get the param
        param = ProjectPanelParameter.objects.get(id=param_id)

        for marker in param.projectpanelparametermarker_set.all():
            marker.id = None
            marker.project_panel_parameter = new_param
            marker.save()

    return HttpResponseRedirect(reverse(
        'view_project_panels',
        args=(project.id,)))


@login_required
def render_sample_compensation(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)
    if not sample.has_view_permission(request.user):
        raise PermissionDenied

    return render_to_response(
        'render_sample_compensation.html',
        {
            'sample': sample
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_compensations(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user_view_sites = Site.objects.get_sites_user_can_view(
        request.user,
        project=project)

    if project.has_view_permission(request.user):
        compensations = Compensation.objects\
            .select_related()\
            .filter(site_panel__site__project=project)\
            .order_by('name')
    elif user_view_sites.count() > 0:
        compensations = Compensation.objects\
            .select_related()\
            .filter(site_panel__site__in=user_view_sites)\
            .order_by('name')
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
def add_compensation(request, project_id, compensation_id=None):
    project = get_object_or_404(Project, pk=project_id)

    if compensation_id:
        compensation = get_object_or_404(Compensation, pk=compensation_id)
        add_or_edit = 'edit'
    else:
        compensation = Compensation()
        add_or_edit = 'add'

    user_sites = Site.objects.get_sites_user_can_add(request.user, project)

    if not (project.has_add_permission(request.user) or user_sites.count() > 0):
        raise PermissionDenied

    if request.method == 'POST':
        form = CompensationForm(
            request.POST,
            instance=compensation,
            project_id=project_id,
            request=request)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(
                'project_compensations',
                args=(project_id,)))
    else:
        form = CompensationForm(
            instance=compensation,
            project_id=project_id,
            request=request)

    return render_to_response(
        'add_compensation.html',
        {
            'form': form,
            'project': project,
            'add_or_edit': add_or_edit,
            'compensation_id': compensation_id
        },
        context_instance=RequestContext(request)
    )


@login_required
def process_dashboard(request):

    workers = Worker.objects.all()
    requests = ProcessRequest.objects.filter(
        project__in=Project.objects.get_projects_user_can_view(
            request.user))

    return render_to_response(
        'process_dashboard.html',
        {
            'workers': sorted(workers, key=attrgetter('worker_name')),
            'requests': requests,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda u: u.is_superuser)
def add_worker(request):
    if request.method == 'POST':
        form = WorkerForm(request.POST)

        if form.is_valid():
            worker = form.save()

            return HttpResponseRedirect(reverse('process_dashboard'))
    else:
        form = WorkerForm()

    return render_to_response(
        'add_worker.html',
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_process_request(request, process_request_id):
    process_request = get_object_or_404(ProcessRequest, pk=process_request_id)
    sample_members = process_request.sample_collection.samplecollectionmember_set.all()

    return render_to_response(
        'view_process_request.html',
        {
            'process_request': process_request,
            'sample_members': sample_members
        },
        context_instance=RequestContext(request)
    )