import json
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

import xbmc
import xbmcaddon
import xbmcvfs

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_NAME = ADDON.getAddonInfo("name")

TMDB_API = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p"


def setting(key, default=""):
    value = ADDON.getSetting(key)
    return value if value != "" else default


def setting_int(key, default=0):
    try:
        return int(ADDON.getSetting(key))
    except (ValueError, TypeError):
        return default


def profile_dir():
    path = xbmcvfs.translatePath("special://profile/addon_data/%s/" % ADDON_ID)
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdirs(path)
    return path


def log(message, level=xbmc.LOGINFO):
    xbmc.log("[%s] %s" % (ADDON_ID, message), level)


def notify(message, heading=None):
    import xbmcgui
    xbmcgui.Dialog().notification(heading or ADDON_NAME, message)


def localize(string_id):
    return ADDON.getLocalizedString(string_id)


def _opener():
    proxy = setting("proxy_url")
    if not proxy:
        return urllib.request.build_opener()
    if "://" not in proxy:
        proxy = "http://" + proxy
    handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
    return urllib.request.build_opener(handler)


HTTP_RETRIES = 5
HTTP_RETRY_BACKOFF = 0.4

_RETRYABLE = (urllib.error.URLError, ssl.SSLError, socket.timeout, TimeoutError, ConnectionError)


def http_get_json(url, headers=None, timeout=15):
    req = urllib.request.Request(url, headers=headers or {})
    last = None
    for attempt in range(1, HTTP_RETRIES + 1):
        try:
            with _opener().open(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            log("HTTP %s для %s" % (exc.code, url), xbmc.LOGERROR)
            return None
        except ValueError as exc:
            log("Невалидный JSON от %s: %s" % (url, exc), xbmc.LOGERROR)
            return None
        except _RETRYABLE as exc:
            last = exc
            log("Попытка %d/%d не удалась для %s: %s"
                % (attempt, HTTP_RETRIES, url, exc))
            if attempt < HTTP_RETRIES:
                time.sleep(HTTP_RETRY_BACKOFF * attempt)
    log("Все попытки исчерпаны для %s: %s" % (url, last), xbmc.LOGERROR)
    return None


def build_query(params):
    pairs = []
    for key, value in params.items():
        if value is None or value == "":
            continue
        if isinstance(value, (list, tuple)):
            for item in value:
                pairs.append((key, str(item)))
        else:
            pairs.append((key, str(value)))
    return urllib.parse.urlencode(pairs)


def tmdb_api_base():
    return setting("tmdb_api_base", TMDB_API).rstrip("/")


def tmdb_image_base():
    return setting("tmdb_image_base", TMDB_IMG).rstrip("/")


def image_url(path, size="w342"):
    if not path:
        return ""
    return "%s/%s%s" % (tmdb_image_base(), size, path)
