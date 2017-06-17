# anime-scrapers

Anime scrapers is a collection of scrapers that have been all unified.

## Functions

There are three primary function calls in the scrapers

```
scrape_all_show_sources(link):

  return {
    'episodes': [
      {
        'epNumber', 'number as a string',
        'sources', [{
            'link': 'link',
            'type': 'type of file (mp4 or iframe)',
          }]
      }
    ],
    'title': 'title of the show',
    'status': 'status of the show',
    'host': 'host such as gogoanime',
    'released': 'year released as a string',
  }
```

```

```
