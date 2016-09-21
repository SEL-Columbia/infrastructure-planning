class InfrastructurePlanningError(Exception):
    pass


class InvalidData(InfrastructurePlanningError):
    pass


class ExpectedPositive(InvalidData):
    pass


class UnsupportedFormat(InfrastructurePlanningError):
    pass
