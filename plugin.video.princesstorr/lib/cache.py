import hashlib
import json
import os
import time

import xbmcvfs

from . import utils


def _cache_dir():
    path = os.path.join(utils.profile_dir(), "cache")
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdirs(path)
    return path


def _path_for(key):
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
    return os.path.join(_cache_dir(), digest + ".json")


def get(key, ttl_seconds):
    if ttl_seconds <= 0:
        return None
    path = _path_for(key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (ValueError, OSError):
        return None
    if time.time() - payload.get("ts", 0) > ttl_seconds:
        return None
    return payload.get("data")


def set(key, data):
    path = _path_for(key)
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({"ts": time.time(), "data": data}, handle)
    except OSError as exc:
        utils.log("Не удалось записать кэш: %s" % exc)
