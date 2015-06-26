# coding: utf-8
from pypeline.plugins.base import BaseAsyncPlugin
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
import os
import io
import asyncio
import mistune


class HighlightRenderer(mistune.Renderer):

    def block_code(self, code, lang=None):
        if not lang:
            return '\n<pre><code>{}</code></pre>\n'.format(mistune.escape(code))
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(**self.options.get('highlight_options', {}))
        return highlight(code, lexer, formatter)


class MarkdownPlugin(BaseAsyncPlugin):

    name = 'Markdown Plugin'

    def __init__(self, filter_pattern=r'\.m(d|arkdown)$', filter_collections=None, highlight_options=None):
        super().__init__(filter_pattern=filter_pattern, filter_collections=filter_collections)
        self.highlight_options = highlight_options or {}

        renderer = HighlightRenderer(highlight_options=self.highlight_options)
        self.markdown = mistune.Markdown(renderer=renderer)

    @asyncio.coroutine
    def process_file(self, path, file):
        file['contents'].seek(0)
        contents = self.markdown.render(file['contents'].read().decode(encoding='UTF-8'))
        file['contents'] = io.BytesIO(bytes(contents, 'UTF-8'))

    def post_run(self, pypeline, files):
        for path, file in files.items():
            filename, _ = os.path.splitext(path)
            pypeline.rename_file(path, '{}.html'.format(filename))
