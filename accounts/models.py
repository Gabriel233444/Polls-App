from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.utils import image_resize
from pollme import settings
from accounts.managers import PollMeUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import Group


class PollMeUser(AbstractUser):

    SUBSCRIBER_ROLE = (
        ('admin', 'admin'),
        ('staff', 'staff'),
        ('customer', 'customer'),
    )

    username = None
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=200, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = PollMeUserManager()
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    groups = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    store_location = models.CharField(max_length=50, null=True, blank=True)
    manage_subscriber_acct = models.BooleanField(default=False)
    subscriber_role = models.CharField(max_length=50, choices=SUBSCRIBER_ROLE, null=True, blank=True)
    receive_threshold_alert = models.BooleanField(default=False)
    receive_supply_alert = models.BooleanField(default=False)
    receive_pickup_alert = models.BooleanField(default=False)
    is_approver = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    password_updated = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='uploads/profile', blank=True, null=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   related_name='created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   related_name='updated')

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        try:
            image_resize(self.image, 1024, 1024)
        except Exception as e:
            pass
        super().save(*args, **kwargs)
