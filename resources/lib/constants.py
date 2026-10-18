# -*- coding: utf-8 -*-

'''
    MEGA Player Addon
    Author Twilight0

    SPDX-License-Identifier: GPL-3.0-only
    See LICENCES/GPL-3.0-only for more information.
'''

BASE = 'https://www.megatv.com'

LIVE_PAGE = BASE + '/live/'

SHOWS_PAGE = BASE + '/shows/'
TV_PROGRAM_PAGE = BASE + '/tv-program/'

REST_BASE = BASE + '/wp-json/wp/v2'

# Show post type plus every episode post type, in the site's own naming:
# tvshows = series, etvshows = news, gtvshows = entertainment,
# ftvshows = foreign series, fltvshows = flashback, ktvshows = mega kids,
# megasports and goldenclassics carry their videos slug-only (no numeric id).
SHOW_CPT = 'ekpompes'
EPISODE_CPTS = (
    'tvshows', 'etvshows', 'gtvshows', 'ftvshows', 'fltvshows', 'ktvshows', 'megasports', 'goldenclassics'
)



# The show sections rendered on https://www.megatv.com/shows/ and their own
# /showtype/<slug>/ pages. Label ids live in the addon strings.
SHOWTYPES = (
    ('greekseries', 30002),
    ('entertainment', 30016),
    ('news', 30010),
    ('megasports', 30011),
    ('paidika', 30012),
    ('ntokimanter', 30013),
    ('flashback', 30015),
    ('pemptousia', 30017),
)

# Curated collections from the /shows/ page: tag and playlist listings that
# reuse the same card markup. Each entry is (key, label id, listing url).
TAG_SECTIONS = (
    ('megaclassics', 30018, BASE + '/tag/megaclassics/'),
    ('archive', 30019, BASE + '/tag/archive/?stID=10'),
    ('sezon-2025-2026', 30020, BASE + '/tag/sezon-2025-2026/'),
    ('komodia', 30027, BASE + '/playlists/komodia/'),
    ('drama', 30028, BASE + '/playlists/drama/'),
)

GOLDEN_CLASSICS_PAGE = BASE + '/golden-classics/'
MEGANEWS_PAGE = BASE + '/meganews/'

PAGE_SIZE = 20


def bookmarks_file():
    from tulip import kodi
    import os

    return os.path.join(kodi.dataPath, 'bookmarks.db')


# ---------------------------------------------------------------------------
# Playback
#
# Stream resolution is delegated to ResolveURL / PluginsGR's MegaTVResolver:
# VOD episode pages resolve through their data-kwik_source m3u8, while the
# live page resolves through Vindral (channelId -> load balancer edge ->
# websocket proxy url).
# ---------------------------------------------------------------------------

PLUGINSGR_ID = 'script.module.resolveurl.pluginsgr'
PLUGINS_PATH = 'special://home/addons/{0}/resources/plugins/'.format(PLUGINSGR_ID)
