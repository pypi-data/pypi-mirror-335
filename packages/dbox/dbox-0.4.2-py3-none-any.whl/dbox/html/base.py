import logging
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


class HtmlRule(ABC):
    @abstractmethod
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        pass
