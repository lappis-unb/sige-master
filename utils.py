from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    r'^\(\d{2,}\) \d{4,}\-\d{4}$',
    'Invalid phone format'
)

web_site_validator = RegexValidator(
    r'^(https?:\/\/)?(www\.)?([a-zA-Z0-9]+'
    '(-?[a-zA-Z0-9])*\.)+[\w]{2,}(\/\S*)?$',
    'Invalid website format'
)


class ValidationException(Exception):
    def __init__(self, message):
        super(ValidationException, self).__init__(message)
        self.message = message
