from operator import attrgetter

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.forms.models import inlineformset_factory

from process_manager.models import *
from process_manager.forms import *

from repository.models import Project


@login_required
def process_dashboard(request):

    processes = Process.objects.all()
    workers = Worker.objects.all()
    requests = ProcessRequest.objects.filter(
        sample_set__project__in=Project.objects.get_projects_user_can_view(
            request.user))

    return render_to_response(
        'process_dashboard.html',
        {
            'processes': sorted(processes, key=attrgetter('process_name')),
            'workers': sorted(workers, key=attrgetter('worker_name')),
            'requests': requests,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_process(request, process_id):
    process = get_object_or_404(Process, pk=process_id)

    return render_to_response(
        'view_process.html',
        {
            'process': process,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda u: u.is_superuser)
def add_process_input(request, process_id):
    process = get_object_or_404(Process, pk=process_id)

    if request.method == 'POST':
        process_input = ProcessInput(process=process)
        form = ProcessInputForm(request.POST, instance=process_input)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse(
                'view_process',
                args=(process.id,)))
    else:
        form = ProcessInputForm()

    return render_to_response(
        'add_process_input.html',
        {
            'process': process,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda u: u.is_superuser)
def edit_process_input(request, process_input_id):
    process_input = get_object_or_404(ProcessInput, pk=process_input_id)

    if request.method == 'POST':
        form = ProcessInputForm(request.POST, instance=process_input)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse(
                'view_process',
                args=(process_input.process_id,)))
    else:
        form = ProcessInputForm(instance=process_input)

    return render_to_response(
        'edit_process_input.html',
        {
            'process_input': process_input,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda u: u.is_superuser)
def add_worker(request):
    if request.method == 'POST':
        form = WorkerForm(request.POST)

        if form.is_valid():
            worker = form.save()

            return HttpResponseRedirect(reverse(
                'view_worker',
                args=(worker.id,)))
    else:
        form = WorkerForm()

    return render_to_response(
        'add_worker.html',
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda u: u.is_superuser)
def create_process_request(request, process_id):
    process = get_object_or_404(Process, pk=process_id)
    process_request = ProcessRequest(
        process=process,
        request_user=request.user)

    PRInputValueFormSet = inlineformset_factory(
        ProcessRequest,
        ProcessRequestInputValue,
        form=ProcessRequestInputValueForm,
        extra=process.processinput_set.count(),
        can_delete=False,
    )

    if request.method == 'POST':
        form = ProcessRequestForm(request.POST, instance=process_request)

        if form.is_valid():
            valid_request = form.save(commit=False)
            formset = PRInputValueFormSet(request.POST, instance=valid_request)

            if formset.is_valid():
                valid_request.save()
                formset.save()

                return HttpResponseRedirect(reverse('process_dashboard'))
        else:
            formset = PRInputValueFormSet(
                request.POST,
                instance=process_request)
    else:
        form = ProcessRequestForm(instance=process_request)

        initial_data = list()

        for process_input in process.processinput_set.all():
            # note that 'value_label' is
            # used for the 'value' field's label
            initial_data.append(
                {
                    'process_input': process_input,
                    'value_label': process_input.input_name
                })

        formset = PRInputValueFormSet(
            instance=process_request,
            initial=initial_data)

    return render_to_response(
        'create_process_request.html',
        {
            'process': process,
            'form': form,
            'formset': formset,
        },
        context_instance=RequestContext(request)
    )


@login_required
def view_process_request(request, process_request_id):
    process_request = get_object_or_404(ProcessRequest, pk=process_request_id)

    return render_to_response(
        'view_process_request.html',
        {
            'process_request': process_request,
        },
        context_instance=RequestContext(request)
    )