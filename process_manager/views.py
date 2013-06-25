from operator import attrgetter

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from process_manager.models import *


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
    return process_dashboard(request)