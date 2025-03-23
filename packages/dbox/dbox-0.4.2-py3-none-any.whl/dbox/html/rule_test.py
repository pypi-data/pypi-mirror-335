# import logging
# from pathlib import Path

# from bs4 import BeautifulSoup

# import luna.html.rule as rl

# log = logging.getLogger(__name__)


# def test_unnest(test_data_dir: Path, root_dir: Path):
#     html = (test_data_dir / "0.html").read_text()
#     html = Path(root_dir / "bigquery/docs/loading-data-cloud-storage-parquet.html").read_text()
#     soup = BeautifulSoup(html, "lxml")
#     rules = [
#         rl.RemoveNodeRule(
#             select=[
#                 "devsite-header",
#                 "devsite-book-nav",
#                 "devsite-footer-linkboxes",
#                 "devsite-feature-tooltip",
#                 "devsite-footer-utility",
#                 "devsite-content-footer",
#                 "devsite-feedback",
#                 "div > template",
#             ]
#         ),
#         rl.RemoveAllAttributesRule(ignore_attrs="(href|data-text|data-github-includecode-link|language|role)"),
#         rl.ClearSpacesRule(),
#         rl.IngoreInlineRule(),
#         rl.AnchorToTextRule(),
#         rl.ListToTextRule(),
#         rl.SimpleTableToTextRule(),
#         rl.MergeConsicutivePNodeRule(),
#         rl.RemoveEmptyNodeRule(),
#         rl.SimplifyLiItemsRule(),
#         rl.MergeConsicutivePNodeRule(),
#         rl.RemoveEmptyNodeRule(),
#         rl.BQDocContentRule(),
#         rl.RemoveAttributesRule(attrs="data-text|data-github-includecode-link"),
#         rl.ClearSpacesRule(),
#         rl.SmoothRule(),
#     ]
#     # rule = UnnestInlineNodeRule()
#     # soup = rule

#     # .apply(soup.body)
#     # ListToTextRule()

#     for rule in rules:
#         soup = rule.apply(soup)

#     with open(test_data_dir / "x.html", "w") as f:
#         # f.write(str(soup))
#         f.write(soup.prettify().replace("–", "-"))

#         pug = html_to_pug(soup)
#         with open(test_data_dir / "x.pug", "w") as f:
#             f.write(pug)
#     # with open(test_data_dir / "x.md", "w") as f:
#     #     f.write(markdownify(str(soup), heading_style="ATX"))


# def convert_to_pug(soup, indent=0):
#     pug_lines = []
#     indent_str = "  " * indent

#     if isinstance(soup, str):
#         pug_lines.append(indent_str + soup.strip())
#         return pug_lines

#     if soup.name:
#         tag_line = indent_str + soup.name
#         if soup.attrs:
#             attrs = []
#             for key, value in soup.attrs.items():
#                 if isinstance(value, list):
#                     value = " ".join(value)
#                 attrs.append(f'{key}="{value}"')
#             tag_line += "(" + " ".join(attrs) + ")"
#         pug_lines.append(tag_line)

#     if soup.contents:
#         for content in soup.contents:
#             if isinstance(content, str) and content.strip():
#                 pug_lines[-1] += " " + content.strip()
#             else:
#                 pug_lines.extend(convert_to_pug(content, indent + 1))

#     return pug_lines


# def html_to_pug(soup: BeautifulSoup):
#     pug_lines = convert_to_pug(soup)
#     return "\n".join(list(pug_lines))
