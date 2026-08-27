from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


class _HtmlLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.add(element_id)
        for attribute in ("href", "src"):
            value = values.get(attribute)
            if value:
                self.links.append(value)


def _local_target(source: Path, raw_link: str) -> Path | None:
    link = raw_link.strip().strip("<>").split(maxsplit=1)[0]
    parsed = urlsplit(link)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    return (source.parent / unquote(parsed.path)).resolve()


def check_markdown(path: Path) -> list[str]:
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    for raw_link in MARKDOWN_LINK.findall(text):
        target = _local_target(path, raw_link)
        if target is not None and not target.exists():
            failures.append(f"{path}: missing target {raw_link}")
    return failures


def check_html(path: Path) -> list[str]:
    parser = _HtmlLinks()
    parser.feed(path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for link in parser.links:
        if link.startswith("#"):
            if link[1:] not in parser.ids:
                failures.append(f"{path}: missing anchor {link}")
            continue
        target = _local_target(path, link)
        if target is not None and not target.exists():
            failures.append(f"{path}: missing target {link}")
    return failures


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    markdown_files = [
        path
        for path in root.rglob("*.md")
        if not any(part.startswith(".") for part in path.relative_to(root).parts)
        and "release" not in path.relative_to(root).parts
    ]
    failures = [
        failure
        for path in markdown_files
        for failure in check_markdown(path)
    ]
    failures.extend(check_html(root / "guide" / "iphone-shortcuts.html"))

    if failures:
        print("\n".join(failures))
        return 1
    print(f"Checked {len(markdown_files)} Markdown files and the HTML guide")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
