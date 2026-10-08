import markdown


def to_html(text: str) -> str:
    return markdown.markdown(text)


def strip_markdown(text: str) -> str:
    html = markdown.markdown(text)
    return html.removeprefix("<p>").removesuffix("</p>\n")
