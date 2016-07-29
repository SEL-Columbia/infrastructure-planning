class InfrastructurePlanningError(Exception):
    pass


class MissingData(InfrastructurePlanningError):
    pass


class UnsupportedFormat(InfrastructurePlanningError):
    pass
