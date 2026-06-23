import datetime
import re
import sys
import urllib.parse

import xbmc
import xbmcgui
import xbmcplugin

from . import history, jacktorr, jacred, prowlarr, tmdb, utils

HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

L = utils.localize


def url_for(action, **kwargs):
    kwargs["action"] = action
    return "%s?%s" % (BASE_URL, urllib.parse.urlencode(kwargs))


def _params():
    return dict(urllib.parse.parse_qsl(sys.argv[2][1:]))


def index():
    if history.items():
        _add_dir(L(30190), url_for("history_list"))
    _add_dir(L(30001), url_for("movies_root"))
    _add_dir(L(30002), url_for("tv_root"))
    _add_dir(L(30003), url_for("search_movies"))
    _add_dir(L(30004), url_for("search_tv"))
    _end()


def movies_root():
    _add_dir(L(30010), url_for("movie_list", kind="popular"))
    _add_dir(L(30011), url_for("movie_list", kind="now_playing"))
    _add_dir(L(30012), url_for("movie_list", kind="upcoming"))
    _add_dir(L(30013), url_for("movie_list", kind="top_rated"))
    _add_dir(L(30014), url_for("movie_genres"))
    _add_dir(L(30015), url_for("search_movies"))
    _end()


def tv_root():
    _add_dir(L(30010), url_for("tv_list", kind="popular"))
    _add_dir(L(30016), url_for("tv_list", kind="on_the_air"))
    _add_dir(L(30013), url_for("tv_list", kind="top_rated"))
    _add_dir(L(30014), url_for("tv_genres"))
    _add_dir(L(30015), url_for("search_tv"))
    _end()


def movie_list():
    params = _params()
    kind = params.get("kind", "popular")
    page = int(params.get("page", 1))
    data = tmdb.movies_list(kind, page) or {}
    _render_movies(data, lambda p: url_for("movie_list", kind=kind, page=p), page)


def movie_genres():
    data = tmdb.movie_genres() or {}
    for genre in data.get("genres", []):
        _add_dir(genre.get("name", ""),
                 url_for("movie_by_genre", genre_id=genre.get("id")))
    _end()


def movie_by_genre():
    params = _params()
    genre_id = params.get("genre_id")
    page = int(params.get("page", 1))
    data = tmdb.movies_by_genre(genre_id, page) or {}
    _render_movies(
        data, lambda p: url_for("movie_by_genre", genre_id=genre_id, page=p), page)


def search_movies():
    query = _ask(L(30003))
    if not query:
        _end()
        return
    params = _params()
    page = int(params.get("page", 1))
    data = tmdb.search_movies(query, page) or {}
    _render_movies(data, None, page)


def tv_list():
    params = _params()
    kind = params.get("kind", "popular")
    page = int(params.get("page", 1))
    data = tmdb.tv_list(kind, page) or {}
    _render_tv(data, lambda p: url_for("tv_list", kind=kind, page=p), page)


def tv_genres():
    data = tmdb.tv_genres() or {}
    for genre in data.get("genres", []):
        _add_dir(genre.get("name", ""),
                 url_for("tv_by_genre", genre_id=genre.get("id")))
    _end()


def tv_by_genre():
    params = _params()
    genre_id = params.get("genre_id")
    page = int(params.get("page", 1))
    data = tmdb.tv_by_genre(genre_id, page) or {}
    _render_tv(data, lambda p: url_for("tv_by_genre", genre_id=genre_id, page=p), page)


def search_tv():
    query = _ask(L(30004))
    if not query:
        _end()
        return
    data = tmdb.search_tv(query) or {}
    _render_tv(data, None, 1)


def tv_seasons():
    params = _params()
    tmdb_id = params.get("tmdb_id")
    details = tmdb.tv_details(tmdb_id) or {}
    show_title = details.get("name") or details.get("original_name") or ""
    for season in details.get("seasons", []):
        number = season.get("season_number")
        if number is None:
            continue
        label = season.get("name") or (L(30022) % number)
        item = xbmcgui.ListItem(label)
        poster = (utils.image_url(season.get("poster_path"))
                  or utils.image_url(details.get("poster_path")))
        item.setArt({
            "poster": poster,
            "thumb": poster,
            "fanart": utils.image_url(details.get("backdrop_path"), "w780"),
        })
        item.addContextMenuItems([(
            L(30021),
            "Container.Update(%s)" % url_for(
                "season_torrents", tmdb_id=tmdb_id, season=number),
        )])
        xbmcplugin.addDirectoryItem(
            HANDLE,
            url_for("tv_episodes", tmdb_id=tmdb_id, season=number),
            item, isFolder=True)
    _end()


