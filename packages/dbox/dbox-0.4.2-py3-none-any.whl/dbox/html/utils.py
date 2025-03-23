from bs4 import NavigableString, Tag


def get_contents(tag: Tag):
    contents = []
    for c in tag.contents:
        if isinstance(c, Tag):
            contents.append(c)
        elif isinstance(c, NavigableString):
            if c.strip():
                contents.append(c)
    return contents
