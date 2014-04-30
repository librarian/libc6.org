#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Nikita Menkovich'
SITENAME = u'librarian@blog:~$'
SITEURL = 'https://libc6.org'

TIMEZONE = 'Europe/Moscow'

DEFAULT_LANG = u'ru'

# Feed generation is usually not desired when developing
FEED_DOMAIN = SITEURL
FEED_ALL_RSS = "feed/index.xml"
CATEGORY_FEED_RSS = "feed/category/%s/index.xml"
FEED_MAX_ITEMS = 10

# Save as URL
ARTICLE_URL = 'page/{slug}/'
ARTICLE_SAVE_AS = 'page/{slug}/index.html'
CATEGORY_URL = 'category/{slug}/'
CATEGORY_SAVE_AS = 'category/{slug}/index.html'
TAGS_SAVE_AS = ''
TAG_SAVE_AS = ''
AUTHOR_SAVE_AS = ''
AUTHORS_SAVE_AS = ''
ARCHIVES_SAVE_AS = ''
CATEGORIES_SAVE_AS = ''

PLUGIN_PATH = 'plugins'
PLUGINS = ["neighbors", "sitemap", "extract_toc"]

PATH = 'content'
OUTPUT_PATH = 'output'
THEME = 'themes/librarian'
ARTICLE_EXCLUDES = (('pages',))

SLUG_SUBSTITUTIONS = [
    ("puteshestviia", "travel"),
    ("administrirovanie","sysadmin"),
    ("raznoe", "misc"),
    ("razrabotka", "development"),
    ("virtualizatsiia", "virtualization"),
]


# Sitemap
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}

MD_EXTENSIONS = (['toc', 'extra', 'abbr','footnotes'])

DEFAULT_PAGINATION = 1

EXTRA_PATH_METADATA = {
    'extras/robots.txt': {'path': 'robots.txt'},
    'extras/yandex_60245d14c5c4a755.txt': {'path': 'yandex_60245d14c5c4a755.txt'},
    'extras/yandex_6faa0e13dc55cf9f.txt': {'path': 'yandex_6faa0e13dc55cf9f.txt'},
}

STATIC_PATHS = [
    'uploads',
    'extras',
]

