# coding: utf-8
import io
import asyncio
from pypeline.plugins.base import BaseAsyncPlugin
from frontmatter import parse

class FrontmatterPlugin(BaseAsyncPlugin):
    name = 'Frontmatter Plugin'

    @asyncio.coroutine
    def process_file(self, path, file):
        metadata, contents = parse(file['contents'].read())

        if metadata.pop('path', None) or metadata.pop('collections', None):
            self.log_error('{}: path and collections are reserved keywords'.format(path))

        file.update(metadata)
        file['contents'] = io.BytesIO(bytes(contents, 'UTF-8'))