from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.forms import ArkUserChangeForm, ArkUserCreationForm
from accounts.models import PollMeUser


# Register your models here.


class ArkUserAdmin(UserAdmin):
    add_form = ArkUserCreationForm
    form = ArkUserChangeForm
    model = PollMeUser
    filter_horizontal = ('user_permissions',)
    list_display = ('email', 'id', 'is_staff', 'is_active', 'role',)
    list_filter = ('email', 'is_staff', 'is_active', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        ('Profile', {'fields': ('name', 'phone_number', 'email_verified', 'password_updated',
                                'role',)}),
        ('Activity History', {'fields': ('date_joined',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active',)}
         ),
    )

    search_fields = ('email', 'name', 'role',)
    ordering = ('email',)
    list_per_page = 50


admin.site.register(PollMeUser, ArkUserAdmin)

# Customize Admin Portal Name
admin.site.site_header = "POLL administration"
admin.site.site_title = "POLL Admin Portal"
admin.site.index_title = "Welcome to POLL Server Administration Portal"

# Register your models here.
