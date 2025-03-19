import sys
from abc import abstractmethod, ABC


class LogSink(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def log_message(self, message, **kwargs):
        pass

    @abstractmethod
    def log_exception(self, e, **kwargs):
        pass


class ConsoleLogSink(LogSink):
    def __init__(self):
        super().__init__()

    def log_message(self, message, **kwargs):
        is_error = kwargs.pop('error', False)
        if is_error:
            print(message, file=sys.stderr, **kwargs)
        else:
            print(message, **kwargs)

    def log_exception(self, e, **kwargs):
        # In this context, we're running from a script,
        # so might as well just raise instead of handling gracefully
        raise e
