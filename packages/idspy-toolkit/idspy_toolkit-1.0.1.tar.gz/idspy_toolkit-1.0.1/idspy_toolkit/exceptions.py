import logging


class IdsBaseException(Exception):
    """ An exception that also logs the msg to the given logger. """

    def __init__(self, msg: str, logger: logging.Logger = logging.getLogger()):
        logger.error(msg)
        super().__init__(msg)


class IdsDimensionError(IdsBaseException):
    pass

class IdsForbiddenValue(IdsBaseException):
    pass

class IdsEmptyEntriesError(IdsBaseException):
    pass


class IdsMissingEntriesError(IdsBaseException):
    pass


class IdsWrongFormatError(IdsBaseException):
    pass

class IdsVersionError(IdsBaseException):
    pass

class IdsNotValid(IdsBaseException):
    """ exception raised when an IDS is not considered as valid """
    pass





class IdsTypeError(IdsBaseException):
    """ exception raised when datatype is not the expected type """
    pass


class IdsRequiredMissing(IdsBaseException):
    """ exception raised when required members are equals to IMAS default values or None """

    pass
