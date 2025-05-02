from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Display, Template
from .serializers import DisplaySerializer, TemplateSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_display(request):
    serializer = DisplaySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_display(request, pk):
    try:
        display = Display.objects.get(pk=pk)
    except Display.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = DisplaySerializer(display, data=request.data, partial=True)
    if serializer.is_valid():
        print(serializer.validated_data)
        print(request.data)

        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_display(request, pk):
    try:
        display = Display.objects.get(pk=pk)
    except Display.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = DisplaySerializer(display)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_displays_for_project(request, project_id):
    displays = Display.objects.filter(
        project_id=project_id).order_by('-modified')
    serializer = DisplaySerializer(displays, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_template(request, pk):
    try:
        template = Template.objects.get(pk=pk)
    except Template.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TemplateSerializer(template)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_templates_by_type(request, template_type):
    templates = Template.objects.filter(type=template_type)
    serializer = TemplateSerializer(templates, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_templates(request):
    templates = Template.objects.all()
    serializer = TemplateSerializer(templates, many=True)
    return Response(serializer.data)
