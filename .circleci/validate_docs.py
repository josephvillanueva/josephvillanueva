"""Validate tracked Markdown, relative file links, and YAML without remote requests."""
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from markdown_it import MarkdownIt


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


class HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src") and value:
                self.targets.append(value)


def validate(root):
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=root
    ).decode().split("\0")
    errors = []
    counts = {"Markdown": 0, "YAML": 0, "local links": 0}
    parser = MarkdownIt("commonmark")
    for name in filter(None, tracked):
        path = root / name
        if path.suffix.lower() not in (".md", ".yml", ".yaml"):
            continue
        try:
            content = path.read_text(encoding="utf-8")
            if re.search(r"^(<<<<<<< |=======\s*$|>>>>>>> )", content, re.M):
                raise ValueError("unresolved merge conflict marker")
            if path.suffix.lower() in (".yml", ".yaml"):
                list(yaml.load_all(content, Loader=UniqueKeyLoader))
                counts["YAML"] += 1
                continue
            counts["Markdown"] += 1
            if not content.strip():
                raise ValueError("empty Markdown document")
            tokens = parser.parse(content)
            headings = [int(t.tag[1:]) for t in tokens if t.type == "heading_open"]
            for previous, current in zip(headings, headings[1:]):
                if current > previous + 1:
                    errors.append(f"{name}: heading skips from h{previous} to h{current}")
            targets = []
            for token in tokens:
                if token.type == "fence":
                    lines = content.splitlines()
                    closing = lines[token.map[1] - 1].strip()
                    if token.map[1] <= token.map[0] + 1 or not re.fullmatch(
                        re.escape(token.markup[0]) + "{" + str(len(token.markup)) + ",}", closing
                    ):
                        errors.append(f"{name}: unclosed fenced code block")
                for child in token.children or []:
                    if child.type in ("link_open", "image"):
                        targets.append(child.attrGet("href") or child.attrGet("src"))
                html = HTMLLinks()
                if token.type == "html_block":
                    html.feed(token.content)
                for child in token.children or []:
                    if child.type == "html_inline":
                        html.feed(child.content)
                targets.extend(html.targets)
            for target in targets:
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                counts["local links"] += 1
                relative = unquote(url.path)
                destination = (
                    root / relative.lstrip("/") if relative.startswith("/")
                    else path.parent / relative
                ).resolve()
                if root != destination and root not in destination.parents:
                    errors.append(f"{name}: local link escapes repository: {target}")
                elif not destination.exists():
                    errors.append(f"{name}: missing local target: {target}")
        except (ValueError, UnicodeError, yaml.YAMLError) as error:
            errors.append(f"{name}: {error}")
    if not counts["Markdown"]:
        errors.append("No tracked Markdown documents found")
    for error in errors:
        print(error)
    print(", ".join(f"{value} {key}" for key, value in counts.items()))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(validate(Path(__file__).resolve().parents[1]))
