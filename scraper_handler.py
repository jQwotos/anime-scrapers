import glob
import imp
import logging
import os
import re

from difflib import SequenceMatcher
from templates.module_search import ModuleSearch

matchPercentage = .85

class ScraperHandler(ModuleSearch):
    def __init__(self):
        self.scrapers_location = "scrapers/"
        self.modules = glob.glob("%s*.py" % (self.scrapers_location))
        self.modules = self._load_modules()

    def _search_module(self, query, module):
        return module.search(query)

    def search(self, query):
        logging.debug("Starting a search for '%s'." % (query,))
        return [self._search_module(query, x) for x in self.modules]

    def resolve(self, link):
        logging.debug("Starting a resolution for '%s' under scraper_handler." % (link,))
        for module in self.modules:
            functions = self._try_match_module(link, module)
            if len(functions) > 0:
                return functions[0](link)
        return None

def score_similarity(stringA, stringB):
    return SequenceMatcher(None, stringA, stringB).ratio()

scraper_handler = ScraperHandler()
