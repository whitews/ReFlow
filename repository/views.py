from repository.models import *
from repository.forms import *

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from operator import attrgetter

@login_required
def projects(request):

    projects = Project.objects.all()

    return render_to_response(
        'projects.html',
        {
            'projects': sorted(projects, key=attrgetter('project_name')),
        },
        context_instance=RequestContext(request)
    )

@login_required
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
        project = Project()
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            project.save()
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
def project_panels(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    panels = Panel.objects.filter(site__project=project)

    return render_to_response(
        'project_panels.html',
        {
            'project': project,
            'panels': panels,
        },
        context_instance=RequestContext(request)
    )

@login_required
def add_panel(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        panel = Panel()
        form = PanelForm(request.POST, instance=panel)

        if form.is_valid():
            panel.save()
            return HttpResponseRedirect(reverse('project_panels', args=(project_id,)))
    else:
        form = PanelForm()

    return render_to_response(
        'add_panel.html',
        {
            'form': form,
            'project': project,
        },
        context_instance=RequestContext(request)
    )

@login_required
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
def retrieve_sample(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)
    sample_filename = sample.sample_file.name.split('/')[-1]
    
    response = HttpResponse(sample.sample_file, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % sample_filename
    return response