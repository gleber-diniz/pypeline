# coding: utf-8
from __future__ import unicode_literals
import asyncio
import textwrap
from pypeline.plugins.base import BaseAsyncPlugin
from bs4 import BeautifulSoup

class ExcerptsPlugin(BaseAsyncPlugin):

    name = 'Excerpts Plugin'

    def __init__(self, filter_pattern=r'\.html', filter_collections=None, size=200, max_paragraphs=3):
        super().__init__(filter_pattern=filter_pattern, filter_collections=filter_collections)
        self.size = size
        self.max_paragraphs = max_paragraphs

    @asyncio.coroutine
    def process_file(self, path, file):
        if file.get('excerpt'):
            return

        description = file.get('description')
        if description:
            file['excerpt'] = description
        else:
            contents = file['contents'].read().decode(encoding='UTF-8')
            soup = BeautifulSoup(contents)
            contents = ' '.join(p.get_text() for p in soup.find_all('p')[:self.max_paragraphs])

            if len(contents) < self.size:
                excerpt = contents
            else:
                lines = textwrap.wrap(contents, self.size, break_long_words=False)

                if len(lines) > 1:
                    excerpt = '{}...'.format(lines[0])
                else:
                    excerpt = lines[0]

            file['excerpt'] = excerpt
