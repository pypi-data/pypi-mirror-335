# https://betterstack.com/docs/logs/python/#logging-from-python
import logging

from davidkhala.syntax.log import AbstractIngestion
from logtail import LogtailHandler


class Ingestion(AbstractIngestion):

    def __init__(self, token: str, host: str):
        """
        :param token:
        :param host: Ingestion host is scoped to each BetterStack Source. With or without host are both accepted
        """
        assert host.endswith('.betterstackdata.com')
        super().__init__(LogtailHandler(
            source_token=token,
            host=host,
            raise_exceptions=True
        ))
