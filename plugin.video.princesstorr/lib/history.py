import json
import os
import time

from . import utils

MAX_ITEMS = 50


def _path():
    return os.path.join(utils.profile_dir(), "history.json")


def _load():
    path = _path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, list) else []
    except (ValueError, OSError):
        return []


def _save(items):
    try:
        with open(_path(), "w", encoding="utf-8") as handle:
            json.dump(items[:MAX_ITEMS], handle, ensure_ascii=False)
    except OSError as exc:
        utils.log("Не удалось записать историю: %s" % exc)


def record(media_type, tmdb_id, title, poster, season="", episode=""):
    if not tmdb_id:
        return
    key = (media_type, str(tmdb_id))
    items = [i for i in _load() if (i.get("mt"), str(i.get("id"))) != key]
    items.insert(0, {
        "mt": media_type,
        "id": str(tmdb_id),
        "title": title or "",
        "poster": poster or "",
        "s": str(season or ""),
        "e": str(episode or ""),
        "ts": int(time.time()),
    })
    _save(items)


def items():
    return _load()


def remove(media_type, tmdb_id):
    key = (media_type, str(tmdb_id))
    _save([i for i in _load() if (i.get("mt"), str(i.get("id"))) != key])


def clear():
    _save([])
