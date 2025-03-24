class FilterException(Exception):
    pass


class QueueCreateError(Exception):
    pass


class QueueSendError(Exception):
    pass


class APIFetchQueuesError(Exception):
    pass


class RouterDuplicationError(Exception):
    pass
