# Changelog

## 0.1.2
- The addon is now distributed through the PrincessTorr Kodi repository: install
  the repository once and Kodi keeps the addon up to date automatically.

## 0.1.1
- JacRed movie search now queries both the localized and the original title and
  merges the results (fixes cases like "Awareness"/"Осознание" where most
  releases live under a different Russian title than TMDb returns); the same
  dual-title search is used for TV releases.
- JacRed results are filtered by the selected film's year (exact year, falling
  back to +-1), so same-named films from other years no longer pollute the list.
- "Russian only" filter for JacRed now detects Russian audio from the release
  title (ЛМ/MVO/DVO/dubbing/"от <author>", etc.), not just the often-empty
  `voices` field; subtitle-only releases ("СТ"/"Субтитры") stay excluded.
- Sort/quality/Russian/keyword/reset controls in the release list update the
  list in place (`endOfDirectory(updateListing=True)`) instead of opening a new
  page, so toggling filters no longer piles up navigation history.
- Removed emoji from the release-list filter rows: supplementary-plane glyphs
  (🔊/🔎) broke the label in the Kodi skin font, leaving rows visually empty;
  the rows now show plain text.
- Default list view per skin. Switch a movie/TV list to the view you want with
  the skin's own menu, then pick "Set as default view" from the item context
  menu — the addon remembers the skin's view id and reapplies it for movie and
  TV lists (and history). View ids are stored in settings and editable there.

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
