import re
import logging

import requests
import demjson

from bs4 import BeautifulSoup

site_name = 'masteranime'

BASE_URL = "https://www.masterani.me"
SEARCH_URL = "%s/api/anime/search" % (BASE_URL,)
SHOW_URL = "%s/anime/info/" % (BASE_URL,)
EPISODE_LIST_URL = "%s/api/anime/{ID}/detailed" % (BASE_URL,)

showid_pat = re.compile("%s([0-9]+)-" % (SHOW_URL,))
sources_pat = re.compile('mirrors:(.*?), auto_update: \[1')

def _combine_link(url):
    return ("%s%s" % (BASE_URL, url,)).replace(' ', '')

def _merge_slug(location, slug):
    return _combine_link("/anime/%s/%s" % (location, slug,))

def _extract_single_search(data):
    return {
        'link': _merge_slug("info", data['slug']),
        'title': data['title'],
        'id': data['id'],
        'language': 'sub', # masteranime only has subs
        'host': site_name,
    }


def _extract_multiple_search(data):
    #return list(map(lambda x: _extract_single_search(x), data))
    return [_extract_single_search(x) for x in data]

# Masteranime has a hidden api
# that we can abuse, this makes it easier
# so that we don't need to webscrape as much.
def search(query):
    params = {
        'search': query,
        'sb': 'true',
    }
    data = requests.get(SEARCH_URL, params=params).json()

    return _extract_multiple_search(data)

def _scrape_show_id(link):
    return re.findall(showid_pat, link)[0]

def _scrape_single_video_source(data):
    combined = '%s%s' % (data['host']['embed_prefix'], data['embed_id'])
    if data['host']['embed_suffix'] is not None:
        combined = "%s%s" % (combined, data['host']['embed_suffix'])
    return {
        'link': combined,
        'type': '',
        'quality': data['quality'],
        'id': data['id'],
    }

def _scrape_video_sources(link):
    logging.info("Scraping sources for %s under masteranime." % (link,))
    data = BeautifulSoup(requests.get(link).content, 'html.parser')
    sources = str(data.findAll("script")[3])
    sources = re.findall(sources_pat, sources)[0]
    sources = demjson.decode(sources)

    # return list(map(lambda x: _scrape_single_video_source(x), sources))
    return [_scrape_single_video_source(x) for x in sources]


def _parse_list_single(data, link):
    data = data['info']
    link = "%s/%s" % (link, data['episode'])
    return {
        'epNum': data['episode'],
        'sources': _scrape_video_sources(link),
    }

def _parse_list_multi(data):
    logging.info("A request for scraping all sources from %s under masteranime" % (data['link'],))
     #return list(map(lambda x: _parse_list_single(x, data['link']), data['episodes']))
    return [_parse_list_single(x, data['link']) for x in data['episodes']]

def _load_list_episodes(data):
    slug = data['info']['slug']
    link = _merge_slug("watch" ,slug)
    data['link'] = link
    return _parse_list_multi(data)

def _parse_status(status):
    statuses = ['completed', 'airing']
    return statuses[status]

def scrape_all_show_sources(link):
    id = _scrape_show_id(link)
    updatedLink = EPISODE_LIST_URL.replace('{ID}', id)
    data = requests.get(updatedLink).json()
    episodes = _load_list_episodes(data)
    data = data['info']
    data.update({
        'episodes': episodes,
        'status': _parse_status(data['status']),
    })
    return data

matching_urls = [
    {
        'urls': [r'https://www.masterani.me/anime/info/(.*)'],
        'function': scrape_all_show_sources,
    },
    {
        'urls': [],
        'function': search,
    },
    {
        'urls': [r'https://www.masterani.me/anime/watch/(.*)/([0-9]+)'],
        'function': _scrape_video_sources,
    }
]
