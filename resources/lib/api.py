# -*- coding: utf-8 -*-

'''
    MEGA Player Addon
    Author Twilight0

    SPDX-License-Identifier: GPL-3.0-only
    See LICENCES/GPL-3.0-only for more information.
'''

import re
import time
from html import unescape
from urllib.parse import quote

from . import constants as c

try:
    from netclient import Net

    _net = Net()
except ImportError:  # pragma: no cover - only when run outside Kodi
    _net = None


USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')

TAG_RE = re.compile(r'<[^>]+>')
WS_RE = re.compile(r'\s+')


# ---------------------------------------------------------------------------
# HTTP plumbing
# ---------------------------------------------------------------------------

def fetch(url, timeout=30, retries=2):

    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
    }

    for attempt in range(retries + 1):

        try:
            if _net is not None:
                response = _net.http_GET(url, headers=headers, timeout=timeout)
                # netclient falls back to ascii when a response carries no
                # charset, which mangles the Greek titles, so always decode
                # the raw bytes.
                return response.nodecode(True).content.decode('utf-8', 'replace')

            import urllib.request

            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode('utf-8', 'replace')

        except Exception as error:
            if not _throttled(error) or attempt == retries:
                raise

            time.sleep(3 * (attempt + 1))


def _throttled(error):
    """True for the HTTP 429 the site answers bursts with."""

    return getattr(error, 'code', None) == 429 or '429' in str(error)


def _clean(value):
    """Unescapes entities and flattens the whitespace of a scraped string."""

    if not value:
        return ''

    return WS_RE.sub(' ', unescape(value)).strip()


def _abs(url):
    """Makes a site-relative path absolute."""

    if not url:
        return ''

    url = unescape(url)

    if url.startswith('//'):
        return 'https:' + url

    if url.startswith('/'):
        return c.BASE + quote(url)

    return url


def _humanize(slug):
    """Turns a url slug into a readable title when no better one exists."""

    slug = unquote_slug(slug)

    return _clean(slug.replace('-', ' ')).capitalize()


def unquote_slug(slug):

    from urllib.parse import unquote

    try:
        return unquote(slug)
    except Exception:
        return slug


# ---------------------------------------------------------------------------
# Cards
#
# Shows render as <article class="card card--show ..."> with a stretched
# /ekpompes/<id>/<slug>/ link, an <img data-src> poster and an
# <h3 class="card__title"><a> title.
# Episodes render as <article class="card card--video ..."> with a playable
# link (tv/etv/gtv/ftv/fltv/ktvshows, megasports or goldenclassics), a lazy
# <img data-src> thumb and an <h3 class="card__title card__title--sm"><a>
# title. Several episode flavors carry no numeric id (/fltvshows/<slug>/,
# /megasports/<slug>/, /goldenclassics/<slug>/).
# ---------------------------------------------------------------------------

def _cards(html, kind):
    """
    Parses show or video cards, shared by section pages (shows), show pages
    (episodes) and the /shows/ page (latest videos). Video listings also
    come as card--news (the /episodes/ pages use that variant with a div
    instead of an h3 title).
    """

    cards = []
    seen = set()

    if kind == 'show':
        parts = re.split(r'<article class="card card--show', html)
    else:
        parts = re.split(r'<article class="card card--(?:video|news)', html)

    for chunk in parts[1:]:

        window = chunk[:6000]

        if kind == 'show':
            link = re.search(r'href="(https://www\.megatv\.com/ekpompes/\d+/[\w\-/]+?/)"', window)
        else:
            link = re.search(
                r'href="(https://www\.megatv\.com/(?:[a-z]*tvshows|megasports|goldenclassics)/[^"]+?/)"',
                window
            )

        if not link:
            continue

        url = link.group(1).rstrip('/')

        if url in seen:
            continue

        seen.add(url)

        title = re.search(
            r'<(?:h3|div) class="card__title[^"]*">\s*<a[^>]*>(.*?)</a>', window, re.S
        )
        image = re.search(r'data-src="([^"]+)"', window) or \
            re.search(r'<img[^>]*src="(https?://[^"]+)"', window)
        alt = re.search(r'alt="([^"]*)"', window)

        if title:
            title = _clean(TAG_RE.sub('', title.group(1)))
        elif alt and alt.group(1).strip():
            title = _clean(alt.group(1))
        else:
            title = _humanize(url.rstrip('/').rsplit('/', 1)[-1])

        cards.append({
            'title': title,
            'url': url,
            'image': _abs(image.group(1)) if image else '',
        })

    return cards


# ---------------------------------------------------------------------------
# Show catalogue (/showtype/<slug>/ sections and shows)
# ---------------------------------------------------------------------------

def shows_of(showtype):
    """Returns [{'title', 'url', 'image'}] for one /showtype/ section."""

    html = fetch('{0}/showtype/{1}/'.format(c.BASE, showtype))

    return _cards(html, 'show')


