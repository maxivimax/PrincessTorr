from . import cache, utils

CATALOG_TTL = 6 * 60 * 60
DETAIL_TTL = 24 * 60 * 60


def _auth():
    bearer = utils.setting("tmdb_bearer")
    if bearer:
        return {"Authorization": "Bearer %s" % bearer}, {}
    return {}, {"api_key": utils.setting("tmdb_api_key")}


def _lang():
    return utils.setting("tmdb_lang", "ru-RU")


def _get(path, params=None, ttl=CATALOG_TTL):
    headers, auth_params = _auth()
    merged = {"language": _lang()}
    merged.update(auth_params)
    if params:
        merged.update(params)
    url = "%s%s?%s" % (utils.tmdb_api_base(), path, utils.build_query(merged))

    cache_key = "tmdb:" + url
    cached = cache.get(cache_key, ttl)
    if cached is not None:
        return cached

    data = utils.http_get_json(url, headers=headers)
    if data is not None:
        cache.set(cache_key, data)
    return data


def movies_list(kind, page=1):
    return _get("/movie/%s" % kind, {"page": page})


def movie_genres():
    return _get("/genre/movie/list")


def movies_by_genre(genre_id, page=1):
    return _get(
        "/discover/movie",
        {"with_genres": genre_id, "sort_by": "popularity.desc", "page": page},
    )


def search_movies(query, page=1):
    return _get(
        "/search/movie",
        {"query": query, "include_adult": "false", "page": page},
    )


def movie_details(movie_id):
    return _get(
        "/movie/%s" % movie_id,
        {"append_to_response": "external_ids,credits,release_dates"},
        ttl=DETAIL_TTL,
    )


def tv_list(kind, page=1):
    return _get("/tv/%s" % kind, {"page": page})


def tv_genres():
    return _get("/genre/tv/list")


def tv_by_genre(genre_id, page=1):
    return _get(
        "/discover/tv",
        {"with_genres": genre_id, "sort_by": "popularity.desc", "page": page},
    )


def search_tv(query, page=1):
    return _get("/search/tv", {"query": query, "page": page})


def tv_details(tv_id):
    return _get(
        "/tv/%s" % tv_id,
        {"append_to_response": "external_ids,credits"},
        ttl=DETAIL_TTL,
    )


def season_details(tv_id, season_number):
    return _get(
        "/tv/%s/season/%s" % (tv_id, season_number),
        ttl=DETAIL_TTL,
    )
