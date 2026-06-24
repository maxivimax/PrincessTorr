#!/usr/bin/env python3
"""Подготовить релиз из верхнего раздела CHANGELOG.md.

Источник правды — самый верхний раздел `## <version>` в CHANGELOG.md.
Скрипт:
  - выставляет version в addon.xml равной версии верхнего раздела;
  - формирует тело GitHub Release (пункты раздела + ссылку Full Changelog);
  - если запущен в Actions (есть GITHUB_OUTPUT) — отдаёт version/prev/body_path.

Запуск: python3 tools/release.py
"""
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON_XML = os.path.join(ROOT, "plugin.video.princesstorr", "addon.xml")
CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")


def sections():
    text = open(CHANGELOG, encoding="utf-8").read()
    found = re.findall(r"(?ms)^## (.+?)\n(.*?)(?=^## |\Z)", text)
    return [(ver.strip(), body.strip()) for ver, body in found]


def set_version(version):
    text = open(ADDON_XML, encoding="utf-8").read()
    new, count = re.subn(r'(\n\s*version=")[^"]*(")',
                         r"\g<1>%s\g<2>" % version, text, count=1)
    if count != 1:
        sys.exit("addon.xml: атрибут version не найден")
    open(ADDON_XML, "w", encoding="utf-8").write(new)


def main():
    secs = sections()
    if not secs:
        sys.exit("CHANGELOG.md: нет разделов '## <version>'")
    version, body = secs[0]
    prev = secs[1][0] if len(secs) > 1 else ""

    set_version(version)

    repo = os.environ.get("GITHUB_REPOSITORY") or "maxivimax/PrincessTorr"
    notes = body
    if prev:
        notes += ("\n\n**Full Changelog**: "
                  "https://github.com/%s/compare/v%s...v%s" % (repo, prev, version))

    tmp = os.environ.get("RUNNER_TEMP") or tempfile.gettempdir()
    body_path = os.path.join(tmp, "princesstorr_release_body.md")
    open(body_path, "w", encoding="utf-8").write(notes + "\n")

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write("version=%s\n" % version)
            fh.write("prev=%s\n" % prev)
            fh.write("body_path=%s\n" % body_path)

    print("version=%s prev=%s body_path=%s" % (version, prev, body_path))


if __name__ == "__main__":
    main()
