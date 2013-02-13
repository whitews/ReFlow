from repository.models import *
from repository.serializers import *

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """

    return Response({
        'projects': reverse('project-list', request=request),
        'samples': reverse('sample-list', request=request),
    })

class ProjectList(generics.ListAPIView):
    """
    API endpoint representing a list of projects.
    """

    model = Project
    serializer_class = ProjectSerializer

class ProjectDetail(generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = Project
    serializer_class = ProjectSerializer


class SampleList(generics.ListAPIView):
    """
    API endpoint representing a list of projects.
    """

    model = Sample
    serializer_class = SampleSerializer
    filter_fields = ('subject', 'original_filename')

    def get_queryset(self):
        """
        Override .get_queryset() to filter on the SampleParameterMap property 'name'
        """

        # Value may have multiple names separated by commas
        name_value = self.request.QUERY_PARAMS.get('name', None)

        # The name property is just a concatenation of 2 related fields:
        #  - parameter__parameter_short_name
        #  - value_type__value_type_short_name (single character for H, A, W, T)
        # they are joined by a hyphen
        names = name_value.split(',')

        queryset = Sample.objects.all()

        for name in names:
            parameter = name[0:-2]
            value_type = name[-1]

            queryset = queryset.filter(
                    sampleparametermap__parameter__parameter_short_name=parameter,
                    sampleparametermap__value_type__value_type_short_name=value_type,
            ).distinct()

        return queryset

class SampleDetail(generics.RetrieveAPIView):
    """
    API endpoint representing a single project.
    """

    model = Sample
    serializer_class = SampleSerializer
