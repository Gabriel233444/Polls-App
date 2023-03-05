from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from .utils import get_random_numeric_string
import copy

current_site = Site.objects.get_current()
UserModel = get_user_model()


class DefaultAccountAdapterCustom(DefaultAccountAdapter):

    def send_mail(self, template_prefix, email, context):
        context['activate_url'] = f"{settings.URL_FRONT}verify_email/{email}/{context['key']}"
        generate_password = copy.copy(f'Ark@{get_random_numeric_string(6)}')
        update_user_password = UserModel.objects.get(email=email)
        update_user_password.set_password(generate_password)
        update_user_password.save()
        context['password'] = generate_password
        msg = self.render_mail(template_prefix, email, context)
        msg.send()