# Changelog

## 0.1.0
- Release list for an episode is filtered to those that actually contain the
  selected episode (packs `1-4`, `1-2` no longer show up for episode 5).
- Sorting and filters in the release list: seeders/size/quality, quality
  (4K/1080p/720p), Russian only, search by word (for example "Сыендук"), reset.
- "Continue watching" and local history (recorded when a release starts,
  remove/clear from the menu, toggle in settings).
- Episode air status: unaired episodes are marked, do not start a search,
  and show the air date.
- Images: w342 posters, poster in thumb, fallback art for episodes/seasons
  without a still.
- Network layer retries; configurable base URLs for the TMDb API and images.
- Optional HTTP proxy for addon requests (with login/password support).
- Russian/English localization, strings moved to strings.po.
- JacRed search source (a public RU tracker aggregator, like in Lampa), source
  switch, voice/dub info, release details in the info panel.
- TMDb catalog of movies and TV shows (with localized metadata), search via
  Prowlarr/JacRed, native release list, playback via Jacktorr, settings.
