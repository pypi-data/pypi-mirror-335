import logging
import re

from attrs import define, field
from bs4 import BeautifulSoup, Tag

from .base import HtmlRule
from .utils import get_contents

log = logging.getLogger(__name__)


@define(kw_only=True)
class RemoveAllAttributesRule(HtmlRule):
    ignore_attrs: re.Pattern = field(converter=re.compile)

    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all():
            tag: Tag
            for attr in list(tag.attrs.keys()):
                if self.ignore_attrs.match(attr):
                    continue
                else:
                    del tag[attr]
        return soup


@define(kw_only=True)
class RemoveAttributesRule(HtmlRule):
    attrs: re.Pattern = field(converter=re.compile)

    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all():
            tag: Tag
            for attr in list(tag.attrs.keys()):
                if self.attrs.match(attr):
                    del tag[attr]
        return soup


@define(kw_only=True)
class RemoveEmptyNodeRule(HtmlRule):
    tags: list[str] = ["p", "div", "span"]

    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all():
            tag: Tag
            if not get_contents(tag):
                log.debug("Removing tag %s", tag.name)
                tag.decompose()
        return soup
