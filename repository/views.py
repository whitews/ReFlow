from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.forms.models import inlineformset_factory

from guardian.shortcuts import assign_perm
from guardian.decorators import permission_required

from repository.models import *
from repository.forms import *
from repository.decorators import require_project_user
from repository.utils import apply_panel_to_sample


def d3_test(request):
    return render_to_response(
        'd3_test.html',
        {},
        context_instance=RequestContext(request)
    )


@login_required
def view_projects(request):

    projects = Project.objects.get_user_projects(request.user)

    return render_to_response(
        'view_projects.html',
        {
            'projects': sorted(projects, key=attrgetter('project_name')),
        },
        context_instance=RequestContext(request)
    )


@login_required
@permission_required('view_project_data', (Project, 'id', 'project_id'), return_403=True)
def view_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    can_add_project_data = request.user.has_perm('add_project_data', project)
    can_modify_project_data = request.user.has_perm('modify_project_data', project)

    return render_to_response(
        'view_project.html',
        {
            'project': project,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save()

            # Automatically add the request user to the project with all permissions...it's the polite thing to do
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
@permission_required('modify_project_data', (Project, 'id', 'project_id'), return_403=True)
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
@permission_required('view_project_data', (Project, 'id', 'project_id'), return_403=True)
def view_subjects(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    subjects = Subject.objects.filter(project=project).order_by('subject_id')

    can_add_project_data = request.user.has_perm('add_project_data', project)
    can_modify_project_data = request.user.has_perm('modify_project_data', project)

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
@require_project_user
def view_samples(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    samples = Sample.objects.filter(subject__project=project).values(
        'id',
        'subject__subject_id',
        'site__site_name',
        'visit__visit_type_name',
        'original_filename')

    spm_maps = SampleParameterMap.objects.filter(sample_id__in=[i['id'] for i in samples]).values(
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

    return render_to_response(
        'view_project_samples.html',
        {
            'project': project,
            'samples': samples,
        },
        context_instance=RequestContext(request)
    )


@login_required
@require_project_user
def view_sites(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    sites = Site.objects.select_related().filter(project=project).order_by('site_name')

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

            # Automatically grant all site permissions to the request user
            assign_perm('view_site_data', request.user, site)
            assign_perm('add_site_data', request.user, site)
            assign_perm('modify_site_data', request.user, site)
            assign_perm('manage_site_users', request.user, site)

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
@require_project_user
def view_compensations(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    compensations = Compensation.objects.select_related().filter(site__project=project).order_by('original_filename')

    return render_to_response(
        'view_project_compensations.html',
        {
            'project': project,
            'compensations': compensations,
        },
        context_instance=RequestContext(request)
    )


@login_required
@require_project_user
def view_site_compensations(request, site_id):
    site = get_object_or_404(Site, pk=site_id)

    compensations = Compensation.objects.filter(site=site).order_by('original_filename')

    return render_to_response(
        'view_site_compensations.html',  # TODO: create site compensation view
        {
            'site': site,
            'compensations': compensations,
        },
        context_instance=RequestContext(request)
    )


@login_required
@require_project_user
def add_compensation(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = CompensationForm(request.POST, request.FILES, project_id=project_id)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_compensations', args=project_id))
    else:
        form = CompensationForm(project_id=project_id)

    return render_to_response(
        'add_compensation.html',
        {
            'form': form,
            'project': project,
        },
        context_instance=RequestContext(request)
    )


@login_required
@require_project_user
def add_site_compensation(request, site_id):
    site = get_object_or_404(Subject, pk=site_id)

    if request.method == 'POST':
        compensation = Compensation(site=site)
        form = CompensationForm(request.POST, request.FILES, instance=compensation)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_site', args=site_id))
    else:
        form = CompensationForm()

    return render_to_response(
        'add_compensation.html',
        {
            'form': form,
            'project': site.project,
        },
        context_instance=RequestContext(request)
    )


@login_required
@require_project_user
def view_visit_types(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    visit_types = ProjectVisitType.objects.filter(project=project).order_by('visit_type_name')

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
def edit_visit_type(request, visit_type_id):
    visit_type = get_object_or_404(ProjectVisitType, pk=visit_type_id)

    if request.method == 'POST':
        form = ProjectVisitTypeForm(request.POST, instance=visit_type)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_visit_types', args=str(visit_type.project_id)))
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
                return HttpResponseRedirect(reverse('project_panels', args=str(panel.site.project_id)))
            else:
                json = simplejson.dumps(form.errors)
                return HttpResponseBadRequest(json, mimetype='application/json')

    #panels = Panel.objects.select_related().prefetch_related('panelparametermap_set').filter(site__project=project).order_by('site__site_name', 'panel_name')

    panels = Panel.objects.filter(site__project=project).values(
        'id',
        'panel_name',
        'panel_description',
        'site__site_name'
    )

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
        messages.warning(
            request,
            'This project has no associated sites. A panel must be associated with a specific site.')
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
        form = PanelEditForm(request.POST, instance=panel)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_panels', args=str(panel.site.project_id)))
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
@require_project_user
def remove_panel_parameter(request, panel_parameter_id):
    ppm = get_object_or_404(PanelParameterMap, pk=panel_parameter_id)
    project = ppm.panel.site.project
    ppm.delete()

    return HttpResponseRedirect(reverse('project_panels', args=str(project.id)))


@login_required
@require_project_user
def create_panel_from_sample(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)

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

                return HttpResponseRedirect(reverse('project_panels', args=str(sample.subject.project_id)))

    else:
        # need to check if the sample is associated with a site, since panels have a required site relation
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
                'This sample is not associated with a site. Associate the sample with a site first.')
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
@permission_required('view_project_data', (Project, 'id', 'project_id'), return_403=True)
def view_subject(request, project_id, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id, project_id=project_id)
    project = subject.project

    samples = Sample.objects.filter(subject=subject).values(
        'id',
        'site__site_name',
        'visit__visit_type_name',
        'original_filename')

    spm_maps = SampleParameterMap.objects.filter(sample_id__in=[i['id'] for i in samples]).values(
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
        sample['parameters'] = [i for i in spm_maps if i['sample_id']==sample['id']]

    can_add_project_data = request.user.has_perm('add_project_data', project)
    can_modify_project_data = request.user.has_perm('modify_project_data', project)

    return render_to_response(
        'view_subject.html',
        {
            'project': project,
            'subject': subject,
            'samples': samples,
            'can_add_project_data': can_add_project_data,
            'can_modify_project_data': can_modify_project_data,
        },
        context_instance=RequestContext(request)
    )


@login_required
@permission_required('add_project_data', (Project, 'id', 'project_id'), return_403=True)
def add_subject(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        subject = Subject(project=project)
        form = SubjectForm(request.POST, instance=subject)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_subjects', args=project_id))

    else:
        form = SubjectForm()

    return render_to_response(
        'add_subject.html',
        {
            'form': form,
            'project': project,
        },
        context_instance=RequestContext(request)
    )


@login_required
@permission_required('modify_project_data', (Project, 'id', 'project_id'), return_403=True)
def edit_subject(request, project_id, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id, project_id=project_id)

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_subject', args=(project_id, subject_id)))
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
def add_sample(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = SampleForm(request.POST, request.FILES, project_id=project_id)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project_samples', args=project_id))
    else:
        form = SampleForm(project_id=project_id)

    return render_to_response(
        'add_sample.html',
        {
            'form': form,
            'project': project,
        },
        context_instance=RequestContext(request)
    )


@login_required
@require_project_user
def add_subject_sample(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)

    if request.method == 'POST':
        sample = Sample(subject=subject)
        form = SampleSubjectForm(request.POST, request.FILES, instance=sample)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_subject', args=subject_id))
    else:
        form = SampleSubjectForm(project_id=subject.project_id)

    return render_to_response(
        'add_subject_sample.html',
        {
            'form': form,
            'subject': subject,
        },
        context_instance=RequestContext(request)
    )


@login_required
@require_project_user
def edit_sample(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)

    if request.method == 'POST':
        form = SampleEditForm(request.POST, request.FILES, instance=sample)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('view_subject', args=str(sample.subject_id)))
    else:
        form = SampleEditForm(instance=sample, project_id=sample.subject.project_id)

    return render_to_response(
        'edit_sample.html',
        {
            'form': form,
            'sample': sample,
        },
        context_instance=RequestContext(request)
    )


@login_required
@require_project_user
def select_panel(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)
    site_panels = Panel.objects.filter(site=sample.site)

    if request.method == 'POST':
        if 'panel' in request.POST:

            # Get the user selection
            selected_panel = get_object_or_404(Panel, pk=request.POST['panel'])

            try:
                status = apply_panel_to_sample(selected_panel, sample)
            except ValidationError as e:
                status = e.messages

            # if everything saved ok, then the status should be 0, but might be an array of errors
            if status != 0:
                if isinstance(status, list):
                    json = simplejson.dumps(status)
                    return HttpResponseBadRequest(json, mimetype='application/json')
            else:
                return HttpResponseRedirect(reverse('view_subject', args=str(sample.subject_id)))

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

    response = HttpResponse(sample.sample_file, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % sample.original_filename
    return response


@login_required
@require_project_user
def retrieve_compensation(request, compensation_id):
    compensation = get_object_or_404(Compensation, pk=compensation_id)

    response = HttpResponse(compensation.compensation_file, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % compensation.original_filename
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