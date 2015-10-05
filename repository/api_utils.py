from rest_framework import status
from rest_framework.authentication import \
    SessionAuthentication, \
    TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated

from django.views.generic.detail import SingleObjectMixin
from django.core.exceptions import PermissionDenied

from repository import models


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    if isinstance(exc, NotAuthenticated):
        response = Response(
            {'detail': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED,
            exception=True
        )
    else:
        response = exception_handler(exc, context)

    return response


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def repository_api_root(request):
    """
    The entry endpoint of our API.
    """

    return Response({
        'compensations': reverse('compensation-list', request=request),
        'panel-templates': reverse('panel-template-list', request=request),
        'panel-variants': reverse('panel-variant-list', request=request),
        'site-panels': reverse('site-panel-list', request=request),
        'markers': reverse('marker-list', request=request),
        'fluorochromes': reverse('fluorochrome-list', request=request),
        'specimens': reverse('specimen-list', request=request),
        'permissions': reverse('permission-list', request=request),
        'users': reverse('user-list', request=request),
        'projects': reverse('project-list', request=request),
        'cell_subset_labels': reverse(
            'cell-subset-label-list',
            request=request
        ),
        'create_samples': reverse('create-sample', request=request),
        'samples': reverse('sample-list', request=request),
        'sample_metadata': reverse('sample-metadata-list', request=request),
        'sample_collections': reverse(
            'sample-collection-list', request=request),
        'sample_collection_members': reverse(
            'sample-collection-member-list', request=request),
        'sites': reverse('site-list', request=request),
        'subject_groups': reverse('subject-group-list', request=request),
        'subjects': reverse('subject-list', request=request),
        'visit_types': reverse('visit-type-list', request=request),
        'stimulations': reverse('stimulation-list', request=request),
        'workers': reverse('worker-list', request=request),
        'subprocess_categories': reverse(
            'subprocess-category-list', request=request),
        'subprocess_implementations': reverse(
            'subprocess-implementation-list', request=request),
        'subprocess_inputs': reverse('subprocess-input-list', request=request),
        'process_requests': reverse('process-request-list', request=request),
        'process_request_stage2_create': reverse(
            'process-request-stage2-create',
            request=request
        ),
        'process_request_inputs': reverse(
            'process-request-input-list', request=request),
        'assigned_process_requests': reverse(
            'assigned-process-request-list', request=request),
        'viable_process_requests': reverse(
            'viable-process-request-list', request=request),
        'clusters': reverse('cluster-list', request=request),
        'cluster-labels': reverse('cluster-label-list', request=request),
        'sample_clusters': reverse('sample-cluster-list', request=request),
        'sample_cluster_components': reverse(
            'sample-cluster-component-list',
            request=request
        )
    })


class LoginRequiredMixin(object):
    """
    View mixin to verify a user is logged in.
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)


class AdminRequiredMixin(object):
    """
    View mixin to verify a user is an administrator.
    """

    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser)


class PermissionRequiredMixin(SingleObjectMixin):
    """
    View mixin to verify a user has permission to a resource.
    """

    def get_object(self, *args, **kwargs):
        # TODO: see if we can check HTTP method (GET, PUT, etc.) to reduce
        # duplicate code for modifying resources
        obj = super(PermissionRequiredMixin, self).get_object(*args, **kwargs)
        if hasattr(self, 'request'):
            request = self.request
        else:
            raise PermissionDenied

        if isinstance(obj, models.ProtectedModel):
            if isinstance(obj, models.Project):
                user_sites = models.Site.objects.get_sites_user_can_view(
                    request.user, obj)

                if not obj.has_view_permission(request.user) and not (
                        user_sites.count() > 0):
                    raise PermissionDenied
            elif not obj.has_view_permission(request.user):
                raise PermissionDenied

        return obj
