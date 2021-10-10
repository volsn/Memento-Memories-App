from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Memory
from memories.serializers import TagSerializer

TAGS_URL = reverse('memories:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@mail.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Spot Idea')
        Tag.objects.create(user=self.user, name='Plan')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='other@mail.com',
            password='testpass'
        )
        Tag.objects.create(user=user2, name='Spot Idea')
        tag = Tag.objects.create(user=self.user, name='Roadmap')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'New Tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_memory(self):
        """Test filtering tags by those assigned to memories"""
        tag1 = Tag.objects.create(user=self.user, name='Spot Idea')
        tag2 = Tag.objects.create(user=self.user, name='Plan')
        memory = Memory.objects.create(
            title='People excellence for new project',
            user=self.user
        )
        memory.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'in_use': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name='Spot Idea')
        Tag.objects.create(user=self.user, name='Plan')
        memory1 = Memory.objects.create(
            title='Call Sam',
            user=self.user
        )
        memory1.tags.add(tag)
        memory2 = Memory.objects.create(
            title='Call Mike',
            user=self.user
        )
        memory2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'in_use': 1})

        self.assertEqual(len(res.data), 1)
