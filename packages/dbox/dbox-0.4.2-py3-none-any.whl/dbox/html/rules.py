import logging
import re
from abc import ABC, abstractmethod
from textwrap import indent
from typing import Callable, List, Union

from attrs import define, field
from bs4 import BeautifulSoup, NavigableString, Tag

log = logging.getLogger(__name__)


def to_list(s: Union[str, List[str]]) -> list[str]:
    if isinstance(s, str):
        return [s]
    return s


class HtmlRule(ABC):
    @abstractmethod
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        pass


# class UnnestDivNodeRule(HtmlRule):
#     def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
#         # unwrap all div nodes if they have single child
#         for div in soup.find_all("div"):
#             if self.is_single_child(div):
#                 pass
#         return soup


class UnwrapTextNodeRule(HtmlRule):
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        # unwrap all text nodes if they have single child
        for tag in soup.find_all():
            if has_string_content_only(tag):
                new_contents = []
                for c in tag.contents:
                    if isinstance(c, Tag):
                        new_contents.append(c)
                    elif isinstance(c, NavigableString):
                        if c.strip():
                            new_contents.append(c)


class UnnestInlineNodeRule(HtmlRule):
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all():
            tag: Tag
            if has_string_content_only(tag):
                tag.unwrap()
        return soup


@define(kw_only=True)
class ClearSpacesRule(HtmlRule):
    ignore_tags: list[str] = ["pre", "code"]

    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all():
            tag: Tag
            if tag.name in self.ignore_tags:
                continue
            if has_string_content_only(tag):
                text = get_text(tag)
                tag.string = re.sub(r"\s+", " ", text, flags=re.MULTILINE)
            else:
                for c in tag.contents:
                    if isinstance(c, NavigableString):
                        c.replace_with(re.sub(r"\s+", " ", c.string, flags=re.MULTILINE))
        return soup


@define(kw_only=True)
class AnchorToTextRule(HtmlRule):
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all("a"):
            tag: Tag
            href = tag.get("href")
            link_text = tag.get_text().strip()
            new_text = f"[{link_text}]"
            if href:
                new_text += f"({href})"
            tag.replace_with(new_text)
        return soup


@define(kw_only=True)
class ListToTextRule(HtmlRule):
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all(["ul", "ol"]):
            tag: Tag
            new_text = ""
            no_complex_li = True
            for li in tag.find_all("li"):
                if has_string_content_only(li):
                    li_text = get_text(li)
                    new_text += "--- " + li_text + "\n"
                else:
                    no_complex_li = False
                    break
            if no_complex_li:
                ntag = soup.new_tag("pre")
                ntag.string = "\n" + new_text
                tag.replace_with(ntag)
        return soup


@define(kw_only=True)
class RemoveNodeRule(HtmlRule):
    select: List[str] = field(converter=to_list)

    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        for select in self.select:
            for tag in soup.select(select):
                tag.decompose()
        return soup


@define(kw_only=True)
class InlineToTextRule(HtmlRule):
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all(
            [
                "strong",
            ]
        ):
            tag: Tag
            text = get_text(tag)
            tag.replace_with("**" + text + "**")
        return soup


@define(kw_only=True)
class IngoreInlineRule(HtmlRule):
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all(["strong", "b", "em", "small", "mark", "del", "ins", "sub", "sup", "nobr"]):
            tag: Tag
            text = get_text(tag).strip()
            if tag.name in ("strong", "b"):
                text = "**" + text + "**"
            elif tag.name == "em":
                text = "*" + text + "*"
            else:
                pass  # TODO
            tag.replace_with(text.strip())
        return soup


@define(kw_only=True)
class SmoothRule(HtmlRule):
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        soup.smooth()
        return soup


@define(kw_only=True)
class BreadCumRule(HtmlRule):
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        ul = soup.select_one("ul.devsite-breadcrumb-list")
        if ul:
            text = "Current Location: "
            li = ul.find_all("li", recursive=False)
            for item in li:
                text += item.get_text() + " / "
            text = re.compile(r"[\s/]+$").sub("", text)
            if ul.parent.name == "div":
                p = soup.new_tag("p")
                p.string = text
                ul.parent.replace_with(p)
            else:
                ul.replace_with(text)
        return soup


