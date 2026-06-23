<div align="center">

# PrincessTorr

🇺🇸 English | [🇷🇺 Русский](README.ru.md)

*Kodi addon: a TMDb catalog of movies and TV shows, on demand torrent search and playback via Jacktorr/TorrServer. Native UI, the look is driven by your installed skin.*

[![Kodi Version](https://img.shields.io/badge/Kodi-21+-blue.svg)](https://kodi.tv)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---
</div>

## Features

- TMDb catalog with localized metadata (Russian by default): movies, TV shows, genres, search.
- On demand torrent search, source JacRed (a public RU tracker aggregator, like in Lampa) or Prowlarr.
- Voice/dub shown right in the release line, plus quality, size, seeders.
- List sorting and filters: seeders/size/quality, Russian only, search by word.
- Episode air status: unaired episodes are marked and show the air date.
- Continue watching and local history.
- Playback via Jacktorr. Search runs only when you open a movie or episode, so the catalog opens fast.

## Install

1. Copy the `plugin.video.princesstorr` folder into the Kodi addons directory
   (`~/.kodi/addons/` on Linux, `%APPDATA%\Kodi\addons\` on Windows), or use the built zip via "Install from zip file".
2. Start Kodi, the addon appears under "Video add-ons".
3. Install and configure [`plugin.video.jacktorr`](https://github.com/Sam-Max/plugin.video.jacktorr) for your TorrServer.

## Configuration

Addon settings:

- TMDb: [API key (v3 or v4 Bearer)](https://www.themoviedb.org/settings/api), metadata language.
- Search source: JacRed (default) or Prowlarr with address and key.
- Network: HTTP proxy if needed.

If TMDb is blocked at the DNS level, a clean DNS on the device helps (for example Quad9 via Private DNS).

## Menu structure

```
Movies: Popular / Now playing / Upcoming / By genre / Search
TV Shows: Popular / On the air / By genre / Search
```

Opening a movie starts the torrent search. TV show goes seasons, episodes; a season has a context action "Find torrents for the whole season".

## Dependencies

Python standard library only (urllib). No external modules.

## Author

Telegram [@iamprincessshine](https://t.me/iamprincessshine)
