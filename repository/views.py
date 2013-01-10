from repository.models import *
from repository.forms import *
from repository.decorators import require_project_user

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from operator import attrgetter

def d3_test(request):
    return render_to_response(
        'd3_test.html',
        {},
        context_instance=RequestContext(request)
    )

@login_required
def projects(request):

    projects = ProjectUserMap.objects.get_user_projects(request.user)

    return render_to_response(
        'projects.html',
        {
            'projects': sorted(projects, key=attrgetter('project_name')),
        },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def view_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    subjects = Subject.objects.filter(site__project=project)

    return render_to_response(
        'view_project.html',
        {
            'project': project,
            'subjects': sorted(subjects, key=attrgetter('subject_id')), 
        },
        context_instance=RequestContext(request)
    )

@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save()

            # Automatically add the request user to the project...it's the polite thing to do
            ProjectUserMap(project=project, user=request.user).save()

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
@require_project_user
def view_project_sites(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    sites = Site.objects.filter(project=project)

    return render_to_response(
        'view_project_sites.html',
        {
            'project': project,
            'sites': sites,
        },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def add_site(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

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
@require_project_user
def view_project_panels(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    panels = Panel.objects.filter(site__project=project)

    return render_to_response(
        'view_project_panels.html',
        {
            'project': project,
            'panels': panels,
        },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def add_panel(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # need to check if the project has any sites, since panels have a required site relation
    if request.method == 'POST' and project.site_set.exists():
        panel = Panel()
        form = PanelForm(request.POST, instance=panel)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_panels', args=project_id))

    elif not project.site_set.exists():
        messages.warning(request, 'This project has no associated sites. A panel must be associated with a specific site.')
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
@require_project_user
def edit_panel(request, panel_id):
    panel = get_object_or_404(Panel, pk=panel_id)

    if request.method == 'POST':
        form = PanelForm(request.POST, instance=panel)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_panel', args=panel_id))
    else:
        form = PanelForm(instance=panel)

    return render_to_response(
        'edit_panel.html',
        {
            'form': form,
            'panel': panel,
            },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def add_panel_parameter(request, panel_id):
    panel = get_object_or_404(Panel, pk=panel_id)

    if request.method == 'POST':
        ppm = PanelParameterMap(panel=panel)
        form = PanelParameterMapForm(request.POST, instance=ppm)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_panels', args=str(panel.site.project.id)))
        else:
            json = simplejson.dumps(form.errors)
            return HttpResponseBadRequest(json, mimetype='application/json')
    else:
        form = PanelParameterMapForm(instance=panel)

    return render_to_response(
        'add_panel_parameter.html',
        {
            'form': form,
            'panel': panel,
        },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def view_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)

    samples = Sample.objects.filter(subject=subject)

    return render_to_response(
        'view_subject.html',
        {
            'project': subject.site.project,
            'subject': subject,
            'samples': samples, 
        },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def add_subject(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # need to check if the project has any sites, since patients have a required site relation
    if request.method == 'POST' and project.site_set.exists():
        subject = Subject()
        form = SubjectForm(request.POST, instance=subject)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_project', args=project_id))

    elif not project.site_set.exists():
        messages.warning(request, 'This project has no associated sites. A subject must be associated with a specific site.')
        return HttpResponseRedirect(reverse('warning_page',))

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
@require_project_user
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_subject', args=subject_id))
    else:
        form = SubjectForm(instance=subject)

    return render_to_response(
        'edit_subject.html',
        {
            'form': form,
            'subject': subject,
        },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def add_sample(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)

    if request.method == 'POST':
        sample = Sample(subject=subject)
        form = SampleForm(request.POST, request.FILES, instance=sample)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_subject', args=subject_id))
    else:
        form = SampleForm()

    return render_to_response(
        'add_sample.html',
        {
            'form': form,
            'subject': subject,
        },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def retrieve_sample(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)
    sample_filename = sample.sample_file.name.split('/')[-1]
    
    response = HttpResponse(sample.sample_file, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % sample_filename
    return response