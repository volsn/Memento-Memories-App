import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Memory, Tag, Domain
from memories.serializers import MemorySerializer, MemoryDetailSerializer

MEMORIES_URL = reverse('memories:memory-list')


def image_upload_url(memory_id):
    """Return URL for memories image upload"""
    return reverse('memories:memory-upload-image', args=(memory_id,))


def detail_url(memory_id):
    """Return memories detail URL"""
    return reverse('memories:memory-detail', args=(memory_id,))


def sample_tag(user, name='Spot Idea'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_domain(user, name='Life'):
    """Create and return a sample domain"""
    return Domain.objects.create(user=user, name=name)


def sample_memory(user, **params):
    """Create and return a sample memories"""
    defaults = {
        'title': 'Sample memories',
        'text': 'Sample text'
    }
    defaults.update(params)

    return Memory.objects.create(user=user, **defaults)


class PublicMemoryApiTests(TestCase):
    """Test public memories API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that authentication is required"""
        res = self.client.get(MEMORIES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMemoryApiTests(TestCase):
    """Test private memories API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@mail.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_memories(self):
        """Test retrieving a list of memories"""
        _ = sample_memory(user=self.user)
        _ = sample_memory(user=self.user)

        res = self.client.get(MEMORIES_URL)
        memories = Memory.objects.all().order_by('-id')
        serializer = MemorySerializer(memories, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_memory_detail(self):
        """Test viewing a memories detail"""
        memory = sample_memory(user=self.user)
        memory.tags.add(sample_tag(user=self.user))
        memory.domains.add(sample_domain(user=self.user))

        url = detail_url(memory.id)
        res = self.client.get(url)

        serializer = MemoryDetailSerializer(memory)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_memory(self):
        """Test updating a memories with patch"""
        memory = sample_memory(user=self.user, title='Call Mark')
        memory.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Spot Idea')

        payload = {'title': 'Call Sam', 'tags': [new_tag.id]}
        url = detail_url(memory.id)
        self.client.patch(url, payload)

        memory.refresh_from_db()
        self.assertEqual(memory.title, payload['title'])
        tags = memory.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)


class MemoryImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@mail.com',
            password='testpass'
        )
        self.client.force_authenticate(self.user)
        self.memory = sample_memory(self.user)

    def tearDown(self):
        self.memory.image.delete()

    def test_upload_image_to_memory(self):
        """Test uploading an image to memories"""
        url = image_upload_url(self.memory.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.memory.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.memory.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.memory.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_memories_by_tags(self):
        """Test returning memories with specific tags"""
        memory1 = sample_memory(user=self.user, title='Call Mark')
        memory2 = sample_memory(user=self.user, title='Call Sam')
        tag1 = sample_tag(user=self.user, name='Life')
        tag2 = sample_tag(user=self.user, name='Work')
        memory1.tags.add(tag1)
        memory2.tags.add(tag2)
        memory3 = sample_memory(user=self.user,
                                title='Get ready for People Excellence')

        res = self.client.get(
            MEMORIES_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = MemorySerializer(memory1)
        serializer2 = MemorySerializer(memory2)
        serializer3 = MemorySerializer(memory3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
