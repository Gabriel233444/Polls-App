from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode as uid_encoder
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
import unicodedata
from django.contrib.sites.models import Site

current_site = Site.objects.get_current()

UserModel = get_user_model()


class ArkUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = UserModel
        fields = ('email',)


class ArkUserChangeForm(UserChangeForm):
    class Meta:
        model = UserModel
        fields = ('email',)


def encoder(value):
    value = uid_encoder(force_bytes(value))
    return value


def _unicode_ci_compare(s1, s2):
    """
    Perform case-insensitive comparison of two identifiers, using the
    recommended algorithm from Unicode Technical Report 36, section
    2.11.2(B)(2).
    """
    return unicodedata.normalize('NFKC', s1).casefold() == unicodedata.normalize('NFKC', s2).casefold()


class PasswordResetForm:

    def __init__(self, email):
        self.email = email

    def send_mail(self, context):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        user_data = UserModel.objects.get(email=self.email)
        email_plaintext_message = "{}change_password/{}/{}".format(settings.URL_FRONT,
                                                                   encoder(
                                                                       user_data.id),
                                                                   context['token'])

        user_d = UserModel.objects.get(email=self.email)
        link = email_plaintext_message

        c = dict(
            user=user_d,
            link=link,
            website=settings.URL_FRONT,
            site_name=current_site.domain
        )
        html_message = render_to_string('account/email/password_reset_email.html', c)
        plain_message = strip_tags(html_message)

        subject, from_email, to = '[{domain}] Password Reset for {title}'.format(domain=current_site.domain,
                                                                                 title="Ark"), \
                                  'noreply@somehost.local', UserModel.objects.get(email=self.email).email

        msg = EmailMultiAlternatives(subject, plain_message, from_email, [to])

        msg.attach_alternative(html_message, "text/html")
        msg.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(**{
            '%s__iexact' % email_field_name: email,
            'is_active': True,
        })
        return (
            u for u in active_users
            if u.has_usable_password() and
               _unicode_ci_compare(email, getattr(u, email_field_name))
        )

    def save(self, use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.email
        for user in self.get_users(email):
            context = {
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            self.send_mail(context)
