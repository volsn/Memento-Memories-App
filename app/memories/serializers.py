from rest_framework import serializers

from core.models import Tag, Domain, Memory


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class DomainSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""

    class Meta:
        model = Domain
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class MemorySerializer(serializers.ModelSerializer):
    """Serializer for memories objects"""
    domains = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Domain.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Memory
        fields = ('id', 'title', 'text',
                  'domains', 'tags', 'image',)
        read_only_fields = ('id',)


class MemoryDetailSerializer(MemorySerializer):
    """Serialize a memories detail"""
    domains = DomainSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class MemoryImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to memories"""

    class Meta:
        model = Memory
        fields = ('id', 'image',)
        read_only_fields = ('id',)
