import re

from . import cache, utils

_QUALITY = {2160: "4K", 1080: "1080p", 720: "720p", 480: "SD"}

_RUS_AUDIO = re.compile(
    r"дубляж|дублир|многоголос|одноголос|двухголос|закадров|любительск|"
    r"профессиональн|\bдуб\b|\bлм\b|\bло\b|\bпм\b|\bмво\b|\bдво\b|\bаво\b|"
    r"\bmvo\b|\bdvo\b|\bavo\b|\bdub\b|\brus\b|русск",
    re.IGNORECASE,
)
_RUS_BY = re.compile(r"\bот\s+\w", re.IGNORECASE)
_SUBS_ONLY = re.compile(r"субтитр|\bст\b|\bsub\b", re.IGNORECASE)


def _has_russian(r):
    if r.get("voices"):
        return True
    title = r.get("title") or ""
    if _RUS_AUDIO.search(title):
        return True
    if _RUS_BY.search(title) and not _SUBS_ONLY.search(title):
        return True
    return False


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


def search_movie(title, original, year=None):
    results = _merge_searches(title, original)
    matched = _filter_by_year(results, year)
    return matched or results


def _merge_searches(*terms, **params):
    merged = {}
    for term in dict.fromkeys(t for t in terms if t):
        query = {"search": term, "exact": "true"}
        query.update(params)
        for r in _search(query):
            merged.setdefault(r["magnet"], r)
    return sorted(merged.values(), key=lambda r: r["seeders"], reverse=True)


def _filter_by_year(results, year):
    try:
        y = int(year)
    except (TypeError, ValueError):
        return results
    exact = [r for r in results if r.get("year") == y]
    if exact:
        return exact
    return [r for r in results if r.get("year") and abs(r["year"] - y) <= 1]


def search_tv(name, original, season=None):
    extra = {"season": season} if season else {}
    return _merge_searches(name, original, **extra)


def normalize(r):
    voices = r.get("voices") or []
    return {
        "title": r.get("title") or "",
        "originalname": r.get("originalname") or "",
        "year": r.get("relased") or 0,
        "indexer": r.get("tracker") or "",
        "seeders": r.get("sid") or 0,
        "leechers": r.get("pir") or 0,
        "size": r.get("size") or 0,
        "magnet": r.get("magnet") or "",
        "download_url": "",
        "protocol": "torrent",
        "quality": _QUALITY.get(r.get("quality"), ""),
        "has_russian": _has_russian(r),
        "voices": voices,
    }
