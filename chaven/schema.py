from rest_framework.decorators import api_view, renderer_classes, \
    permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer


generator = SchemaGenerator(title='Chaven API')


@api_view()
@permission_classes([AllowAny])
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer, CoreJSONRenderer])
def schema_view(request):
    schema = generator.get_schema()
    return Response(schema)