# ---------------------------------------------------------------------------
# Show episodes (/ekpompes/<id>/<slug>/ pages)
#
# A show page lists its episodes as card--video links; the episode pages
# resolve through PluginsGR (data-kwik_source m3u8).
# ---------------------------------------------------------------------------

def episodes_of(show_url):
    """
    Returns [{'title', 'url', 'image'}] for one show page, newest first.

    Long-running shows keep only the newest ~24 episodes inline and link
    the rest through a "Περισσότερα" button to /episodes/?id=<CODE>&type=
    <cpt>, whose pages (/episodes/page/N/...) are walked until the next
    button goes disabled.
    """

    html = fetch(show_url.rstrip('/') + '/')
    entries = _cards(html, 'video')
    seen = set(entry['url'] for entry in entries)

    more = re.search(
        r'/episodes/?\?id=([A-Z0-9]+)&type=([a-z]+)',
        unescape(html))

    if more:
        code, cpt = more.group(1), more.group(2)
        entries.extend(_walk_episodes(code, cpt, seen))

    return entries


EPISODES_PAGE_SIZE = 24
EPISODES_MAX_PAGES = 25


def _walk_episodes(code, cpt, seen):
    """Follows the /episodes/ pagination for one series code."""

    extra = []
    page = 1

    while page <= EPISODES_MAX_PAGES:
        if page == 1:
            url = '{0}/episodes/?id={1}&type={2}'.format(c.BASE, code, cpt)
        else:
            url = '{0}/episodes/page/{1}/?id={2}&type={3}'.format(c.BASE, page, code, cpt)

        try:
            html = fetch(url)
        except Exception:
            break

        for entry in _cards(html, 'video'):
            if entry['url'] not in seen:
                seen.add(entry['url'])
                extra.append(entry)

        if not _has_next_episodes(html):
            break

        page += 1

    return extra


def _has_next_episodes(html):
    """True while the /episodes/ next button is still enabled."""

    match = re.search(
        r"<a href='[^']+/episodes/page/\d+/\?[^']*'[^>]*class='([^']*btn--next[^']*)'",
        html)

    return bool(match) and 'disabled' not in match.group(1)


def latest():
    """Returns [{'title', 'url', 'image'}] with the most recent videos."""

    html = fetch(c.SHOWS_PAGE)

    return _cards(html, 'video')


# ---------------------------------------------------------------------------
# Collections (/shows/ page links: tags, playlists, golden classics, meganews)
#
# Tag and playlist pages reuse the show card markup; the golden classics
# page lists directly playable videos instead of shows; meganews mixes
# both, so it returns (shows, videos).
# ---------------------------------------------------------------------------

def tag_shows(url):
    """Returns [{'title', 'url', 'image'}] for one tag/playlist listing url."""

    html = fetch(url)

    return _cards(html, 'show')


def golden_classics():
    """Returns [{'title', 'url', 'image'}] with the golden classics videos."""

    html = fetch(c.GOLDEN_CLASSICS_PAGE)

    return _cards(html, 'video')


def meganews():
    """Returns (shows, videos) from the meganews hub page."""

    html = fetch(c.MEGANEWS_PAGE)

    return _cards(html, 'show'), _cards(html, 'video')


def episode_details(url):
    """
    Reads one episode page into an enriched dict. Entries with no playable
    marker report playable False so listings can drop them.
    """

    try:
        html = fetch(url.rstrip('/') + '/')
    except Exception:
        return None

    playable = bool(re.search(r'data-kwik_source="[^"]+?\.m3u8"', html))

    meta = _video_meta_from_html(html, url)
    meta['playable'] = playable

    return meta


def _video_meta_from_html(html, url):
    """Builds a listing dict from already-fetched page html (og: metatags)."""

    title = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    image = re.search(r'<meta property="og:image"\s*content="([^"]+)"', html)
    plot = re.search(r'<meta property="og:description" content="([^"]+)"', html) or \
        re.search(r'<meta name="description" content="([^"]+)"', html)
    # Episode pages name the parent show the way listings should quote it:
    #   <h1 class="article__title">SHOW</h1>
    #   <div class="article__subtitle"><span class="episode__no">EPISODE</span>
    show = re.search(r'<h1 class="article__title[^"]*">(.*?)</h1>', html, re.S)

    slug = url.rstrip('/').rsplit('/', 1)[-1]

    if title:
        title = _clean(title.group(1))
        # Strip only the site suffix, pipes inside real titles are kept.
        title = re.sub(r'\s*\|\s*MEGA(\s*TV)?\s*$', '', title).strip()
        if title.lower() in ('mega tv', 'mega'):
            title = ''
    else:
        title = ''

    return {
        'title': title or _humanize(slug),
        'url': url.rstrip('/'),
        'image': _abs(image.group(1)) if image else '',
        'plot': _clean(plot.group(1)) if plot else '',
        'show': _clean(TAG_RE.sub('', show.group(1))) if show else '',
    }


def _rest(path, params):
    """GETs one WP REST collection and returns the decoded JSON list."""

    import json as _json

    query = '&'.join('{0}={1}'.format(k, quote(str(v))) for k, v in params.items())
    body = fetch('{0}{1}?{2}'.format(c.REST_BASE, path, query))

    try:
        data = _json.loads(body)
    except Exception:
        return []

    return data if isinstance(data, list) else []


