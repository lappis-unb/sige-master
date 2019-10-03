from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException

fields = ['serial_number', 'start_date', 'end_date']
messages = {
    'serial_number': _('It must have a serial_number argument'),
    'start_date': _('It must have a start_date argument'),
    'end_date': _('It must have an end_date argument')
}

def validate_query_params(params):
    error_messages = {}
    for attribute in params:
        if attribute['name'] in fields and not attribute['value']:
            error_messages[attribute['name']] = messages[attribute['name']]

    if error_messages != {}:
        raise APIException(error_messages)
