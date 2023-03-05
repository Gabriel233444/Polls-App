from builtins import super
# Django Allauth Imports #
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC, EmailAddress
from allauth.account.signals import email_confirmed
from allauth.account.utils import send_email_confirmation
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.account.adapter import get_adapter
# Django Imports #
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.http import HttpResponse
# Rest-Auth Imports #
from rest_auth.registration.views import RegisterView, SocialLoginView
from rest_auth.views import LoginView
from rest_auth.registration.serializers import VerifyEmailSerializer
# Django rest-framework Imports
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, APIView
from rest_framework.exceptions import APIException
from rest_framework.generics import (
    RetrieveUpdateAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
# Account Imports
from .permission import IdentityIsVerified
from .serializers import ChangePasswordSerializer, ArkUserDeactivateActivateSerializer, \
    ArkUserDetailSerializer, NewUserChangePasswordSerializer, \
    ResendEmailSerializer, ArkAdminUpdateUserSerializer, CreateUserSerializer, ArkPasswordResetSerializer, \
    ArkUpdateProfileSerializer, ArkPasswordResetConfirmSerializer
from .utils import return_msg
# Roles Imports
from polls.permission import permission_required
from django.contrib.auth.models import Group
# Audit Imports
from polls.models import Poll

# Create your views here.
UserModel = get_user_model()
poll_model = Poll
role = ['admin', 'owner', 'reader']
group_model = Group


class NoPaginationView(PageNumberPagination):
    page_size = None


@api_view()
def django_rest_auth_null():
    return Response(status=status.HTTP_400_BAD_REQUEST)


@receiver(email_confirmed)
def email_confirmed_(request, email_address, **kwargs):
    user = email_address.user
    user.email_verified = True

    user.save()


# request a new confirmation email
class ResendEmailConfirmation(APIView):
    """ Resend E-mail Confirmation Endpoint """
    permission_classes = [AllowAny]
    serializer_class = ResendEmailSerializer

    def post(self, request):

        try:
            user = UserModel.objects.get(email=request.data['email'])
            email_address = EmailAddress.objects.filter(user=user, verified=True).exists()
            if email_address:
                return Response({'message': 'This email is already verified'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                send_email_confirmation(request, user=user)
                return Response({'message': 'Verification email resent'},
                                status=status.HTTP_201_CREATED)
        except APIException:
            return Response({'message': 'This email does not exist, please create a new account'},
                            status=status.HTTP_403_FORBIDDEN)


class VerifyEmailView(APIView):
    """ Verify/Confirm E-mail Endpoint """

    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')

    def get_serializer(self, *args, **kwargs):
        return VerifyEmailSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs['key'] = serializer.validated_data['key']
        try:
            confirmation = self.get_object()
            confirmation.confirm(self.request)
            return Response({'detail': _('Successfully confirmed email.')},
                            status=status.HTTP_200_OK)
        except EmailConfirmation.DoesNotExist:
            return Response({'detail': _('Invalid Token.')},
                            status=status.HTTP_404_NOT_FOUND)

    def get_object(self, queryset=None):
        key = self.kwargs['key']
        email_confirmation = EmailConfirmationHMAC.from_key(key)
        if not email_confirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                email_confirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                raise EmailConfirmation.DoesNotExist
        return email_confirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs


class UserLoginView(LoginView):
    """ Login Endpoint """

    def get_response(self):
        response = super().get_response()
        if self.user.password_updated:
            data = {"message": "Welcome {}".format(self.user), "code": response.status_code,
                    "role": self.user.role, "user_id": self.user.id, "password_updated": self.user.password_updated}
            response.data.update(data)
            return response
        else:
            return Response({"password_updated": False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    authentication_classes = [TokenAuthentication]
    serializer_class = ChangePasswordSerializer
    model = UserModel
    permission_classes = (IsAuthenticated, IdentityIsVerified,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            try:
                get_adapter().clean_password(serializer.data.get("new_password"))
                # set_password also hashes the password that the user will get
                self.object.set_password(serializer.data.get("new_password"))
                self.object.save()
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully',
                    'data': []
                }
                return Response(response)
            except Exception as e:
                return Response({"detail": e}, status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewUserUpdatePassword(UpdateAPIView):
    """ New User Update Password Endpoint """

    serializer_class = NewUserChangePasswordSerializer
    queryset = UserModel.objects.all()

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            get_adapter().clean_password(serializer.data.get("new_password"))
            user = UserModel.objects.get(email=serializer.data.get("email"))
            user.set_password(serializer.data.get("new_password"))
            user.password_updated = True
            user.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            return Response(response)
        except Exception as e:
            response = {"detail": e}
            return Response(response, status=status.HTTP_403_FORBIDDEN)


class DeactivateUserView(RetrieveUpdateAPIView):
    """
        An endpoint for deactivating a user.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, IdentityIsVerified,
                          permission_required('accounts.change_polluser'),)
    serializer_class = ArkUserDeactivateActivateSerializer
    queryset = UserModel.objects.all()

    def get_object(self):
        return get_object_or_404(UserModel, id=self.kwargs['pk'])

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        created_by = self.request.user
        if instance.is_superuser:
            return Response({"detail": "Cannot deactivate this user."},
                            status=status.HTTP_401_UNAUTHORIZED)
        else:
            instance.is_active = False
            instance.save()
            poll_model.objects.create(
                f"{created_by.name}deactivate a user with the name {instance.name}").save()
            return Response({"message": "User successfully deactivated."})


class ActivateUserView(RetrieveUpdateAPIView):
    """
    An endpoint for activating a user.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, IdentityIsVerified,
                          permission_required('accounts.change_polluser'),)
    serializer_class = ArkUserDeactivateActivateSerializer
    queryset = UserModel.objects.all()

    def get_object(self):
        return get_object_or_404(UserModel, id=self.kwargs['pk'])

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        created_by = self.request.user
        instance.is_active = True
        instance.save()
        poll_model.objects.create(
                f"{created_by.name}deactivate a user with the name {instance.name}").save()
        response = {"message": "User successfully activated."}
        return Response(response)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class ArkUserListView(ListAPIView):
    """ List All Users Endpoint """

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, IdentityIsVerified, permission_required('accounts.polluser'),)
    queryset = UserModel.objects.all()
    serializer_class = ArkUserDetailSerializer
    pagination_class = NoPaginationView


class ArkUserProfileView(APIView):
    """ Get User Profile Endpoint """

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = ArkUserDetailSerializer

    def get(self, request):
        queryset = UserModel.objects.get(pk=self.request.user.id)
        data = self.serializer_class(queryset)
        return Response(return_msg('00', 'profile', data.data))


class ArkUpdateProfileView(APIView):
    """ Endpoint for Update Profile """

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, IdentityIsVerified,)
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]
    queryset = UserModel.objects.all()
    serializer_class = ArkUpdateProfileSerializer
    serializer_class2 = ArkUserDetailSerializer

    def put(self, request):
        user = self.request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.serializer_class.update(self, request, request.data)
        data = self.serializer_class2(UserModel.objects.get(id=user.id))
        return Response(data.data)


class ArkUserDetailView(RetrieveAPIView):
    """ Admin Get User Detail Endpoint """

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, IdentityIsVerified, permission_required('accounts.view_polluser'),)
    queryset = UserModel.objects.all()
    serializer_class = ArkUserDetailSerializer


class ArkAdminUpdateUserView(APIView):
    """ Admin Create User Endpoint"""

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, IdentityIsVerified, permission_required('accounts.change_polluser'),)
    serializer_class = ArkAdminUpdateUserSerializer
    serializer_class2 = ArkUserDetailSerializer

    def put(self, request, pk):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.serializer_class.update(self, request, pk)
            data = self.serializer_class2(UserModel.objects.get(id=pk))
            return Response(return_msg('00', 'Profile updated successfully', data.data))
        except UserModel.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


