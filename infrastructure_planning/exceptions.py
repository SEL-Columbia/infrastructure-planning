class InfrastructurePlanningError(Exception):
    pass


class InvalidData(InfrastructurePlanningError):
    pass


class UnsupportedFormat(InfrastructurePlanningError):
    pass


class ValidationError(InfrastructurePlanningError):

    def __init__(self, argument_name, error_message):
        self.argument_name = argument_name
        self.error_message = error_message
        text = '%s.error = %s' % (argument_name, error_message)
        self.args = (text,)


class ExpectedPositive(ValidationError):

    def __init__(self, argument_name):
        super(ExpectedPositive, self).__init__(
            argument_name, 'must be greater than or equal to zero')
