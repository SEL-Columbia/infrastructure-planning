class InfrastructurePlanningError(Exception):
    pass


class InvalidData(InfrastructurePlanningError):
    pass


class UnsupportedFormat(InfrastructurePlanningError):
    pass
