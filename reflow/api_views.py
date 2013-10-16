from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response


@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """

    return Response({
        'repository_api': reverse('repository-api-root', request=request),
        'api_token_auth': reverse('api-token-auth', request=request),
        'api_docs': reverse('api-docs', request=request),
    })