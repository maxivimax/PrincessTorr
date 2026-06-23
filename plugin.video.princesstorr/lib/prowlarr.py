import re

from . import cache, utils

CAT_MOVIES = 2000
CAT_TV = 5000


def _base():
    return utils.setting("prowlarr_url", "http://localhost:9696").rstrip("/")


def _headers():
    return {"X-Api-Key": utils.setting("prowlarr_api_key")}


def _indexer_ids():
    raw = utils.setting("prowlarr_indexer_ids")
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _search_once(query, category):
    params = {
        "query": query,
        "type": "search",
        "categories": category,
        "indexerIds": _indexer_ids(),
    }
    url = "%s/api/v1/search?%s" % (_base(), utils.build_query(params))
    data = utils.http_get_json(url, headers=_headers())
    return data if isinstance(data, list) else []


def _release_key(release):
    info_hash = (release.get("infoHash") or "").lower()
    if info_hash:
        return "hash:" + info_hash
    guid = release.get("guid") or ""
    if guid:
        return "guid:" + guid
    title = re.sub(r"\s+", " ", (release.get("title") or "").lower()).strip()
    return "title:%s:%s" % (title, release.get("size") or 0)


def search(queries, category):
    queries = [q for q in dict.fromkeys(q.strip() for q in queries) if q]
    ttl = utils.setting_int("cache_minutes", 30) * 60
    cache_key = "prowlarr:%s:%s" % (category, "|".join(queries))

    cached = cache.get(cache_key, ttl)
    if cached is not None:
        return cached

    merged = {}
    for query in queries:
        for release in _search_once(query, category):
            key = _release_key(release)
            existing = merged.get(key)
            if existing is None or _seeders(release) > _seeders(existing):
                merged[key] = release

    results = sorted(merged.values(), key=_seeders, reverse=True)
    if results:
        cache.set(cache_key, results)
    return results


def _seeders(release):
    value = release.get("seeders")
    return value if isinstance(value, int) else 0


def normalize(release):
    return {
        "title": release.get("title") or "",
        "indexer": release.get("indexer") or "",
        "seeders": _seeders(release),
        "leechers": release.get("leechers") or 0,
        "size": release.get("size") or 0,
        "magnet": release.get("magnetUrl") or "",
        "download_url": release.get("downloadUrl") or "",
        "protocol": release.get("protocol") or "",
        "quality": _detect_quality(release.get("title") or ""),
        "has_russian": _has_russian_audio(release.get("title") or ""),
        "voices": [],
    }


_QUALITY_PATTERNS = [
    ("4K", r"\b(2160p|4k|uhd)\b"),
    ("1080p", r"\b1080p\b"),
    ("720p", r"\b720p\b"),
    ("SD", r"\b(480p|dvdrip|sd)\b"),
]


def _detect_quality(title):
    low = title.lower()
    for label, pattern in _QUALITY_PATTERNS:
        if re.search(pattern, low):
            return label
    return ""


def _has_russian_audio(title):
    low = title.lower()
    return bool(re.search(r"(rus|русск|дубляж|многоголос|mvo|dvo|лицензия)", low))


def human_size(num_bytes):
    try:
        num = float(num_bytes)
    except (TypeError, ValueError):
        return ""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num < 1024.0:
            return "%.1f %s" % (num, unit)
        num /= 1024.0
    return "%.1f PB" % num
