# coding: utf-8
import re
import asyncio
from time import time

class Bcolors(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class BasePlugin(object):

    name = 'BasePlugin'
    description = ''

    def __init__(self, filter_pattern=None, filter_collections=None):
        self.filter_pattern = filter_pattern
        self.filter_collections = filter_collections or []
        self.files_created = []

    def log_error(self, message):
        print('{}{}{}'.format(Bcolors.FAIL, message, Bcolors.ENDC))

    def log_sucess(self, message):
        print('{}{}{}'.format(Bcolors.OKGREEN, message, Bcolors.ENDC))

    def get_filtered_files(self, pypeline, files):
        filtered_files = {}
        filter_pattern = self.filter_pattern
        filter_collections = self.filter_collections

        if filter_collections:
            for collection in filter_collections:
                for file in pypeline.collections.get(collection, {}).get('files', []):
                    if filter_pattern and re.search(filter_pattern, file['path']):
                        filtered_files[file['path']] = file
                    else:
                        filtered_files[file['path']] = file

        elif filter_pattern:
            for path, file in files.items():
                if re.search(filter_pattern, path):
                    filtered_files[path] = file

        else:
            filtered_files = files

        return filtered_files

    def pre_run(self, pypeline, files):
        pass

    def post_run(self, pypeline, files):
        pass

    def run(self, pypeline, files):
        started_at = time()
        filtered_files = self.get_filtered_files(pypeline, files)

        self.pre_run(pypeline, filtered_files)

        self.process_files(pypeline, filtered_files)

        for file in self.files_created:
            pypeline.add_file(file)

        self.post_run(pypeline, filtered_files)

        self.log_sucess('{}: processed {} files in {:.5f}s'.format(self.name, len(filtered_files), time()-started_at))

    def process_files(self, pypeline, files):
        for path, file in files.items():
            self.process_file(path, file)

    def process_file(self, path, file):
        raise NotImplementedError


class BaseAsyncPlugin(BasePlugin):

    name = 'BaseAsyncPlugin'

    def run(self, pypeline, files):
        started_at = time()
        filtered_files = self.get_filtered_files(pypeline, files)

        self.pre_run(pypeline, filtered_files)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.process_files(pypeline, filtered_files))

        for file in self.files_created:
            pypeline.add_file(file)

        self.post_run(pypeline, filtered_files)

        self.log_sucess('{}: processed {} files in {:.5f}s'.format(self.name, len(filtered_files), time()-started_at))

    @asyncio.coroutine
    def process_files(self, pypeline, files):
        coroutines = [self.process_file(path, file) for path, file in files.items()]
        yield from asyncio.gather(*coroutines)

    @asyncio.coroutine
    def process_file(self, path, file):
        raise NotImplementedError
