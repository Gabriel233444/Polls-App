from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode as uid_encoder
from django_rest_passwordreset.signals import reset_password_token_created


def encoder(value):
    value = uid_encoder(force_bytes(value))
    return value


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # email_plaintext_message = "{}confirm/{}/{}".format(reverse('password_reset:reset-password-request'),
    #                                             encoder(reset_password_token.user.pk),
    #                                             reset_password_token.key)

    email_plaintext_message = "{}change_password/{}/{}".format(settings.URL_FRONT,
                                                               encoder(
                                                                   reset_password_token.user.pk),
                                                               reset_password_token.key)

    # print("Password Reset Confirm Email", email_plaintext_message)

    first_name = reset_password_token.user.first_name
    link = email_plaintext_message

    c = dict(
        first_name=first_name,
        link=link,
        website=settings.URL_FRONT,
        site_name="ARK"
    )
    html_message = render_to_string('account/email/password_reset_email.html', c)
    plain_message = strip_tags(html_message)

    subject, from_email, to = 'Password Reset for {title}'.format(title="Ark"), \
                              'noreply@somehost.local', reset_password_token.user.email

    msg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
    msg.attach_alternative(html_message, "text/html")
    msg.send()
