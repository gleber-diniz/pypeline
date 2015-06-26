# coding: utf-8
import asyncio
from datetime import datetime
import io
from pypeline.plugins.base import BaseAsyncPlugin
from jinja2 import FileSystemLoader, Environment


class TemplateJinja2Plugin(BaseAsyncPlugin):

    name = 'Jinja2 Plugin'

    def __init__(self, filter_pattern='.html$', filter_collections=None, default_template='page.html'):
        super().__init__(filter_pattern=filter_pattern, filter_collections=filter_collections)
        self.default_template = default_template
        self.templates_cache = {}
        self.env = None

        self.metadata = {}
        self.collections = {}

    def pre_run(self, pypeline, files):
        self.env = Environment(loader=FileSystemLoader(pypeline.templates_path))
        self.metadata = pypeline.metadata
        self.collections = pypeline.collections

    def get_template(self, env, template_name):
        if not template_name:
            template_name = self.default_template

        if template_name in self.templates_cache:
            return self.templates_cache[template_name]
        else:
            return env.get_template(template_name)

    @asyncio.coroutine
    def process_file(self, path, file):
        template = self.get_template(self.env, file.get('template'))

        file['contents'].seek(0)
        file['contents'] = file['contents'].read().decode('utf-8')

        context = {
            'page': file,
            'metadata': self.metadata,
            'collections': self.collections,
            'strftime': datetime.now().strftime
        }

        file['contents'] = io.BytesIO(template.render(**context).encode('utf-8'))
