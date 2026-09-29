#!/usr/bin/env python3
"""Assemble media, audit folders/ZIPs and package completed folders in separate commands."""

import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import stat
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets/template"
COMPONENTS = ROOT / "assets/components"
LIMIT = 50 * 1024 * 1024
BLOCKS = {
    "playbook": ("playbook_main", "플레이북", "플레이북"),
    "scenario-canvas": ("canvas_main", "시나리오 캔버스", "시나리오캔버스"),
    "data-book": ("databook_main", "데이터북", "데이터북"),
}
IMAGES = {".svg", ".png", ".webp", ".jpg", ".jpeg", ".gif", ".avif"}
VIDEOS = {".webm", ".mp4", ".ogv"}
VOID = set("area base br col embed hr img input link meta param source track wbr".split())


def read(path):
    return path.read_bytes().decode("utf-8-sig")


def name_page(text, title):
    text = text.replace("<title>UserStory</title>", f"<title>{html.escape(title, quote=False)}</title>", 1)
    for _, label, _ in BLOCKS.values():
        text = text.replace(f'data-screen-name="가족을 위한 두 번째 차 {label}"',
                            f'data-screen-name="{html.escape(title, quote=True)} {label}"')
    return text


def markers(kind):
    if kind == "css":
        return "/* ▼ 내 디자인 붙여넣기 ▼", "/* ▲ 여기까지 ▲ */"
    if kind == "js":
        return "// ▼ 내 스크립트 붙여넣기 ▼", "// ▲ 여기까지 ▲"
    name = BLOCKS[kind][2]
    return f"<!-- ▼ {name} 코드 붙여넣기 시작 ▼ -->", f"<!-- ▲ {name} 코드 붙여넣기 끝 ▲ -->"


def insert(text, kind, content):
    begin, end = markers(kind)
    if text.count(begin) != 1 or text.count(end) != 1:
        raise ValueError(f"Missing or repeated paste markers: {kind}")
    return text.replace(end, content + "\n" + end, 1)


def remove_databook(text):
    return re.sub(r"^[ \t]*<!-- ✂ 데이터북이 없으면 여기부터 지우기 ✂ -->.*?"
                  r"<!-- ✂ 데이터북이 없으면 여기까지 지우기 ✂ -->[^\S\n]*\n?", "", text,
                  count=1, flags=re.S | re.M)


def skeleton(text, kinds):
    text = text.replace("\r\n", "\n")
    for kind in kinds:
        begin, end = markers(kind)
        text = re.sub(re.escape(begin) + r".*?" + re.escape(end),
                      lambda _: begin + end, text, count=1, flags=re.S)
    return text


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.nodes, self.stack, self.errors = [], [], []
        self.feed(text)
        self.close()
        if self.stack:
            self.errors.append("Unclosed HTML elements")

    def handle_starttag(self, tag, attrs):
        if len(dict(attrs)) != len(attrs):
            self.errors.append(f"Repeated attributes: {tag}")
        self.nodes.append({"tag": tag, "attrs": {key: value or "" for key, value in attrs},
                           "parent": self.stack[-1] if self.stack else None})
        if tag not in VOID:
            self.stack.append(len(self.nodes) - 1)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.nodes[self.stack[-1]]["tag"] != tag:
            self.errors.append(f"Unmatched HTML closing tag: {tag}")
        else:
            self.stack.pop()


