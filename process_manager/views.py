from operator import attrgetter

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from process_manager.models import *
from process_manager.forms import *


@login_required
def process_dashboard(request):

    processes = Process.objects.all()

    return render_to_response(
        'process_dashboard.html',
        {
            'processes': sorted(processes, key=attrgetter('process_name')),
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