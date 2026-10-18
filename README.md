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

## Compatibility & Requirements

Tested on Kodi 20 (Nexus) and 21 (Omega), all platforms Kodi supports.

The addon leverages lightweight modular dependencies hosted on the
Twilight0 repositories:

- `script.module.tulip` (4.1.5+) — modern Kodi Python framework.
- `script.module.urldispatcher` — URL routing.
- `script.module.netclient` — HTTP requests and session management.
- `script.module.unicache` — disk and memory caching layer.
- `script.module.resolveurl` (5.1.210+) — primary video host resolvers.
- `script.module.resolveurl.pluginsgr` (0.3.2+, 0.3.9 recommended) —
  dedicated resolvers for official Greek broadcast portals, including
  the MegaTV resolver this addon plays through.
- `inputstream.adaptive` (Kodi built-in binary addon, optional) —
  required for HLS/DASH adaptive VOD playback.

## Installation

### Method 1: Via Twilight0 Repository (Recommended)

Installing via the repository ensures all dependencies, resolvers, and
future updates are installed automatically:

1. In Kodi, navigate to **Settings** (gear icon) → **File Manager** →
   **Add source**.
2. Select `<None>` and enter the following URL:
   ```text
   https://twilight0.github.io/repository.twilight0/
   ```
3. Enter a name for the media source (e.g. `Twilight0 Repo`) and click
   **OK**.
4. Go back to Kodi's home screen, click **Add-ons** → **Add-on browser**
   (open box icon at top left).
5. Select **Install from zip file** (enable *Unknown sources* in Kodi
   settings if prompted).
6. Select `Twilight0 Repo` and click `repository.twilight0-2.0.zip`.
7. Once the repository is installed, select **Install from repository**
   → **Twilight0 Repository** → **Video add-ons** → **MEGA Player** →
   **Install**.

### Method 2: Direct Zip Download

You can also download the repository ZIP file directly:

- Repository ZIP: [repository.twilight0.zip](https://raw.githubusercontent.com/Twilight0/repository.twilight0/gh-pages/repository.twilight0.zip)

After downloading, in Kodi go to **Add-ons** → **Add-on browser** →
**Install from zip file** and select the downloaded file, then continue
from step 7 of Method 1 above.

## Recommended configuration

For the best streaming experience:

1. Ensure **InputStream Adaptive** is enabled:
   - Kodi **Settings** → **Add-ons** → **My add-ons** →
     **VideoPlayer InputStream** → **InputStream Adaptive** → **Enable**.
2. In MEGA Player settings you can adjust the page indicator overlay
   position and margins used in long listings.

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

## Bug reporting

File issues at [Twilight0/plugin.video.megatv.com](https://github.com/Twilight0/plugin.video.megatv.com/issues).

> Disclaimer: the author does not host, stream, or distribute any of the
> media content displayed within this software. All streams and on-demand
> links are parsed from publicly available domains on the internet. This
> addon acts strictly as a directory and search client.

## License

This software is released under the [GPL 3.0 license][1].

[1]: http://www.gnu.org/licenses/gpl-3.0.html

## Credits

- Main artwork (MEGA logo) from the official MEGA TV app.
- Kids artwork from https://www.megatv.com/showtype/paidika/
- Menu icons drawn for this addon; programme dialog adapted from the
  STAR Player layout.
