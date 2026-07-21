from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    def normalize_email(self, email):
        return super().normalize_email(email).lower() if email else email

    def create_user(self, username, email=None, password=None, **extra_fields):
        email = self.normalize_email(email)
        return super().create_user(username, email=email, password=password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        email = self.normalize_email(email)
        extra_fields.setdefault('is_email_verified', True)
        return super().create_superuser(username, email=email, password=password, **extra_fields)


class UserStatus(models.Model):
    DEFAULT_NAMES = (_('Вільний'), _('Зайнятий'), _('Free'), _('Busy'))

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='statuses')
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at', 'id')
        verbose_name = _('User Status')
        verbose_name_plural = _('User Statuses')
        constraints = (
            models.UniqueConstraint(fields=('user', 'name'), name='unique_user_status_name'),
        )

    def clean(self):
        super().clean()
        self.name = self.name.strip() if self.name else self.name
        if not self.name:
            raise ValidationError({'name': _('Status name cannot be empty.')})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Friend(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        ACCEPTED = 'accepted', _('Accepted')
        REJECTED = 'rejected', _('Rejected')

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='friends')
    friend = models.ForeignKey('User', on_delete=models.CASCADE, related_name='friend_of')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Friend')
        verbose_name_plural = _('Friends')
        constraints = (
            models.UniqueConstraint(fields=('user', 'friend'), name='unique_friendship'),
            models.CheckConstraint(
                check=~models.Q(user=models.F('friend')),
                name='no_self_friendship',
            ),
        )

    def __str__(self):
        return f'{self.user.username} -> {self.friend.username} ({self.status})'


class User(AbstractUser):
    class AuthProvider(models.TextChoices):
        LOCAL = 'local', _('Local')
        GOOGLE = 'google', _('Google')

    username_validator = RegexValidator(
        regex=r'^[A-Za-z0-9_.-]{3,30}$',
        message=_('Username must be 3-30 characters and contain only letters, numbers, dots, hyphens, and underscores.'),
    )

    username = models.CharField(max_length=30, unique=True, validators=[username_validator], verbose_name=_('Username'))
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    first_name = models.CharField(max_length=150, blank=True, verbose_name=_('First name'))
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_('Avatar'))
    is_email_verified = models.BooleanField(default=False, verbose_name=_('Email verified'))
    auth_provider = models.CharField(
        max_length=32,
        choices=AuthProvider.choices,
        default=AuthProvider.LOCAL,
        verbose_name=_('Auth provider'),
    )
    current_status = models.ForeignKey(
        UserStatus,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='current_for_users',
        verbose_name=_('Current status'),
    )
    hexagons_explored = models.PositiveIntegerField(default=0, verbose_name=_('Hexagons explored'))
    checkpoints_visited = models.PositiveIntegerField(default=0, verbose_name=_('Checkpoints visited'))

    objects = CustomUserManager()

    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        if self.email:
            self.email = type(self).objects.normalize_email(self.email)
        if self.auth_provider == self.AuthProvider.GOOGLE:
            self.is_email_verified = True
        if self.current_status_id and self.pk:
            if not UserStatus.objects.filter(pk=self.current_status_id, user_id=self.pk).exists():
                raise ValidationError({'current_status': _('Current status must belong to this user.')})
        super().save(*args, **kwargs)
