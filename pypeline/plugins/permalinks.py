# coding: utf-8
from __future__ import unicode_literals
import asyncio
import re
from pypeline.plugins.base import BaseAsyncPlugin
from slugify import slugify


class PermalinksPlugin(BaseAsyncPlugin):
    """
    Generates a url attribute for each HTML file and rename the file to match the url
    if url is already set manually in frontmatter or by another plugin, just rename the file
    """

    name = 'Permalinks Plugin'

    def __init__(self, filter_pattern=r'\.html$', filter_collections=None):
        super().__init__(filter_pattern=filter_pattern, filter_collections=filter_collections)
        self.collections_permalinks = {}

    @asyncio.coroutine
    def process_file(self, path, file):
        url = file.get('url')
        if not url:
            permalink = self.get_permalink_pattern(file)
            url = '/{}/'.format(re.sub(r':(\w+)', lambda x: slugify(file[x.group(1)]), permalink))
            file['url'] = url

    def pre_run(self, pypeline, files):
        for collection_name, collection_data in pypeline.collections.items():
            self.collections_permalinks[collection_name] = collection_data.get('permalink', ':title').strip('/')

    def post_run(self, pypeline, files):
        for path, file in files.items():
            if file['url'].endswith('/'):
                pypeline.rename_file(path, '{}index.html'.format(file['url']))

    def get_permalink_pattern(self, file):
        if file['collections']:
            for collection in file['collections']:
                if collection in self.collections_permalinks:
                    return self.collections_permalinks[collection]
        return ':title'
