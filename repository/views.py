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

import re

def d3_test(request):
    return render_to_response(
        'd3_test.html',
        {},
        context_instance=RequestContext(request)
    )

@login_required
def view_projects(request):

    projects = ProjectUserMap.objects.get_user_projects(request.user)

    return render_to_response(
        'view_projects.html',
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
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

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
@require_project_user
def view_subjects(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    subjects = Subject.objects.filter(site__project=project)

    return render_to_response(
        'view_project_subjects.html',
        {
            'project': project,
            'subjects': subjects,
        },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def view_sites(request, project_id):
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
def edit_site(request, site_id):
    site = get_object_or_404(Site, pk=site_id)

    if request.method == 'POST':
        form = SiteForm(request.POST, instance=site)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_sites', args=str(site.project.id)))
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
@require_project_user
def view_visit_types(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    visit_types = ProjectVisitType.objects.filter(project=project)

    return render_to_response(
        'view_project_visit_types.html',
        {
            'project': project,
            'visit_types': visit_types,
        },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def add_visit_type(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

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
@require_project_user
def view_project_panels(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        if 'panel' in request.POST:

            panel = get_object_or_404(Panel, pk=request.POST['panel'])
            ppm = PanelParameterMap(panel=panel)
            form = PanelParameterMapForm(request.POST, instance=ppm)

            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('project_panels', args=str(panel.site.project.id)))
            else:
                json = simplejson.dumps(form.errors)
                return HttpResponseBadRequest(json, mimetype='application/json')

    panels = Panel.objects.filter(site__project=project)

    # for adding new parameters to panels
    form = PanelParameterMapForm()

    return render_to_response(
        'view_project_panels.html',
        {
            'project': project,
            'panels': panels,
            'form': form,
        },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def add_panel(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # need to check if the project has any sites, since panels have a required site relation
    if request.method == 'POST' and project.site_set.exists():
        form = PanelForm(request.POST, project_id=project_id)

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
            return HttpResponseRedirect(reverse('project_panels', args=str(panel.site.project.id)))
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
def remove_panel_parameter(request, panel_parameter_id):
    ppm = get_object_or_404(PanelParameterMap, pk=panel_parameter_id)
    project = ppm.panel.site.project
    ppm.delete()

    return HttpResponseRedirect(reverse('project_panels', args=str(project.id)))

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
        form = SubjectForm(request.POST, project_id=project_id)

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
        form = SampleForm(project_id=subject.site.project.id)

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
def select_panel(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)
    site_panels = Panel.objects.filter(site=sample.subject.site)
    errors = []
    sample_param_count = 0
    sample_parameters = {} # parameter_number: PnN text

    if request.method == 'POST':
        if 'panel' in request.POST:

            # Get the user selection
            selected_panel = get_object_or_404(Panel, pk=request.POST['panel'])

            # Validate that it is a site panel
            if selected_panel in site_panels:

                # Read the FCS text segment and get the number of parameters
                sample_text_segment = sample.get_fcs_text_segment()

                if 'par' in sample_text_segment:
                    if sample_text_segment['par'].isdigit():
                        sample_param_count = int(sample_text_segment['par'])
                    else:
                        errors.append("Sample reports non-numeric parameter count")
                else:
                    errors.append("No parameters found in sample")

                # Get our parameter numbers from all the PnN matches
                for key in sample_text_segment:
                    matches = re.search('^P(\d)N$', key, flags=re.IGNORECASE)
                    if matches:
                        # while we're here, verify sample parameter PnN text matches a parameter in selected panel
                        if selected_panel.panelparametermap_set.filter(fcs_text=sample_text_segment[key]):
                            sample_parameters[matches.group(1)] = sample_text_segment[key]
                        else:
                            errors.append("Sample parameter " + sample_text_segment[key] + " does not match a parameter in selected panel")

                # Verify:
                # sample parameter count == sample_param_count == selected panel parameter counts
                if len(sample_parameters) == sample_param_count == len(selected_panel.panelparametermap_set.all()):

                    # Copy all the parameters from PanelParameterMap to SampleParameterMap
                    for key in sample_parameters:
                        ppm = selected_panel.panelparametermap_set.get(fcs_text=sample_parameters[key])

                        # Finally, construct and save our sample parameter map for all the matching parameters
                        spm = SampleParameterMap()
                        spm.sample = sample
                        spm.parameter = ppm.parameter
                        spm.value_type = ppm.value_type
                        spm.fcs_number = key
                        spm.fcs_text = sample_parameters[key]
                        spm.save()
                else:
                    errors.append("Matching parameter counts differ between sample and selected panel")

            # If something isn't right, return errors back to user
            if len(errors) > 0:
                json = simplejson.dumps(errors)
                return HttpResponseBadRequest(json, mimetype='application/json')
            else:
                return HttpResponseRedirect(reverse('view_subject', args=str(sample.subject.id)))

    return render_to_response(
        'select_panel.html',
        {
            'sample': sample,
            'site_panels': site_panels,
        },
        context_instance=RequestContext(request)
    )

@login_required
@require_project_user
def retrieve_sample(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)
    sample_filename = sample.sample_file.name.split('/')[-1]
    
    response = HttpResponse(sample.sample_file, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % sample.original_filename
    return response

@login_required
@require_project_user
def sample_data(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)

    return HttpResponse(sample.get_fcs_data(), content_type='text/csv')

@login_required
@require_project_user
def view_sample_scatterplot(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)

    return render_to_response(
        'view_sample_scatterplot.html',
        {
            'sample': sample,
            },
        context_instance=RequestContext(request)
    )