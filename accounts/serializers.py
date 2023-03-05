from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
# Django framework Imports
from rest_framework.authtoken.models import Token
from rest_framework import serializers
# Rest Auth Imports
from rest_auth.serializers import LoginSerializer
# Account Imports
from .forms import PasswordResetForm
# Django Imports
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Group
from django.utils.http import urlsafe_base64_decode as uid_decoder
# Audit Imports
from polls.models import Audit

UserModel = get_user_model()
role = ['admin', 'Owner', 'Reader']
group = Group
token_model = Token
audit_model = Audit


class ArkUserDetailSerializer(serializers.ModelSerializer):
    """ Serializer for Get User detail Endpoint """

    class Meta:
        model = UserModel
        exclude = ['password', 'user_permissions', 'is_superuser', 'first_name', 'last_name', 'last_login']


class AuditDetailSerializer(serializers.ModelSerializer):
    """ Serializer for Audit serializer """

    class Meta:
        model = UserModel
        fields = ['id', 'name', 'email', 'phone_number']


class ArkAdminUpdateUserSerializer(serializers.ModelSerializer):
    """ Serializer for Admin Update user Endpoint """

    class Meta:
        model = UserModel
        fields = "__all__"
        extra_kwargs = {'name': {'required': True}, 'phone_number': {'required': True}, 'password': {'required': False},
                        'role': {'required': True}, 'email': {'required': False}}

    def update(self, request, pk):
        user = request.user
        try:
            get_group = group.objects.get(name=request.data['role'])
        except group.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid Role name"})
        if user.role != role[0] and request.data.get('role') == role[0]:
            raise serializers.ValidationError({"detail": "You do not have the permission to update role to admin."})
        else:
            update = UserModel.objects.filter(id=pk).update(updated_by=user, updated_at=timezone.now(),
                                                            groups=get_group.id, **request.data)
            updated_user = UserModel.objects.get(id=pk)
            audit_model.objects.create(
                subject="update user", user=updated_user, created_by=user, audit_type="user",
                description=f"{user.name} updated a user {updated_user.name}").save()
            return update


class ArkUpdateProfileSerializer(serializers.ModelSerializer):
    """ Serializer for Update Profile Endpoint """

    class Meta:
        model = UserModel
        exclude = ["password"]
        extra_kwargs = {'email': {'required': False}}

    def update(self, request, validated_data):
        user = request.user
        # user.email = validated_data.get('email', user.email)
        user.name = validated_data.get('name', user.name)
        user.phone_number = validated_data.get('phone_number', user.phone_number)
        user.store_location = validated_data.get('store_location', user.store_location)
        user.manage_subscriber_acct = validated_data.get('manage_subscriber_acct', user.manage_subscriber_acct)
        user.subscriber_role = validated_data.get('subscriber_role', user.subscriber_role)
        user.receive_threshold_alert = validated_data.get('receive_threshold_alert', user.receive_threshold_alert)
        user.receive_supply_alert = validated_data.get('receive_supply_alert', user.receive_supply_alert)
        user.receive_pickup_alert = validated_data.get('receive_pickup_alert', user.receive_pickup_alert)
        user.is_approver = validated_data.get('is_approver', user.is_approver)
        user.image = validated_data.get('image', user.image)
        user.updated_at = timezone.now()
        user.updated_by = user
        user.save()
        return user


class ArkUserDeactivateActivateSerializer(serializers.ModelSerializer):
    """ Serializer for deactivate and activating user Endpoint """

    class Meta:
        model = UserModel
        fields = ['email']


class ArkLoginSerializer(LoginSerializer):
    """ Serializer for Login user Endpoint """

    username = None


class ChangePasswordSerializer(serializers.Serializer):
    """ Serializer for change password Endpoint """

    model = UserModel

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class NewUserChangePasswordSerializer(serializers.Serializer):
    """ Serializer for new user change password Endpoint """

    model = UserModel

    """
    Serializer for new user change password endpoint.
    """
    new_password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)


class ResendEmailSerializer(serializers.Serializer):
    """ Serializer for resend email Endpoint """

    email = serializers.CharField()


class CreateUserSerializer(serializers.ModelSerializer):
    """ Serializer for admin create user endpoint """

    class Meta:
        model = UserModel
        fields = "__all__"
        extra_kwargs = {'name': {'required': True}, 'phone_number': {'required': True}, 'role': {'required': True},
                        'password': {'required': False}}

    def save(self, request):
        check_token = request.user
        created_by = UserModel.objects.get(id=check_token.id)
        try:
            group.objects.get(name=request.data['role'])
        except group.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid Role name"})
        adapter = get_adapter()
        user = adapter.new_user(request)
        user.name = request.data['name']
        self.cleaned_data = {'email': request.data['email'], 'password': "Ark@123456"}
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user.save()
        token_model.objects.create(user=user).save()
        UserModel.objects.filter(pk=user.id).update(
            groups=group.objects.get(name=request.data['role']), password=make_password("Ark@123456"),
            created_by=created_by, is_staff=True, **request.data)
        audit_model.objects.create(subject="create user", user=user, created_by=created_by, audit_type="user",
                                   description=f"{created_by.name} created a user {request.data['name']}").save()
        return user


class ArkPasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    uid = serializers.CharField()
    token = serializers.CharField()

    set_password_form_class = SetPasswordForm

    def custom_validation(self, attrs):
        pass

    def validate(self, attrs):
        self._errors = {}

        # Decode the uidb64 to uid to get User object
        try:
            uid = force_str(uid_decoder(attrs['uid']))
            self.user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError({'uid': ['Invalid Token']})

        self.custom_validation(attrs)
        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': ['Invalid Token']})

        return attrs

    def save(self):
        return self.set_password_form.save()


class ArkPasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    email = serializers.EmailField()

    def validate_email(self, email):
        # Create PasswordResetForm with the serializer
        if not UserModel.objects.filter(email=email).exists():
            raise serializers.ValidationError(_('Invalid e-mail address'))

        self.reset_form = PasswordResetForm(email)

        return email

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }
        self.reset_form.save(**opts)
