"""Run with Python 3.10+; no test framework or authored media required."""

import itertools
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

from userstory import audit_path, build


def main():
    node = shutil.which("node")
    with tempfile.TemporaryDirectory(prefix="userstory-check-") as temporary:
        root = Path(temporary).resolve()
        image = root / "Author Image.SVG"
        image.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080">'
                         '<rect width="1920" height="1080" fill="#fff"/></svg>', encoding="utf-8")
        video = root / "Author Video.WEBM"
        video.write_bytes(b"\x1a\x45\xdf\xa3static-path-test-only")
        originals = {path: path.read_bytes() for path in (image, video)}
        config_path = root / "input.json"
        tab_title = '<title>제목 "인용" &amp; &lt;확인&gt;</title>'
        good = None
        for number, (pb, canvas, data) in enumerate(itertools.product(("video", "image"), ("card", "vertical"), (False, True))):
            config = {"title": '제목 "인용" & <확인>',
                      "playbook": {"type": pb, "files": [video.name if pb == "video" else image.name]},
                      "scenariocanvas": {"type": canvas, "files": [image.name] * (2 if canvas == "card" else 1)},
                      "databook": {"type": "image", "files": [image.name]} if data else None}
            config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
            output, archive = root / f"case{number}", root / f"case{number}.zip"
            result = build(config_path, output, archive)
            assert result["code"] == "passed", result
            assert result["browser"] == result["media_decode"] == result["platform"] == "not_run"
            page = (output / "index.html").read_text(encoding="utf-8")
            assert tab_title in page
            assert ('id="data-book"' in page) == data
            with zipfile.ZipFile(archive) as packaged:
                assert all(name == "index.html" or name.startswith("assets/") for name in packaged.namelist())
                assert tab_title in packaged.read("index.html").decode("utf-8")
            for mapping in result["assets"]:
                assert (output / mapping["destination"]).read_bytes() == Path(mapping["source"]).read_bytes()
            if node:
                subprocess.run([node, "--check", str(output / "assets/app.js")], check=True, capture_output=True)
            good = output
        assert all(path.read_bytes() == content for path, content in originals.items())
        try:
            build(config_path, good, root / "overwrite.zip")
        except ValueError as error:
            assert "already exists" in str(error)
        else:
            raise AssertionError("An existing delivery must never be overwritten")

        index = good / "index.html"
        original = index.read_bytes()
        for needle, replacement, message in (
            (tab_title, '<title>UserStory</title>', "HTML outside the permitted paste/title/databook regions changed"),
            ('assets/playbook/p1.svg', 'assets/playbook/P1.svg', "Case mismatch"),
            ('assets/playbook/p1.svg', 'assets/playbook/missing.svg', "Missing reference"),
            ('assets/playbook/p1.svg', '../../outside.svg', "Path escapes ZIP"),
            ('assets/playbook/p1.svg', 'https://example.invalid/image.svg', "Not a local relative URL"),
            ('class="ukimage"', 'class="ukimage" data-screen-id="canvas_main" data-screen-name="중복"', "Repeated DOM id or screen id"),
        ):
            assert needle.encode() in original
            index.write_bytes(original.replace(needle.encode(), replacement.encode(), 1))
            assert any(message in item for item in audit_path(good)["errors"]), message
        index.write_bytes(original)
        app = good / "assets/app.js"
        original_js = app.read_bytes()
        for bad, message in (("localStorage.setItem('a','b');", "Forbidden storage"),
                             ("window.addEventListener('wheel', e => e.preventDefault());", "Global input listener")):
            app.write_bytes(original_js.replace(b"// \xe2\x96\xb2", bad.encode() + b"\n// \xe2\x96\xb2", 1))
            assert any(message in item for item in audit_path(good)["errors"]), message
        app.write_bytes(original_js)
        svg = good / "assets/playbook/p1.svg"
        original_svg = svg.read_bytes()
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><image href="https://example.invalid/a.png"/></svg>', encoding="utf-8")
        assert any("Not a local relative URL" in item for item in audit_path(good)["errors"])
        svg.write_text("<svg>", encoding="utf-8")
        assert any("Invalid SVG" in item for item in audit_path(good)["errors"])
        svg.write_bytes(original_svg)
        unsafe = root / "unsafe.zip"
        with zipfile.ZipFile(unsafe, "w") as archive:
            archive.writestr("../escape.txt", "not extracted")
        try:
            audit_path(unsafe)
        except ValueError as error:
            assert "Unsafe ZIP entry" in str(error)
        else:
            raise AssertionError("ZIP traversal was accepted")
        invalid_dir = root / "invaliddir.zip"
        with zipfile.ZipFile(invalid_dir, "w") as archive:
            archive.writestr("assets/BadName/", "")
        try:
            audit_path(invalid_dir)
        except ValueError as error:
            assert "Invalid ZIP root directory" in str(error)
        else:
            raise AssertionError("An invalid empty ZIP directory was accepted")
        (good / "assets/BadName").mkdir()
        try:
            audit_path(good)
        except ValueError as error:
            assert "Invalid package directory" in str(error)
        else:
            raise AssertionError("An invalid empty package directory was accepted")
        (good / "assets/BadName").rmdir()
        assert audit_path(good)["code"] == "passed"
    print("PASS: 8 media combinations, browser tab titles/escaping, optional databook removal, exact bytes/paths, source protection and rejection checks")
    print("JS syntax: " + ("PASS" if node else "NOT RUN (node unavailable)"))
    print("Media decoding/browser/platform: NOT RUN by this self-check; use tasks/audit.md")


if __name__ == "__main__":
    main()
