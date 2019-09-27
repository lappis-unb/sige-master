from rest_framework.exceptions import APIException

class MeasurementsParamsException(APIException):
    status_code = 400

    def __init__(self, message):
        super(MeasurementsParamsException, self).__init__(message)
        self.message = message