def tv_episodes():
    params = _params()
    tmdb_id = params.get("tmdb_id")
    season = params.get("season")
    details = tmdb.season_details(tmdb_id, season) or {}
    season_poster = utils.image_url(details.get("poster_path"))
    for ep in details.get("episodes", []):
        number = ep.get("episode_number")
        name = ep.get("name") or ""
        base = "%sx%02d %s" % (season, number or 0, name)
        aired, air_fmt = _air_status(ep.get("air_date"))
        thumb = utils.image_url(ep.get("still_path"), "w300") or season_poster

        if aired:
            label = base
            plot = ep.get("overview") or ""
            target = url_for("episode_torrents",
                             tmdb_id=tmdb_id, season=season, episode=number)
            is_folder = True
        else:
            when = (L(30161) % air_fmt) if air_fmt else L(30162)
            label = "[COLOR gray]%s — %s (%s)[/COLOR]" % (base, L(30160), when)
            plot = "%s\n\n%s" % (when, ep.get("overview") or "")
            target = url_for("not_aired", when=air_fmt)
            is_folder = False

        item = xbmcgui.ListItem(label)
        item.setArt({"thumb": thumb, "poster": thumb})
        item.setInfo("video", {
            "title": name,
            "plot": plot,
            "season": int(season),
            "episode": number or 0,
            "mediatype": "episode",
        })
        if not aired:
            item.setProperty("IsPlayable", "false")
        xbmcplugin.addDirectoryItem(HANDLE, target, item, isFolder=is_folder)
    _end()


def not_aired():
    when = _params().get("when", "")
    utils.notify((L(30161) % when) if when else L(30162))
    xbmcplugin.endOfDirectory(HANDLE, succeeded=False)


def _air_status(air_date):
    if not air_date:
        return False, ""
    try:
        d = datetime.date.fromisoformat(air_date)
    except ValueError:
        return False, ""
    return d <= datetime.date.today(), d.strftime("%d.%m.%Y")


def _source():
    return "prowlarr" if utils.setting_int("search_source", 0) == 1 else "jacred"


def movie_torrents():
    params = _params()
    details = tmdb.movie_details(params.get("tmdb_id")) or {}
    title = details.get("title") or ""
    original = details.get("original_title") or ""
    year = (details.get("release_date") or "")[:4]
    imdb = (details.get("external_ids") or {}).get("imdb_id") or ""

    if _source() == "jacred":
        releases = jacred.search_movie(title, original)
    else:
        queries = _movie_queries(title, original, year, imdb)
        releases = [prowlarr.normalize(r)
                    for r in prowlarr.search(queries, prowlarr.CAT_MOVIES)]
    ctx = {"mt": "movie", "id": params.get("tmdb_id"), "title": title,
           "poster": details.get("poster_path") or "", "s": "", "e": ""}
    _render_releases(releases, "%s (%s)" % (title, year), ctx)


def season_torrents():
    params = _params()
    details = tmdb.tv_details(params.get("tmdb_id")) or {}
    season = params.get("season")
    title = details.get("name") or ""
    original = details.get("original_name") or ""

    if _source() == "jacred":
        releases = jacred.search_tv(title, original, season)
    else:
        queries = _season_queries(title, original, season)
        releases = [prowlarr.normalize(r)
                    for r in prowlarr.search(queries, prowlarr.CAT_TV)]
    ctx = {"mt": "tv", "id": params.get("tmdb_id"), "title": title,
           "poster": details.get("poster_path") or "", "s": season, "e": ""}
    _render_releases(releases, "%s — сезон %s" % (title, season), ctx)


def episode_torrents():
    params = _params()
    details = tmdb.tv_details(params.get("tmdb_id")) or {}
    season = params.get("season")
    episode = params.get("episode")
    title = details.get("name") or ""
    original = details.get("original_name") or ""

    if _source() == "jacred":
        releases = jacred.search_tv(title, original, season)
    else:
        queries = _episode_queries(title, original, season, episode)
        releases = [prowlarr.normalize(r)
                    for r in prowlarr.search(queries, prowlarr.CAT_TV)]
    releases = [r for r in releases if _covers_episode(r.get("title", ""), episode)]
    ctx = {"mt": "tv", "id": params.get("tmdb_id"), "title": title,
           "poster": details.get("poster_path") or "", "s": season, "e": episode}
    _render_releases(releases, "%s S%02dE%02d" % (title, int(season), int(episode)), ctx)


