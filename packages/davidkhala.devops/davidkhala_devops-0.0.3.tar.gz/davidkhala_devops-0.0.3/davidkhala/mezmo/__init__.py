# https://github.com/logdna/python/blob/master/README.md
import logging
import os
from logging import LogRecord as NativeLogRecord
from time import sleep

from davidkhala.syntax.log import AbstractIngestion
from logdna import LogDNAHandler


class LogRecord(NativeLogRecord):
    def __init__(self, source, level, app, lineno, msg, args, exc_info, **kwargs):
        super().__init__(source, level, app, lineno, msg, args, exc_info, **kwargs)


class Ingestion(AbstractIngestion):
    timeout = 3
    handler: LogDNAHandler
    flag: str

    def __init__(self, api_key: str = None, **options):
        if api_key is None:
            api_key = os.environ['LOGDNA_INGESTION_KEY']
        options['log_error_response'] = True
        super().__init__(LogDNAHandler(api_key, options))

    def connect(self):
        self.flag = 'pending'
        raise_error = not self.handler.log_error_response
        expected_error_msg = 'Please provide a valid ingestion key. Discarding flush buffer'

        class OnInvalidKey(logging.Handler):
            def __init__(self, i: Ingestion):
                super().__init__()
                self.i = i

            def emit(self, record):
                if record.levelno == logging.DEBUG and record.msg == expected_error_msg:
                    self.i.flag = 'failed'
                elif self.i.flag == 'pending':
                    self.i.flag = 'success'

        handler = OnInvalidKey(self)
        self.handler.internalLogger.addHandler(handler)
        self.handler.emit(LogRecord(
            source=self.handler.internalLogger.name,
            level=logging.DEBUG,
            app='api.logs',
            lineno=0,
            msg='connected',
            args=(),
            exc_info=None,
        ))
        ticktock = 0
        while self.flag == 'pending':
            sleep(1)
            ticktock += 1
            if ticktock > Ingestion.timeout:
                break
        self.handler.internalLogger.removeHandler(handler)
        if self.flag == 'failed':
            if raise_error:
                raise Exception(expected_error_msg)
            else:
                return False
        return True
