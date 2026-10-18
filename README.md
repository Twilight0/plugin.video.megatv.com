# MEGA Player addon for Kodi

MEGA live and on-demand broadcasts for Kodi — https://www.megatv.com

> This addon is not published nor endorsed by megatv.com. It offers content
> available in Greece.

## Features

- **Live stream** — the MEGA live broadcast, resolved through the Vindral
  edge network (see [Playback](#playback)).
- **TV shows by section** — Series, Entertainment, News, Sports, Mega Kids,
  Documentaries, Flashback and Pemptousia+, scraped from the site's own
  section pages.
- **Collections** — Mega Classics and Archive tags, Season 2025-2026, Comedy
  and Drama playlists, Golden Classics short videos and the MegaNews hub.
- **Latest** — the most recent videos across the site, newest first with
  page navigation.
- **Search** — show and episode search through the site's WordPress REST
  API, with persistent search history.
- **Programme guide** — the full `/tv-program/` schedule in a dialog with a
  day strip, per-day rows and a now-airing highlight; activating a row
  plays the live stream or opens the show.
- **Bookmarks** — save any listing for quick access.
- **"Show − Episode" titles** — episode pages name their parent show, so
  date-titled entries (e.g. bulletins) always read clearly.
- **Trailer fallback** — shows with no published episodes (e.g. older
  classics like *Το Νησί*) offer the show trailer instead of an empty list.
- **Complete archives** — long shows walk the site's episode pagination,
  so all episodes list (e.g. all 139 of *Εμείς κι Εμείς*), fetched
  concurrently for fast loading.
- Listing niceties shared with the STAR / SKAI / Alpha players: page
  indicator overlay (configurable position), jump-to-page dialog and
  function-cache clearing from settings or the context menu.

## Requirements

- Kodi 20+ (Nexus) with Python 3
- `script.module.tulip` ≥ 4.1.5
- `script.module.urldispatcher` 1.1.0
- `script.module.netclient` 1.2.0
- `script.module.unicache` 1.0.1
- `script.module.resolveurl` ≥ 5.1.210
- `script.module.resolveurl.pluginsgr` ≥ 0.3.2 (provides the MegaTV
  resolver; 0.3.9+ covers every video URL shape the site serves)
- `inputstream.adaptive` (optional, for HLS/DASH VOD)

## Installation

> The addon has not been published to a repository yet. Until it is,
> install it manually:

1. Download or clone this repository and zip the
   `plugin.video.megatv.com` folder (the zip must contain `addon.xml`
   at its root).
2. In Kodi go to **Add-ons → Install from zip file** and select the zip.
3. Kodi resolves the dependencies automatically; make sure the
   **Twilight0 Libs** modules (tulip, PluginsGR, …) are installed.

## Usage

Open **MEGA Player** from Video add-ons:

- **Live stream** starts playback immediately.
- **TV shows** → pick a section → pick a show → pick an episode.
- **Collections** → Mega Classics, Archive, Season 2025-2026, Comedy,
  Drama playlists, Golden Classics or MegaNews.
- **Programme** opens the schedule dialog: choose a day, then a show.
  The highlighted (now-airing) row plays the live stream.
- **Search** → **New search**; past queries are kept and can be removed
  individually or all at once.
- Context menu on any entry: add to **Bookmarks**, clear the function
  cache, or jump to a page in long listings.

## Playback

Stream resolution is delegated to ResolveURL using the MegaTV resolver
from PluginsGR:

- On-demand episodes resolve through their `data-kwik_source` HLS
  manifest and play via `inputstream.adaptive`.
- The live stream runs over Vindral: the resolver reads the channel id
  from the live player, asks the Vindral load balancer for an edge, and
  returns a localhost FLV proxy URL (served by PluginsGR's bundled
  `moq_proxy`, no extra addon required), which Kodi plays directly.

## Development

Scrapers live in `resources/lib/api.py` (pure HTML/REST parsing, no Kodi
imports needed for listing logic), navigation in `resources/lib/navigator.py`
and resolution handoff in `resources/lib/player.py`. The stack mirrors the
sibling STAR / SKAI / Alpha players.

## License

This software is released under the [GPL 3.0 license][1].

[1]: http://www.gnu.org/licenses/gpl-3.0.html

## Credits

- Main artwork (MEGA logo) from the official MEGA TV app.
- Kids artwork from https://www.megatv.com/showtype/paidika/
- Menu icons drawn for this addon; programme dialog adapted from the
  STAR Player layout.