_EP_RANGE_PATTERNS = [
    r"e(\d{1,3})\s*-\s*e?(\d{1,3})",
    r"\dx(\d{1,3})\s*-\s*(\d{1,3})",
    r"сери[ияй]\s*:?\s*(\d{1,3})\s*-\s*(\d{1,3})",
    r"(\d{1,3})\s*-\s*(\d{1,3})\s*(?:сери|из)",
]
_EP_SINGLE_PATTERNS = [
    r"s\d{1,2}e(\d{1,3})(?!\s*-)",
    r"сери[яюи]\s*(\d{1,3})\b",
]


def _covers_episode(title, episode):
    try:
        ep = int(episode)
    except (TypeError, ValueError):
        return True
    low = title.lower()
    ranges = []
    for pat in _EP_RANGE_PATTERNS:
        for m in re.finditer(pat, low):
            a, b = int(m.group(1)), int(m.group(2))
            if a <= b <= 999:
                ranges.append((a, b))
    for pat in _EP_SINGLE_PATTERNS:
        for m in re.finditer(pat, low):
            n = int(m.group(1))
            ranges.append((n, n))
    if not ranges:
        return True
    return any(a <= ep <= b for a, b in ranges)


def _movie_queries(title, original, year, imdb):
    queries = []
    if title and year:
        queries.append("%s %s" % (title, year))
    if original and original != title:
        queries.append("%s %s" % (original, year) if year else original)
    if title:
        queries.append(title)
    if imdb:
        queries.append(imdb)
    return queries


def _season_queries(title, original, season):
    s = int(season)
    names = [n for n in (title, original) if n]
    queries = []
    for name in names:
        queries.append("%s S%02d" % (name, s))
        queries.append("%s сезон %s" % (name, s))
    return queries


def _episode_queries(title, original, season, episode):
    s, e = int(season), int(episode)
    names = [n for n in (title, original) if n]
    queries = []
    for name in names:
        queries.append("%s S%02dE%02d" % (name, s, e))
        queries.append("%s сезон %s серия %s" % (name, s, e))
    return queries


def _render_movies(data, page_url_fn, page):
    for movie in data.get("results", []):
        item = _movie_item(movie)
        xbmcplugin.addDirectoryItem(
            HANDLE,
            url_for("movie_torrents", tmdb_id=movie.get("id")),
            item, isFolder=True)
    _maybe_next_page(data, page_url_fn, page)
    xbmcplugin.setContent(HANDLE, "movies")
    _end()


def _render_tv(data, page_url_fn, page):
    for show in data.get("results", []):
        item = _tv_item(show)
        xbmcplugin.addDirectoryItem(
            HANDLE,
            url_for("tv_seasons", tmdb_id=show.get("id")),
            item, isFolder=True)
    _maybe_next_page(data, page_url_fn, page)
    xbmcplugin.setContent(HANDLE, "tvshows")
    _end()


def _movie_item(movie):
    title = movie.get("title") or movie.get("original_title") or ""
    item = xbmcgui.ListItem(title)
    poster = utils.image_url(movie.get("poster_path"))
    item.setArt({
        "poster": poster,
        "thumb": poster,
        "fanart": utils.image_url(movie.get("backdrop_path"), "w780"),
    })
    item.setInfo("video", {
        "title": title,
        "originaltitle": movie.get("original_title") or "",
        "plot": movie.get("overview") or "",
        "year": int((movie.get("release_date") or "0")[:4] or 0),
        "rating": movie.get("vote_average") or 0,
        "mediatype": "movie",
    })
    return item


def _tv_item(show):
    title = show.get("name") or show.get("original_name") or ""
    item = xbmcgui.ListItem(title)
    poster = utils.image_url(show.get("poster_path"))
    item.setArt({
        "poster": poster,
        "thumb": poster,
        "fanart": utils.image_url(show.get("backdrop_path"), "w780"),
    })
    item.setInfo("video", {
        "title": title,
        "originaltitle": show.get("original_name") or "",
        "plot": show.get("overview") or "",
        "year": int((show.get("first_air_date") or "0")[:4] or 0),
        "rating": show.get("vote_average") or 0,
        "mediatype": "tvshow",
    })
    return item