class CreateUserView(RegisterView):
    """ Create User Endpoint """

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, IdentityIsVerified,
                          permission_required('accounts.add_user'),)
    serializer_class = CreateUserSerializer
    serializer_class2 = ArkUserDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = self.perform_create(serializer)
        data = self.serializer_class2(UserModel.objects.get(id=new_user.id))
        return Response(data.data)


# class ArkUploadImageView(RegisterView):
#     """ Upload User Image Endpoint """
#
#     authentication_classes = [TokenAuthentication]
#     permission_classes = (IsAuthenticated, IdentityIsVerified,)
#     parser_classes = [MultiPartParser, FormParser, FileUploadParser]
#     serializer_class = CreateUserSerializer
#     serializer_class2 = ArkUserDetailSerializer
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         new_user = self.perform_create(serializer)
#         data = self.serializer_class2(UserModel.objects.get(id=new_user.id))
#         return Response(data.data)


class ArkPasswordResetView(GenericAPIView):
    """
    Calls Django Auth PasswordResetForm save method.
    Accepts the following POST parameters: email
    Returns the success/fail message.
    """

    serializer_class = ArkPasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        # Return the success message with OK HTTP status
        return Response(
            {"success": "Password reset e-mail has been sent."},
            status=status.HTTP_200_OK
        )


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)


class ArkPasswordResetConfirmView(GenericAPIView):
    """
    Password reset e-mail link is confirmed, therefore
    this resets the user's password.

    Accepts the following POST parameters: token, uid,
        new_password1, new_password2
    Returns the success/fail message.
    """
    serializer_class = ArkPasswordResetConfirmSerializer
    permission_classes = (AllowAny,)

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(ArkPasswordResetConfirmView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("Password has been reset with the new password.")}
        )


class ArkStatView(APIView):
    """ Ark Statistics Endpoint """

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

# class EmailResetView(GenericAPIView):
#     """
#     Calls Django Auth PasswordResetForm save method.
#     Accepts the following POST parameters: email
#     Returns the success/fail message.
#     """
#     authentication_classes = [TokenAuthentication]
#     permission_classes = (IsAuthenticated, IdentityIsVerified,)
#     serializer_class = ArkChangeEmailSerializer
#
#     def post(self, request, *args, **kwargs):
#         # Create a serializer with request.data
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         serializer.save()
#         # Return the success message with OK HTTP status
#         return Response(
#             {"success": "E-mail reset has been sent."},
#             status=status.HTTP_200_OK
#         )


# sensitive_post_parameters_m = method_decorator(
#     sensitive_post_parameters(
#         'email', 'old_email', 'new_email1', 'new_email2'
#     )
# )


# class EmailResetConfirmView(GenericAPIView):
#     """
#     Email reset e-mail link is confirmed, therefore
#     this resets the user's email.
#
#     Accepts the following POST parameters: token, uid,
#         new_email1, new_email2
#     Returns the success/fail message.
#     """
#     authentication_classes = [TokenAuthentication]
#     permission_classes = (IsAuthenticated, IdentityIsVerified,)
#     serializer_class = EmailResetConfirmSerializer
#
#     @sensitive_post_parameters_m
#     def dispatch(self, *args, **kwargs):
#         return super(EmailResetConfirmView, self).dispatch(*args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(
#             {"detail": _("Email has been reset with the new email.")}
#         )


def index(request):
    return HttpResponse("Welcome to PollMe Server API Page")
