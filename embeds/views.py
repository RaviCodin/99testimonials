from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import EmbedCategory, EmbedTemplate, EmbedInstance
from .serializers import EmbedCategorySerializer, EmbedTemplateSerializer, EmbedInstanceSerializer, EmbedInstanceViewSerializer
from projects.models import Project


class EmbedTemplateListView(APIView):
    def get(self, request, *args, **kwargs):
        categories = EmbedCategory.objects.all().order_by('order')
        result = []
        for category in categories:
            templates = EmbedTemplate.objects.filter(category=category)
            serializer = EmbedTemplateSerializer(templates, many=True)
            result.append({
                'category': EmbedCategorySerializer(category).data,
                'templates': serializer.data
            })
        return Response(result)


class EmbedInstanceListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EmbedInstanceViewSerializer
        return EmbedInstanceSerializer

    def get_queryset(self):
        project_id = self.kwargs['projectid']
        return EmbedInstance.objects.filter(project__id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs['projectid']
        project = Project.objects.get(id=project_id)
        print(project)
        serializer.save(project=project)


class EmbedInstanceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmbedInstance.objects.all()
    serializer_class = EmbedInstanceSerializer


class EmbedInstanceDetailView(generics.RetrieveAPIView):
    queryset = EmbedInstance.objects.all()
    serializer_class = EmbedInstanceViewSerializer
    lookup_field = 'pk'
