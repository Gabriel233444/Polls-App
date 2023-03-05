from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PasswordValidator:
    """
    Validate whether the password contains minimum one uppercase, one digit and one symbol.
    """

    def __init__(self, min_length=1):
        self.min_length = min_length

    def validate(self, password, user=None):
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _('Password must contain at least %(min_length)d digit.') % {'min_length': self.min_length})
        if not any(char.isalpha() for char in password):
            raise ValidationError(
                _('Password must contain at least %(min_length)d letter.') % {'min_length': self.min_length})
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _('Password must contain at least %(min_length)d uppercase letter.') % {'min_length': self.min_length})
        if not any(char in special_characters for char in password):
            raise ValidationError(
                _('Password must contain at least %(min_length)d special character.') % {'min_length': self.min_length})

    def get_help_text(self):
        return _("Your password must contain at least 1 number, 1 uppercase and 1 non-alphanumeric character.")