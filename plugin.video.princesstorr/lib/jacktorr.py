import urllib.parse

JACKTORR_ID = "plugin.video.jacktorr"

PREFER_AUTO = 0
PREFER_MAGNET = 1
PREFER_URL = 2


def build_play_url(magnet, download_url, prefer=PREFER_AUTO):
    if prefer == PREFER_MAGNET:
        return _magnet_url(magnet)
    if prefer == PREFER_URL:
        return _url_url(download_url)

    return _magnet_url(magnet) or _url_url(download_url)


def _magnet_url(magnet):
    if not magnet:
        return None
    return "plugin://%s/play_magnet?magnet=%s" % (
        JACKTORR_ID,
        urllib.parse.quote(magnet, safe=""),
    )


def _url_url(download_url):
    if not download_url:
        return None
    return "plugin://%s/play_url?url=%s" % (
        JACKTORR_ID,
        urllib.parse.quote(download_url, safe=""),
    )
