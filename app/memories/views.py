from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Domain, Memory
from memories import serializers


class BaseViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                  mixins.CreateModelMixin):
    """Base viewset for user owned memories attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(memory__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class DomainViewSet(BaseViewSet):
    """Manage domains in the database"""
    queryset = Domain.objects.all()
    serializer_class = serializers.DomainSerializer


class MemoryViewSet(viewsets.ModelViewSet):
    """Manage memorys in the database"""
    serializer_class = serializers.MemorySerializer
    queryset = Memory.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def _query_to_list(params):
        """Convert a list of string IDs to a list of integers"""
        return [int(param) for param in params.split(',')]

    def get_queryset(self):
        """Limit objects to the authenticated user"""
        queryset = self.queryset

        tags = self.request.query_params.get('tags')
        if tags:
            tag_ids = self._query_to_list(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        domains = self.request.query_params.get('domains')
        if domains:
            domains_ids = self._query_to_list(domains)
            queryset = queryset.filter(domains__id__in=domains_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.MemoryDetailSerializer
        elif self.action == 'upload_image':
            return serializers.MemoryImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new memories"""
        serializer.save(user=self.request.user)

    @action(methods=('POST',), detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """upload an image to a memory"""
        memory = self.get_object()
        serializer = self.get_serializer(
            memory,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
