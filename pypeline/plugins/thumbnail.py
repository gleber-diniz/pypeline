# coding: utf-8
import asyncio
import os
from pypeline.plugins.base import BaseAsyncPlugin
from PIL import Image
import io


class ThumbnailPlugin(BaseAsyncPlugin):

    name = 'Thumbnail Plugin'

    def __init__(self, filter_pattern=None, filter_collections=None, sizes=None):
        super().__init__(filter_pattern=filter_pattern, filter_collections=filter_collections)

        self.sizes = sizes or []

    @asyncio.coroutine
    def process_file(self, path, file):

        image = file['contents']

        coroutines = [self.create_thumb(path, image, size) for size in self.sizes]
        thumbs_created = yield from asyncio.gather(*coroutines)

        self.files_created.extend(thumbs_created)

    @asyncio.coroutine
    def create_thumb(self, path, image, size):
        filename, ext = os.path.splitext(path)
        thumb = io.BytesIO()
        thumb_path = '{}_thumb_{}x{}{}'.format(filename, size[0], size[1], ext)
        thumb.name = thumb_path
        img = Image.open(image).copy()
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(thumb)

        image.seek(0)
        thumb.seek(0)

        return {
            'path': thumb_path,
            'contents': thumb,
            'collections': []
        }