def _rest_item(item, kind):
    """Normalizes one WP REST post into a listing dict."""

    title = item.get('title') or {}
    title = _clean(TAG_RE.sub('', title.get('rendered', '')))

    if not title:
        return None

    url = (item.get('link') or '').rstrip('/')

    # Episode links carry a playable path segment (tvshows flavors,
    # megasports, goldenclassics); show links carry /ekpompes/.
    if '/ekpompes/' not in url and \
            not re.search(r'/([a-z]*tvshows|megasports|goldenclassics)/', url):
        return None

    image = ''
    try:
        media = (item.get('_embedded') or {}).get('wp:featuredmedia') or []
        if media:
            image = media[0].get('source_url', '')
    except Exception:
        image = ''

    return {'title': title, 'url': url, 'image': _abs(image), 'kind': kind}


def _rest_search(cpt, query, kind):
    """Searches one post type, returning normalized listing dicts."""

    try:
        items = _rest('/{0}'.format(cpt), {
            'search': query, 'per_page': 20, '_embed': 1,
        })
    except Exception:
        return []

    out = []

    for item in items:
        entry = _rest_item(item, kind)

        if entry:
            out.append(entry)

    return out


def search(query):
    """
    Searches the site's WordPress REST API. The plain ?s= search page is
    served from a cache that ignores the query string for anonymous
    requests, so the addon queries the ekpompes (shows) post type plus
    every episode post type directly. Returns (shows, episodes).
    """

    from concurrent.futures import ThreadPoolExecutor, as_completed

    query = (query or '').strip()

    if not query:
        return [], []

    shows, episodes = [], []
    seen = set()

    with ThreadPoolExecutor(max_workers=7) as pool:
        futures = {'show:{0}'.format(c.SHOW_CPT): pool.submit(
            _rest_search, c.SHOW_CPT, query, 'show')}
        futures.update({
            'ep:{0}'.format(cpt): pool.submit(_rest_search, cpt, query, 'episode')
            for cpt in c.EPISODE_CPTS
        })

        for key, future in futures.items():
            try:
                entries = future.result()
            except Exception:
                continue

            for entry in entries:
                if entry['url'] in seen:
                    continue

                seen.add(entry['url'])

                if key.startswith('show:'):
                    shows.append(entry)
                else:
                    episodes.append(entry)

    return shows, episodes


# ---------------------------------------------------------------------------
# Programme (/tv-program/)
#
# The day strip renders every day as
#   <a data-target="date_N" ...><span class="program__day">DAY</span>
#   <span class="program__date">DD/MM</span></a>
# and each day's schedule lives in <section id="date_N"> whose rows look
# like:
#   <div class="card card--program [past|now-playing]">
#     <span class="time">HH:MM</span> ... <a href="/ekpompes/...">TITLE</a>
#     <img data-src="thumb">
# ---------------------------------------------------------------------------

def programma_dates():
    """Returns [{'label', 'date', 'today'}] for every day in the strip."""

    html = fetch(c.TV_PROGRAM_PAGE)

    dates = []

    for match in re.finditer(
            r'<a[^>]*data-target="(date_\d+)"[^>]*>(.*?)</a>', html, re.S):
        body = match.group(2)
        day = re.search(r'<span class="program__day">(.*?)</span>', body, re.S)
        date = re.search(r'<span class="program__date">(.*?)</span>', body, re.S)

        if not day or not date:
            continue

        label = '{0} {1}'.format(_clean(day.group(1)), _clean(date.group(1)))

        dates.append({
            'label': label,
            'date': match.group(1),
            'today': 'active' in match.group(0),
        })

    return dates


def programma_rows(date=None):
    """Returns [{'time', 'now', 'title', 'url', 'image'}] for one day."""

    html = fetch(c.TV_PROGRAM_PAGE)

    if date:
        section = re.search(
            r'<section id="{0}"(.*?)</section>'.format(re.escape(date)), html, re.S)
        html = section.group(1) if section else ''

    rows = []

    for chunk in re.split(r'<div class="card card--program', html)[1:]:
        window = chunk[:4000]

        time_match = re.search(r'<span class="time">(.*?)</span>', window, re.S)
        # The card carries several /ekpompes/ links (poster, title,
        # "more" button); the title lives in .card__title.
        link = re.search(
            r'<div class="card__title">\s*<a href="(https://www\.megatv\.com/ekpompes/[^"]+)"[^>]*>(.*?)</a>',
            window, re.S)
        image = re.search(r'data-src="([^"]+)"', window)

        if not time_match or not link:
            continue

        rows.append({
            'time': _clean(time_match.group(1)),
            'now': 'now-playing' in chunk[:30],
            'title': _clean(TAG_RE.sub('', link.group(2))),
            'url': link.group(1).rstrip('/'),
            'image': _abs(image.group(1)) if image else '',
        })

    return rows