def audit(files, title=None, zip_bytes=None):
    """Static evidence only. Runtime, media decoding and guide human rows remain pending."""
    errors, warnings = [], []
    required = {"index.html", "assets/style.css", "assets/app.js"}
    errors.extend(f"Missing file: {name}" for name in sorted(required - files.keys()))
    for name, data in files.items():
        parts = PurePosixPath(name).parts
        if name != "index.html" and (not parts or parts[0] != "assets" or len(parts) < 2):
            errors.append(f"Not inside the package root: {name}")
        if "\\" in name or any(not re.fullmatch(r"[a-z0-9]+(?:\.[a-z0-9]+)?", part) for part in parts):
            errors.append(f"Invalid filename: {name}")
        if PurePosixPath(name).name == "meta.json":
            errors.append(f"Platform metadata is forbidden: {name}")
        if not data:
            errors.append(f"Empty file: {name}")
        if PurePosixPath(name).suffix in IMAGES and len(data) > 400 * 1024:
            warnings.append(f"Image over the recommended 400KB (not a failure): {name}")
    if zip_bytes is not None and zip_bytes > LIMIT:
        errors.append("ZIP exceeds 50MB")

    def reference(url, owner, base=""):
        url = html.unescape(url.strip())
        if url.startswith("#"):
            return
        if url.startswith(("data:image/", "data:font/", "data:application/font")):
            return
        try:
            parsed = urlsplit(url)
        except ValueError:
            errors.append(f"Invalid URL: {owner}: {url}")
            return
        path = unquote(parsed.path)
        if not path or parsed.scheme or parsed.netloc or path.startswith("/") or "\\" in path:
            errors.append(f"Not a local relative URL: {owner}: {url}")
            return
        target = posixpath.normpath(posixpath.join(base, path))
        if target == ".." or target.startswith("../"):
            errors.append(f"Path escapes ZIP: {owner}: {url}")
        elif target not in files:
            case = next((name for name in files if name.lower() == target.lower()), None)
            errors.append(f"{'Case mismatch' if case else 'Missing reference'}: {owner}: {url}")

    def css_urls(text, owner):
        for match in re.finditer(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", text, re.I):
            reference(match[1], owner, posixpath.dirname(owner))
        for match in re.finditer(r"@import\s+['\"]([^'\"]+)['\"]", text, re.I):
            reference(match[1], owner, posixpath.dirname(owner))

    text = files.get("index.html", b"").decode("utf-8-sig")
    page = Page(text)
    errors.extend(page.errors)
    mains = [i for i, node in enumerate(page.nodes) if node["tag"] == "main"]
    sections = [node for node in page.nodes if node["tag"] == "section" and node["parent"] in mains]
    order = [node["attrs"].get("id") for node in sections]
    expected = list(BLOCKS) if "data-book" in order else list(BLOCKS)[:2]
    if len(mains) != 1 or order != expected:
        errors.append("Required main-direct sections/order do not match the template")
    scripts = [node for node in page.nodes if node["tag"] == "script"]
    if len(scripts) != 1 or scripts[0]["attrs"].get("src") != "./assets/app.js" or any(node["tag"] == "style" for node in page.nodes):
        errors.append("CSS/JS must be merged into the template style.css/app.js slots")
    if title is None and sections:
        title = sections[0]["attrs"].get("data-screen-name", "").removesuffix(" 플레이북")
        warnings.append("Actual requested title must be checked separately; title inferred from screen name")
    ids, screens = [], []
    for node in page.nodes:
        attrs = node["attrs"]
        if "id" in attrs:
            ids.append(attrs["id"])
        if "data-screen-id" in attrs or "data-screen-name" in attrs:
            sid = attrs.get("data-screen-id", "")
            screens.append(sid)
            if not re.fullmatch(r"[a-z0-9_-]{1,40}", sid) or not attrs.get("data-screen-name", "").strip():
                errors.append(f"Invalid screen identifiers: {sid}")
        classes = (attrs.get("class") or "").split()
        if "page-section" in classes and node not in sections:
            errors.append("page-section is not a main-direct standard section")
        if any(value.startswith("userstory-") for value in classes):
            errors.append("Reserved platform class")
        if node["tag"] == "base" or any(key.startswith("on") for key in attrs):
            errors.append("Base URL/inline event handlers are outside the template contract")
        for key in ("src", "href", "poster", "data"):
            if key in attrs:
                reference(attrs[key] or "", "index.html")
        if "srcset" in attrs:
            for item in attrs["srcset"].split(","):
                reference(item.strip().split()[0] if item.strip() else "", "index.html")
        if "style" in attrs:
            css_urls(attrs["style"], "index.html")
    if len(ids) != len(set(ids)) or len(screens) != len(set(screens)):
        errors.append("Repeated DOM id or screen id")
    for node in sections:
        attrs = node["attrs"]
        if attrs.get("id") not in BLOCKS:
            continue
        screen, label, _ = BLOCKS[attrs["id"]]
        if "page-section" not in (attrs.get("class") or "").split() or attrs.get("data-screen-id") != screen:
            errors.append(f"Standard class/screen id mismatch: {attrs['id']}")
        if not title or attrs.get("data-screen-name") != f"{title} {label}":
            errors.append(f"Screen title mismatch: {attrs['id']}")

    base = name_page(read(TEMPLATE / "index.html"), title or "")
    if "data-book" not in order:
        base = remove_databook(base)
    if skeleton(text, expected) != skeleton(base, expected):
        errors.append("HTML outside the permitted paste/title/databook regions changed")
    for name, kind in (("assets/style.css", "css"), ("assets/app.js", "js")):
        actual = files.get(name, b"").decode("utf-8-sig")
        if skeleton(actual, [kind]) != skeleton(read(TEMPLATE / name), [kind]):
            errors.append(f"Template base code changed: {name}")

    for name, data in files.items():
        suffix = PurePosixPath(name).suffix
        if suffix not in {".html", ".css", ".js", ".svg"}:
            continue
        code = data.decode("utf-8-sig")
        if suffix == ".svg":
            try:
                svg = ET.fromstring(code)
                for element in svg.iter():
                    if element.tag.rsplit("}", 1)[-1] == "script":
                        errors.append(f"Script inside SVG requires removal: {name}")
                    for key, value in element.attrib.items():
                        if key.rsplit("}", 1)[-1] in {"href", "src"}:
                            reference(value, name, posixpath.dirname(name))
                    css_urls(element.get("style", ""), name)
                    if element.tag.rsplit("}", 1)[-1] == "style":
                        css_urls(element.text or "", name)
            except ET.ParseError as exc:
                errors.append(f"Invalid SVG: {name}: {exc}")
            continue  # XML namespace URIs are metadata, not network requests.
        code = re.sub(r"/\*.*?\*/|<!--.*?-->|^\s*//[^\n]*", "", code, flags=re.S | re.M)
        if re.search(r"\b(localStorage|sessionStorage|serviceWorker)\b|userstory-sdk|"
                     r"history\s*\.\s*(pushState|replaceState|go|back|forward|scrollRestoration)", code):
            errors.append(f"Forbidden storage/platform/history code: {name}")
        if suffix == ".css":
            css_urls(code, name)
            for selector, rules in re.findall(r"([^{}]+)\{([^{}]*)\}", code):
                roots = {"html", "body", "main", ".page-section", "main > section", *BLOCKS}
                selectors = [item.strip() for item in selector.split(",")]
                for selector in selectors:
                    if selector.lstrip("#") in roots and re.search(
                        r"overflow(?:-y)?\s*:\s*(hidden|clip)|(?<!-)height\s*:\s*100(?:d|s)?vh|"
                        r"position\s*:\s*(absolute|fixed)", rules):
                        errors.append(f"Locked/overlaid page root: {name}: {selector}")
            if re.search(r"position\s*:\s*fixed|scroll-snap-type\s*:[^;]*mandatory", code):
                errors.append(f"Fixed UI or mandatory page snapping needs removal/review: {name}")
        if suffix == ".js":
            if re.search(r"(?:window|document)\s*\.\s*addEventListener\s*\(\s*['\"](?:wheel|touch\w*|keydown)['\"]", code):
                errors.append(f"Global input listener: {name}")
            for match in re.finditer(r"(['\"])((?:\./)?assets/[^'\"\n]+)\1", code):
                reference(match[2], name)
            for match in re.finditer(r"(['\"`])((?:https?:)?//[^'\"`\s]+)\1", code):
                reference(match[2], name)
            if re.search(r"\b(fetch|XMLHttpRequest|WebSocket|EventSource)\b|preventDefault\s*\(|scrollTo\s*\(", code):
                warnings.append(f"Review dynamic network/input/scroll calls in source and browser: {name}")
    return {"code": "failed" if errors else "passed", "errors": list(dict.fromkeys(errors)),
            "warnings": list(dict.fromkeys(warnings)), "files": len(files), "zip_bytes": zip_bytes,
            "delivery": "review", "browser": "not_run", "media_decode": "not_run", "platform": "not_run",
            "remaining": "Complete every row of tasks/audit.md (guide chapters 7 and 9); static evidence is not final approval."}


def audit_path(path, title=None):
    path = Path(path).resolve()
    if path.is_dir():
        files = {}
        for item in path.rglob("*"):
            if item.is_symlink() or not item.resolve().is_relative_to(path):
                raise ValueError(f"Linked or escaping package entry: {item}")
            parts = item.relative_to(path).parts
            if item.is_dir() and (parts[0] != "assets" or any(not re.fullmatch(r"[a-z0-9]+", part) for part in parts)):
                raise ValueError(f"Invalid package directory: {item.relative_to(path)}")
            if item.is_file():
                files[item.relative_to(path).as_posix()] = item.read_bytes()
        return audit(files, title)
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len(names) != len(set(names)):
            raise ValueError("Repeated ZIP entries")
        # ponytail: bound in-memory ZIP inspection to 256MB; stream larger archives when required.
        if sum(entry.file_size for entry in entries) > 256 * 1024 * 1024:
            raise ValueError("ZIP inspection tool limit: 256MB expanded; inspect the source folder instead")
        for entry in entries:
            parts = PurePosixPath(entry.filename).parts
            if "\\" in entry.filename or entry.filename.startswith("/") or ".." in parts or stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError(f"Unsafe ZIP entry: {entry.filename}")
            if entry.is_dir() and (not parts or parts[0] != "assets" or any(not re.fullmatch(r"[a-z0-9]+", part) for part in parts)):
                raise ValueError(f"Invalid ZIP root directory: {entry.filename}")
        corrupt = archive.testzip()
        if corrupt:
            raise ValueError(f"ZIP CRC failure: {corrupt}")
        return audit({entry.filename: archive.read(entry) for entry in entries if not entry.is_dir()},
                     title, path.stat().st_size)


def build(config_path, output):
    config_path = Path(config_path).resolve()
    config = json.loads(read(config_path))
    if not isinstance(config, dict) or set(config) - {"title", "playbook", "scenariocanvas", "databook"}:
        raise ValueError("Config needs title, playbook, scenariocanvas and optional databook")
    title = config.get("title")
    if not isinstance(title, str) or not title.strip() or title != title.strip() or any(ord(c) < 32 for c in title):
        raise ValueError("A nonempty actual title without boundary whitespace/control characters is required")
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Output already exists; choose a new path, never overwrite source or a delivery")
    if output.is_relative_to(ROOT):
        raise ValueError("Keep generated output outside the plugin")
    prepared, mapping = [], []
    for key, section, folder, prefix, kinds in (
        ("playbook", "playbook", "playbook", "p", {"video", "image"}),
        ("scenariocanvas", "scenario-canvas", "scenariocanvas", "s", {"card", "vertical"}),
        ("databook", "data-book", "databook", "d", {"image"}),
    ):
        block = config.get(key)
        if key == "databook" and block is None:
            continue
        if not isinstance(block, dict) or set(block) - {"type", "files", "background"} or block.get("type") not in kinds:
            raise ValueError(f"Invalid {key} type/options; authored HTML/PDF/game/sequence content uses tasks/build.md")
        kind, entries = block["type"], block.get("files")
        if not isinstance(entries, list) or not entries or (kind == "video" and len(entries) != 1):
            raise ValueError(f"{key} needs ordered media files; the video component takes one finished video")
        sources = []
        for number, entry in enumerate(entries, 1):
            if isinstance(entry, str):
                entry = {"path": entry}
            if not isinstance(entry, dict) or set(entry) - {"path", "alt"} or not isinstance(entry.get("path"), str):
                raise ValueError(f"Invalid media entry: {key} {number}")
            source = (config_path.parent / entry["path"]).resolve()
            if not source.is_file() or source.stat().st_size == 0:
                raise ValueError(f"Missing/empty media: {source}")
            if source.is_relative_to(output):
                raise ValueError("An input overlaps the output")
            if source.suffix.lower() not in (VIDEOS if kind == "video" else IMAGES):
                raise ValueError(f"Unsupported {kind} media: {source}")
            alt = entry.get("alt", f"{title} {BLOCKS[section][1]} {number}")
            if not isinstance(alt, str) or not alt.strip():
                raise ValueError("Meaningful nonempty alt/label is required")
            destination = f"assets/{folder}/{prefix}{number}{source.suffix.lower()}"
            sources.append((source, destination, alt))
            mapping.append({"source": str(source), "destination": destination})
        background = block.get("background", "#000000" if kind == "video" else "#e8e7e4" if kind == "card" else "#ffffff")
        if not isinstance(background, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", background):
            raise ValueError(f"Invalid background color: {key}")
        prepared.append((section, kind, sources, background.lower()))

    index, css, js = (read(TEMPLATE / name) for name in ("index.html", "assets/style.css", "assets/app.js"))
    index = name_page(index, title)
    if config.get("databook") is None:
        index = remove_databook(index)
    styles, scripts = {}, {}
    output.mkdir(parents=True)
    for folder in ("playbook", "scenariocanvas", "databook"):
        (output / "assets" / folder).mkdir(parents=True)
    for section, kind, sources, background in prepared:
        component = "playbookvideo" if kind == "video" else "canvascard" if kind == "card" else "image"
        fragment = read(COMPONENTS / f"{component}.html")
        images = []
        for source, destination, alt in sources:
            shutil.copyfile(source, output / destination)
            if kind != "video":
                image = read(COMPONENTS / "image.html").replace("{{source}}", html.escape(destination, quote=True)).replace("{{alt}}", html.escape(alt, quote=True))
                images.append(image)
        if kind == "card":
            slides = "\n".join(f'<div class="ukcards-slide{ " active" if n == 0 else ""}" aria-hidden="{str(n != 0).lower()}">{image}</div>'
                               for n, image in enumerate(images))
            fragment = fragment.replace("{{slides}}", slides).replace("{{count}}", str(len(images)))
        elif kind == "video":
            fragment = fragment.replace("{{source}}", html.escape(sources[0][1], quote=True)).replace("{{alt}}", html.escape(sources[0][2], quote=True))
        else:
            fragment = "\n".join(images)
        index = insert(index, section, fragment)
        styles[section] = f"#{section} {{ background: {background}; }}"
        styles[component] = read(COMPONENTS / f"{component}.css")
        script = COMPONENTS / f"{component}.js"
        if script.exists():
            scripts[component] = read(script)
    css, js = insert(css, "css", "\n".join(styles.values())), insert(js, "js", "\n".join(scripts.values()))
    for name, content in (("index.html", index), ("assets/style.css", css), ("assets/app.js", js)):
        (output / name).write_bytes(content.encode("utf-8"))
    result = audit_path(output, title)
    if result["errors"]:
        raise ValueError(f"Static audit failed; output retained for repair: {result['errors']}")
    result.update({"output": str(output), "assets": mapping})
    return result


def package(output, zip_path, title=None):
    output, zip_path = Path(output).resolve(), Path(zip_path).resolve()
    if not output.is_dir():
        raise ValueError("Packaging needs an existing content folder")
    if zip_path.exists():
        raise ValueError("ZIP already exists; choose a new path, never overwrite source or a delivery")
    if output.is_relative_to(ROOT) or zip_path.is_relative_to(ROOT) or zip_path.is_relative_to(output):
        raise ValueError("Keep content and ZIP outside the plugin and keep ZIP outside the content folder")
    result = audit_path(output, title)
    if result["errors"]:
        raise ValueError(f"Static audit failed; ZIP not created: {result['errors']}")
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zip_path.open("xb") as handle, zipfile.ZipFile(handle, "w", zipfile.ZIP_DEFLATED) as archive:
        for item in sorted(output.rglob("*")):
            if item.is_file():
                archive.write(item, item.relative_to(output).as_posix())
    result = audit_path(zip_path, title)
    result.update({"output": str(output), "zip": str(zip_path)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("build", help="Assemble the standard media components into a NEW output folder; no ZIP")
    make.add_argument("config")
    make.add_argument("output")
    pack = commands.add_parser("package", help="Package an existing content folder; not browser/platform approval")
    pack.add_argument("path")
    pack.add_argument("zip")
    pack.add_argument("--title")
    check = commands.add_parser("audit", help="Read-only static inspection; not browser/platform approval")
    check.add_argument("path")
    check.add_argument("--title")
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = build(args.config, args.output)
        elif args.command == "package":
            result = package(args.path, args.zip, args.title)
        else:
            result = audit_path(args.path, args.title)
    except (OSError, ValueError, UnicodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"code": "failed", "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(result["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
