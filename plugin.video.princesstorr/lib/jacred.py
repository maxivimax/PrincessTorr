from . import cache, utils

_QUALITY = {2160: "4K", 1080: "1080p", 720: "720p", 480: "SD"}


def _base():
    return utils.setting("jacred_url", "https://ru.jacred.pro").rstrip("/")


def _search(params):
    ttl = utils.setting_int("cache_minutes", 30) * 60
    url = "%s/api/v1.0/torrents?%s" % (_base(), utils.build_query(params))
    cache_key = "jacred:" + url

    cached = cache.get(cache_key, ttl)
    if cached is not None:
        return cached

    data = utils.http_get_json(url)
    results = data if isinstance(data, list) else []
    norm = [n for n in (normalize(r) for r in results) if n["magnet"]]
    norm.sort(key=lambda n: n["seeders"], reverse=True)
    if norm:
        cache.set(cache_key, norm)
    return norm


def search_movie(title, original):
    return _search({"search": title or original, "exact": "true"})


def search_tv(name, original, season=None):
    params = {"search": name or original, "exact": "true"}
    if season:
        params["season"] = season
    return _search(params)


def normalize(r):
    voices = r.get("voices") or []
    return {
        "title": r.get("title") or "",
        "indexer": r.get("tracker") or "",
        "seeders": r.get("sid") or 0,
        "leechers": r.get("pir") or 0,
        "size": r.get("size") or 0,
        "magnet": r.get("magnet") or "",
        "download_url": "",
        "protocol": "torrent",
        "quality": _QUALITY.get(r.get("quality"), ""),
        "has_russian": bool(voices),
        "voices": voices,
    }
