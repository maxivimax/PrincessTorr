#!/usr/bin/env python3
"""Собрать Kodi-репозиторий для раздачи через GitHub Pages.

Создаёт в каталоге docs/:
  - docs/<addon_id>/<addon_id>-<version>.zip для каждого аддона;
  - docs/addons.xml      — индекс репозитория;
  - docs/addons.xml.md5  — контрольная сумма индекса;
  - docs/.nojekyll       — чтобы Pages отдавал файлы как есть.

Релиз: поднять version в addon.xml -> python3 tools/build_repo.py -> git push.
"""
import hashlib
import os
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
ADDONS = ["plugin.video.princesstorr", "repository.princesstorr"]

EXCLUDE_DIRS = {"__pycache__"}
EXCLUDE_EXT = {".pyc", ".pyo"}
EXCLUDE_NAMES = {".DS_Store"}


def addon_version(addon_id):
    tree = ET.parse(os.path.join(ROOT, addon_id, "addon.xml"))
    return tree.getroot().get("version")


def make_zip(addon_id):
    version = addon_version(addon_id)
    out_dir = os.path.join(DOCS, addon_id)
    os.makedirs(out_dir, exist_ok=True)
    zip_path = os.path.join(out_dir, "%s-%s.zip" % (addon_id, version))
    src = os.path.join(ROOT, addon_id)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for base, dirs, files in os.walk(src):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
            for name in sorted(files):
                if name in EXCLUDE_NAMES or os.path.splitext(name)[1] in EXCLUDE_EXT:
                    continue
                full = os.path.join(base, name)
                # путь внутри zip начинается с папки аддона — так ждёт Kodi
                arcname = os.path.relpath(full, ROOT)
                zf.write(full, arcname)
    return version, zip_path


def addon_node(addon_id):
    with open(os.path.join(ROOT, addon_id, "addon.xml"), encoding="utf-8") as fh:
        text = fh.read()
    return re.sub(r"<\?xml[^>]*\?>\s*", "", text, count=1).strip()


def build_index():
    parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>', "<addons>"]
    parts.extend(addon_node(a) for a in ADDONS)
    parts.append("</addons>")
    xml = "\n".join(parts) + "\n"

    with open(os.path.join(DOCS, "addons.xml"), "w", encoding="utf-8") as fh:
        fh.write(xml)
    digest = hashlib.md5(xml.encode("utf-8")).hexdigest()
    with open(os.path.join(DOCS, "addons.xml.md5"), "w", encoding="utf-8") as fh:
        fh.write(digest)
    return digest


def main():
    os.makedirs(DOCS, exist_ok=True)
    open(os.path.join(DOCS, ".nojekyll"), "a").close()
    for addon_id in ADDONS:
        version, path = make_zip(addon_id)
        print("zip   %-28s -> %s" % (addon_id, os.path.relpath(path, ROOT)))
    print("index addons.xml.md5         =", build_index())


if __name__ == "__main__":
    main()
