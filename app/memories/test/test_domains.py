from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Domain, Memory
from memories.serializers import DomainSerializer

DOMAINS_URL = reverse('memories:domain-list')


class PublicDomainsApiTests(TestCase):
    """Test the publicly available domains API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving domains"""
        res = self.client.get(DOMAINS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDomainsApiTests(TestCase):
    """Test the authorized user domains API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@mail.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_domains(self):
        """Test retrieving domains"""
        Domain.objects.create(user=self.user, name='Work')
        Domain.objects.create(user=self.user, name='Life')

        res = self.client.get(DOMAINS_URL)

        domains = Domain.objects.all().order_by('-name')
        serializer = DomainSerializer(domains, many=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_domains_limited_to_user(self):
        """Test that domains returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='other@mail.com',
            password='testpass'
        )
        Domain.objects.create(user=user2, name='Friendship')
        domain = Domain.objects.create(user=self.user, name='Work')

        res = self.client.get(DOMAINS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], domain.name)

    def test_create_domain_successful(self):
        """Test creating a new domain"""
        payload = {'name': 'New Domain'}
        self.client.post(DOMAINS_URL, payload)

        exists = Domain.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_domain_invalid(self):
        """Test creating a new domain with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(DOMAINS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_domains_assigned_to_memory(self):
        """Test filtering domains by those assigned to memories"""
        domain1 = Domain.objects.create(user=self.user, name='Work')
        domain2 = Domain.objects.create(user=self.user, name='Life')
        memory = Memory.objects.create(
            title='People excellence for new project',
            user=self.user
        )
        memory.domains.add(domain1)

        res = self.client.get(DOMAINS_URL, {'in_use': 1})

        serializer1 = DomainSerializer(domain1)
        serializer2 = DomainSerializer(domain2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_domains_assigned_unique(self):
        """Test filtering domains by assigned returns unique items"""
        domain = Domain.objects.create(user=self.user, name='Work')
        Domain.objects.create(user=self.user, name='Life')
        memory1 = Memory.objects.create(
            title='Call Sam',
            user=self.user
        )
        memory1.domains.add(domain)
        memory2 = Memory.objects.create(
            title='Call Mike',
            user=self.user
        )
        memory2.domains.add(domain)

        res = self.client.get(DOMAINS_URL, {'in_use': 1})

        self.assertEqual(len(res.data), 1)