def _render_releases(releases, heading, ctx):
    if not releases:
        utils.notify(L(30030), heading)
        _end()
        return

    p = _params()
    sort = p.get("sort", "seeders")
    qual = p.get("qual", "any")
    rus = p.get("rus", "0")
    kw = p.get("kw", "")

    _filter_header(sort, qual, rus, kw)
    items = _apply_filters(releases, sort, qual, rus, kw)

    if not items:
        _filter_link(L(30181), sort="seeders", qual="any", rus="0", kw="")
        xbmcplugin.setContent(HANDLE, "videos")
        _end()
        return

    for rel in items:
        if not (rel.get("magnet") or rel.get("download_url")):
            continue
        item = xbmcgui.ListItem(_release_label(rel))
        item.setInfo("video", {
            "title": rel["title"],
            "plot": _release_plot(rel),
            "mediatype": "movie",
        })
        item.setProperty("IsPlayable", "true")
        url = url_for("play_release",
                      magnet=rel.get("magnet", ""), url=rel.get("download_url", ""),
                      mt=ctx["mt"], id=ctx["id"], title=ctx["title"],
                      poster=ctx["poster"], s=ctx["s"], e=ctx["e"])
        xbmcplugin.addDirectoryItem(HANDLE, url, item, isFolder=False)

    xbmcplugin.setContent(HANDLE, "videos")
    _end()


_SORTS = ["seeders", "size", "quality"]
_QUALS = ["any", "4K", "1080p", "720p"]


def _cycle(seq, cur):
    try:
        return seq[(seq.index(cur) + 1) % len(seq)]
    except ValueError:
        return seq[0]


def _filter_header(sort, qual, rus, kw):
    _filter_link("⇅ %s: %s" % (L(30170), _sort_name(sort)), sort=_cycle(_SORTS, sort))
    _filter_link("◆ %s: %s" % (L(30151), qual if qual != "any" else L(30175)),
                 qual=_cycle(_QUALS, qual))
    _filter_link("🔊 %s: %s" % (L(30176), L(30177) if rus == "1" else L(30178)),
                 rus="0" if rus == "1" else "1")
    _kw_link("🔎 %s" % (kw if kw else L(30179)))
    if sort != "seeders" or qual != "any" or rus == "1" or kw:
        _filter_link("✖ %s" % L(30180), sort="seeders", qual="any", rus="0", kw="")


def _sort_name(sort):
    return {"seeders": L(30171), "size": L(30172), "quality": L(30173)}.get(sort, sort)


def _filter_link(label, **override):
    p = _params()
    params = {k: v for k, v in p.items() if k not in ("action", "ask_kw")}
    params.update(override)
    params["base_action"] = p.get("action")
    _add_dir(label, url_for("set_filter", **params))


def _kw_link(label):
    p = _params()
    params = {k: v for k, v in p.items() if k not in ("action", "ask_kw")}
    params["base_action"] = p.get("action")
    _add_dir(label, url_for("kw_filter", **params))


def _apply_filters(releases, sort, qual, rus, kw):
    items = list(releases)
    if qual != "any":
        items = [r for r in items if r.get("quality") == qual]
    if rus == "1":
        items = [r for r in items if r.get("has_russian")]
    if kw:
        low = kw.lower()
        items = [r for r in items
                 if low in (r.get("title", "") + " "
                            + " ".join(r.get("voices") or [])).lower()]
    return _sort_releases(items, sort)


def _sort_releases(items, sort):
    if sort == "size":
        return sorted(items, key=lambda r: r.get("size") or 0, reverse=True)
    if sort == "quality":
        rank = {"4K": 4, "1080p": 3, "720p": 2, "SD": 1}
        return sorted(items, key=lambda r: rank.get(r.get("quality"), 0), reverse=True)
    return sorted(items, key=lambda r: r.get("seeders") or 0, reverse=True)


def set_filter():
    p = _params()
    rest = {k: v for k, v in p.items()
            if k not in ("action", "base_action") and v not in ("", None)}
    xbmc.executebuiltin(
        "Container.Update(%s,replace)" % url_for(p.get("base_action"), **rest))


def kw_filter():
    p = _params()
    word = _ask(L(30179))
    rest = {k: v for k, v in p.items()
            if k not in ("action", "base_action", "kw") and v not in ("", None)}
    if word:
        rest["kw"] = word
    xbmc.executebuiltin(
        "Container.Update(%s,replace)" % url_for(p.get("base_action"), **rest))


