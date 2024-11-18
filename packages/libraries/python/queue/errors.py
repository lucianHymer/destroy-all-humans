class QueueError(Exception):
    """Base class for Queue exceptions"""

    pass


class QueueConnectionError(QueueError):
    """Raised when there's an error connecting to the queue backend"""

    pass


class QueueSerializationError(QueueError):
    """Raised when there's an error serializing/deserializing queue data"""

    pass


class QueueUnexpectedError(QueueError):
    """Raised when an unexpected error occurs"""

    pass
