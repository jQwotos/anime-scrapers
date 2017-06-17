import glob
import imp
import logging
import os
import re

from random import randint

from templates.module_search import ModuleSearch

class DownloadHandler(ModuleSearch):
    def __init__(self):
        self.downloaders_location = "downloaders/"
        self.modules = glob.glob("%s*.py" % (self.downloaders_location))
        self.modules = self._load_modules()

    def resolve(self, data):
        logging.info("Trying to resolve '%s'" % (data['epNum']))
        for module in self.modules:
            for source in data['sources']:
                logging.info("Trying to resolve '%s' source." % (source['link']))
                if self._try_match_module(source['link'], module):
                    logging.info("Found a matching module for '%s'." % (source,))
                    fileName = "%s.mp4" % (data['epNum'],) if 'epNum' in data else source
                    if module.download(source['link'], fileName): break

download_handler = DownloadHandler()
