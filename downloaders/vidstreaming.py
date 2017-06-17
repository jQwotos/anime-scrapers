import re
import os
import logging

import requests

from bs4 import BeautifulSoup

from downloaders import mp4

site_name = 'vidstream'

BASE_URL = "https://vidstreaming.io"
DOWNLOAD_URL = "https://vidstream.co/download"

embed_id_pat = re.compile("%s/embed.php\?id=(.*?)&" % (BASE_URL,))
download_id_pat = re.compile("%s/download\?id=(.*?)&" % (BASE_URL,))

qualities = ['1080', '720', '480', '360']

def _try_match_url(link, matchingURL):
    return True if re.match(matchingURL, link) is not None else False

def _try_match_module_section(link, section):
    urls = section['urls']
    matches = [section['function'] for x in urls
                if _try_match_url(link, x) is not False]
    return True if len(matches) > 0 else False

def resolve(link):
    for section in internal_matching_urls:
        if _try_match_module_section(link, section):
            logging.info("Found a match for %s" % (link,))
            source = section['function'](link)
            return source
    return None

def download(link, fname):
    logging.info("Starting download for '%s' under vidstreaming." % (link,))
    source = resolve(link)['sources'][-1]['link']
    if source is not None: mp4.download(source, fname)

def _parse_quality(title):
    for q in qualities:
        if q in title: return q
    return None

def _parse_list_single(data):
    return {
        'link': data['href'],
        'type': 'mp4',
        'quality': _parse_quality(data.text),
    }

def _parse_list_multi(data):
    box = data.find("div", {"class": "mirror_link"})
    sources = box.findAll("a")
    if len(sources) == 0: logging.critical("Can't find sources on vidstreaming!")
    return [_parse_list_single(x) for x in sources]

def _scrape_video_sources_id(id):
    params = {
        'id': id,
    }
    data = BeautifulSoup(requests.get(DOWNLOAD_URL, params=params).content, 'html.parser')
    return {
        'sources': _parse_list_multi(data),
    }

def _scrape_video_sources(link):
    id = re.findall(download_id_pat, link)[0]
    return _scrape_video_sources(id)

def _scrape_iframe_sources(link):
    id = re.findall(embed_id_pat, link)[0]
    return _scrape_video_sources_id(id)

matching_urls = [
    {
        'urls': [
            r'https://vidstream.co/embed.php\?(.*)',
            r'https://vidstreaming.io/embed.php\?id=(.*)',
            ],
        'function': download,
    }
]

internal_matching_urls = [
    {
        'urls': [r'https://vidstream.co/download\?id=(.*)'],
        'function': _scrape_video_sources,
    },
    {
        'urls': [
            r'https://vidstream.co/embed.php\?(.*)',
            r'https://vidstreaming.io/embed.php\?id=(.*)',
            ],
        'function': _scrape_iframe_sources,
    }
]