@define(kw_only=True)
class MergeConsicutivePNodeRule(HtmlRule):
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        parents = set()
        for tag in soup.find_all("p"):
            tag: Tag
            parents.add(tag.parent)
        for parent in parents:
            parent: Tag
            to_be_merged = extract_consecutive_elements(
                parent.contents,
                lambda x: isinstance(x, NavigableString) or (isinstance(x, Tag) and x.name == "p"),
            )
            for items in to_be_merged:
                if len(items) <= 1:
                    continue
                new_contents = []
                new_p = soup.new_tag("p")
                for idx, item in enumerate(items):
                    if isinstance(item, NavigableString) and item.strip():
                        new_contents.append(item)
                    elif isinstance(item, Tag):
                        new_contents.extend(item.contents)
                    if idx == 0:
                        item.replace_with(new_p)
                    if isinstance(item, Tag):
                        # item.decompose()
                        item.extract()
                    elif isinstance(item, NavigableString):
                        item.extract()
                # assert all([e is not None for e in new_contents])
                new_p.extend(new_contents)

        return soup


class SimplifyLiItemsRule(HtmlRule):
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all("li"):
            tag: Tag
            if has_single_child_tag(tag):
                for c in tag.contents:
                    if isinstance(c, Tag) and c.name == "p":
                        c.unwrap()
        return soup


@define(kw_only=True)
class BQDocContentRule(HtmlRule):
    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        article = soup.select_one('body > section > section > main[role="main"] > devsite-content > article')
        assert article, "Main content not found"
        soup.body.clear()
        soup.body.append(article)

        # remove what's next
        h2 = soup.select_one('h2[data-text="What\'s next"]')
        if h2:
            for e in list(h2.next_siblings):
                if isinstance(e, Tag):
                    e.decompose()
                elif isinstance(e, NavigableString):
                    e.extract()
            # h2.decompose()
        return soup


@define(kw_only=True)
class SimpleTableToTextRule(HtmlRule):
    def is_basic_table(self, table: Tag) -> bool:
        for cell in table.find_all(["td", "th"]):
            # Check if the cell contains only text
            for child in cell.children:
                if isinstance(child, Tag):
                    return False
        return True

    def apply(self, soup: BeautifulSoup) -> BeautifulSoup:
        tables = soup.find_all("table")

        for table in tables:
            table: Tag
            if not self.is_basic_table(table):
                continue

            rows = table.find_all("tr")
            table_data = []

            for row in rows:
                cells = row.find_all(["th", "td"])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                table_data.append(cell_texts)

            # Convert table data to a readable text format
            max_lengths = [max(len(str(item)) for item in col) for col in zip(*table_data, strict=False)]
            formatted_rows = []

            for row in table_data:
                formatted_row = " ||| ".join(f"{item:<{max_lengths[i]}}" for i, item in enumerate(row))
                formatted_rows.append(formatted_row)

            table_text = "\n".join(formatted_rows)
            pre_tag = soup.new_tag("pre")
            pre_tag.string = "\n" + table_text + "\n"
            table.replace_with(pre_tag)

        return soup


def has_single_child(tag: Tag) -> bool:
    cnt = 0
    for c in tag.contents:
        if isinstance(c, NavigableString):
            if c.strip():
                cnt += 1
        elif isinstance(c, Tag):
            cnt += 1
    return cnt <= 1


def has_single_child_tag(tag: Tag) -> bool:
    cnt = 0
    for c in tag.contents:
        if isinstance(c, Tag):
            cnt += 1
    return cnt <= 1


def has_string_content_only(tag: Tag) -> bool:
    for c in tag.contents:
        if isinstance(c, Tag):
            return False
    return True


def get_text(tag: Tag) -> str:
    s = ""
    for c in tag.contents:
        if isinstance(c, NavigableString):
            s += c
        elif isinstance(c, Tag):
            raise ValueError("Tag found in text node")
    return s


def make_ident(s: str, level: int = 1) -> str:
    return indent(s, " " * 4 * level)


def extract_consecutive_elements(items: List, predicate: Callable[..., bool]):
    consecutive = []
    for item in items:
        if predicate(item):
            consecutive.append(item)
        else:
            if consecutive:
                yield consecutive
                consecutive = []
            else:
                continue
    if consecutive:
        yield consecutive


# def test_extract_consecutive_elements():
#     items = [1, 2, 4, 6, 3, 4, 5, 6, 7, 8, 9]
#     result = list(extract_consecutive_elements(items, lambda x: x % 2 == 0))
#     assert result == [[2, 4, 6], [4], [6], [8]]
