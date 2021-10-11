import os
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.utils.timezone import make_aware
from django.utils.translation import gettext as _
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.db.models.query import QuerySet


def image_upload_file_path(_, filename) -> str:
    """Generate file path for new memory image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads', 'memories', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs) -> 'User':
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password) -> 'User':
        """Creates and saves a new superuser"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    memory_expiration = models.DurationField(default=timedelta(weeks=1))

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Domain(models.Model):
    """Domain to be used in a memory"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('domain')
        verbose_name_plural = _('domains')


class Tag(models.Model):
    """Tags to be used in a memory"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')


class MemoryManager(models.Manager):
    """Override model manager for memory class"""

    def get_queryset(self) -> QuerySet:
        """Only return memories that have not expired"""
        return super(MemoryManager, self).get_queryset() \
            .filter(expiration__gte=datetime.now())

    def delete_expired_objects(self) -> None:
        """Method to remove memories that have expired"""
        super(MemoryManager, self).get_queryset() \
            .filter(expiration__lte=datetime.now()).delete()


class Memory(models.Model):
    """Recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    text = models.TextField(blank=True)
    expiration = models.DateTimeField(editable=False)
    domains = models.ManyToManyField('Domain')
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(
        null=True,
        upload_to=image_upload_file_path
    )

    objects = MemoryManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs) -> None:
        """Override save method to add expiration datetime to object"""
        self.expiration = make_aware(datetime.now()) + self.user. \
            memory_expiration
        super(Memory, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('memory')
        verbose_name_plural = _('memories')