def play_release():
    p = _params()
    if utils.setting("history_enabled", "true") == "true":
        history.record(p.get("mt"), p.get("id"), p.get("title"),
                       p.get("poster"), p.get("s"), p.get("e"))
    prefer = utils.setting_int("jacktorr_prefer", 0)
    jurl = jacktorr.build_play_url(p.get("magnet"), p.get("url"), prefer)
    xbmcplugin.setResolvedUrl(HANDLE, bool(jurl), xbmcgui.ListItem(path=jurl or ""))


def history_list():
    for it in history.items():
        poster = utils.image_url(it.get("poster"))
        item = xbmcgui.ListItem(_history_label(it))
        item.setArt({"poster": poster, "thumb": poster})
        item.setInfo("video", {
            "title": it.get("title", ""),
            "mediatype": "movie" if it.get("mt") == "movie" else "tvshow",
        })
        item.addContextMenuItems([
            (L(30191), "RunPlugin(%s)"
             % url_for("history_remove", mt=it.get("mt"), id=it.get("id"))),
            (L(30192), "RunPlugin(%s)" % url_for("history_clear")),
        ])
        if it.get("mt") == "movie":
            target = url_for("movie_torrents", tmdb_id=it.get("id"))
        else:
            target = url_for("tv_episodes", tmdb_id=it.get("id"),
                             season=it.get("s") or "1")
        xbmcplugin.addDirectoryItem(HANDLE, target, item, isFolder=True)
    xbmcplugin.setContent(HANDLE, "movies")
    _end()


def _history_label(it):
    if it.get("mt") == "movie":
        return it.get("title", "")
    return "%s · %s" % (it.get("title", ""), L(30022) % (it.get("s") or "1"))


def history_remove():
    p = _params()
    history.remove(p.get("mt"), p.get("id"))
    xbmc.executebuiltin("Container.Refresh")


def history_clear():
    history.clear()
    xbmc.executebuiltin("Container.Refresh")


def _release_label(rel):
    parts = []
    voices = rel.get("voices") or []
    if voices:
        parts.append(", ".join(voices[:2]))
    elif rel["has_russian"]:
        parts.append("RUS")
    if rel["quality"]:
        parts.append(rel["quality"])
    size = prowlarr.human_size(rel["size"])
    if size:
        parts.append(size)
    parts.append(L(30040) % rel["seeders"])
    if rel["indexer"]:
        parts.append(rel["indexer"])
    head = " · ".join(parts)
    return "%s | %s" % (head, rel["title"]) if head else rel["title"]


def _release_plot(rel):
    lines = []
    voices = rel.get("voices") or []
    if voices:
        lines.append("%s: %s" % (L(30150), ", ".join(voices)))
    if rel["quality"]:
        lines.append("%s: %s" % (L(30151), rel["quality"]))
    size = prowlarr.human_size(rel["size"])
    if size:
        lines.append("%s: %s" % (L(30152), size))
    lines.append("%s: %s / %s" % (L(30153), rel["seeders"], rel.get("leechers", 0)))
    if rel["indexer"]:
        lines.append("%s: %s" % (L(30154), rel["indexer"]))
    lines.append("")
    lines.append(rel["title"])
    return "\n".join(lines)


def _add_dir(label, url):
    item = xbmcgui.ListItem(label)
    xbmcplugin.addDirectoryItem(HANDLE, url, item, isFolder=True)


def _maybe_next_page(data, page_url_fn, page):
    if page_url_fn is None:
        return
    total = data.get("total_pages") or 1
    if page < total:
        _add_dir(L(30020), page_url_fn(page + 1))


def _ask(heading):
    keyboard = xbmcgui.Dialog().input(heading)
    return keyboard.strip() if keyboard else ""


def _end():
    xbmcplugin.endOfDirectory(HANDLE)


ACTIONS = {
    "movies_root": movies_root,
    "tv_root": tv_root,
    "movie_list": movie_list,
    "movie_genres": movie_genres,
    "movie_by_genre": movie_by_genre,
    "search_movies": search_movies,
    "tv_list": tv_list,
    "tv_genres": tv_genres,
    "tv_by_genre": tv_by_genre,
    "search_tv": search_tv,
    "tv_seasons": tv_seasons,
    "tv_episodes": tv_episodes,
    "movie_torrents": movie_torrents,
    "season_torrents": season_torrents,
    "episode_torrents": episode_torrents,
    "not_aired": not_aired,
    "set_filter": set_filter,
    "kw_filter": kw_filter,
    "play_release": play_release,
    "history_list": history_list,
    "history_remove": history_remove,
    "history_clear": history_clear,
}


def run():
    action = _params().get("action")
    ACTIONS.get(action, index)()
