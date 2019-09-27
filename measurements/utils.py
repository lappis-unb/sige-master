from django.utils.translation import gettext as _
from .exceptions import *

fields = ['serial_number', 'start_date', 'end_date']
messages = {
    'serial_number': _('It must to have a serial_number argument'),
    'start_date': _('It must to have a start_date argument'),
    'end_date': _('It must to have a end_date argument')
}

def validate_query_params(params):
    error_messages = []
    for attribute in params:
        if attribute['name'] in fields and not attribute['value']:
            error_messages.append(
                {attribute['name']: messages[attribute['name']]}
            )

    if error_messages != []:
        raise MeasurementsParamsException({'errors': error_messages})
