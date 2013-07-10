from operator import attrgetter

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from process_manager.models import *
from process_manager.forms import *

from repository.models import Project

@login_required
def process_dashboard(request):

    processes = Process.objects.all()
    workers = Worker.objects.all()

    return render_to_response(
        'process_dashboard.html',
        {
            'processes': sorted(processes, key=attrgetter('process_name')),
            'workers': sorted(workers, key=attrgetter('worker_name')),
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
def add_process(request):
    if request.method == 'POST':
        form = ProcessForm(request.POST)

        if form.is_valid():
            process = form.save()

            return HttpResponseRedirect(reverse('view_process', args=(process.id,)))
    else:
        form = ProcessForm()

    return render_to_response(
        'add_process.html',
        {
            'form': form,
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
            process_input = form.save()

            return HttpResponseRedirect(reverse('view_process', args=(process.id,)))
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

            return HttpResponseRedirect(reverse('view_process', args=(process_input.process_id,)))
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


@login_required
def view_worker(request, worker_id):
    worker = get_object_or_404(Worker, pk=worker_id)

    return render_to_response(
        'view_worker.html',
        {
            'worker': worker,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda u: u.is_superuser)
def add_worker(request):
    if request.method == 'POST':
        form = WorkerForm(request.POST)

        if form.is_valid():
            worker = form.save()

            return HttpResponseRedirect(reverse('view_worker', args=(worker.id,)))
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
def register_process_to_worker(request, worker_id):
    worker = get_object_or_404(Worker, pk=worker_id)
    worker_process_map = WorkerProcessMap(worker_id=worker_id)

    if request.method == 'POST':
        form = RegisterProcessToWorkerForm(request.POST, instance=worker_process_map)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('view_worker', args=(worker.id,)))
    else:
        form = RegisterProcessToWorkerForm(instance=worker_process_map)

    return render_to_response(
        'register_process_to_worker.html',
        {
            'worker': worker,
            'form': form,
        },
        context_instance=RequestContext(request)
    )


@login_required
def process_requests(request):
    requests = ProcessRequest.objects.filter(
        sample_set__project__in=Project.objects.get_projects_user_can_view(request.user))

    return render_to_response(
        'view_process_requests.html',
        {
            'requests': requests,
        },
        context_instance=RequestContext(request)
    )