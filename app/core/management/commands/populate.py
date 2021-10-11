import random
from typing import Any

from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from core.models import Tag, Domain, Memory, User, create_default_domains

fake = Faker()


def generate_tags(user: User) -> None:
    """Generate fake tags"""
    tags = ['idea', 'plan', 'thought', 'innovation',
            'concept', 'solution', 'project']
    for name in tags:
        Tag(
            name=name,
            user=user
        ).save()


def generate_memories(user: User, num: int = 50) -> None:
    """Generate fake memories"""
    for _ in range(num):
        tags = Tag.objects.filter(
            user=user
        ).order_by('?')[:random.randint(1, 5)]
        domains = Domain.objects.filter(
            user=user
        ).order_by('?')[:random.randint(1, 2)]
        memory = Memory(
            title=fake.sentence(),
            text=fake.text(512),
            user=user
        )
        memory.save()
        memory.domains.set([domain.pk for domain in domains])
        memory.tags.set([tag.pk for tag in tags])
        memory.save()


def generate_users(num: int = 100) -> None:
    """Generate fake users"""
    for _ in range(num):
        profile = fake.profile()
        user = User(
            email=profile['mail'],
            name=profile['name'],
            password=make_password('123456')
        )
        user.save()
        generate_tags(user=user)
        create_default_domains(user=user)
        generate_memories(user=user)


class Command(BaseCommand):
    """Make it possible to populate db with manage command"""

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write('Started generating users...')
        generate_users()
        self.stdout.write(self.style.SUCCESS('Database populated!'))
