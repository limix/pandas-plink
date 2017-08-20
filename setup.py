import re
import sys
from os import chdir, getcwd
from os.path import abspath, dirname, join

from setuptools import find_packages, setup

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


class setup_folder(object):
    def __init__(self):
        self._old_path = None

    def __enter__(self):
        src_path = dirname(abspath(sys.argv[0]))
        self._old_path = getcwd()
        chdir(src_path)
        sys.path.insert(0, src_path)

    def __exit__(self, *_):
        del sys.path[0]
        chdir(self._old_path)


def get_init_metadata(metadata, name):
    expr = re.compile(r"__%s__ *= *\"(.*)\"" % name)
    prjname = metadata['packages'][0]
    data = open(join(prjname, "__init__.py")).read()
    return re.search(expr, data).group(1)


def make_list(metadata, name):
    if name in metadata:
        metadata[name] = metadata[name].strip().split('\n')


def set_long_description(metadata):
    df = metadata['description_file']
    metadata['long_description'] = open(df).read()
    del metadata['description_file']


def convert_types(metadata):
    bools = ['True', 'False']
    for k in metadata.keys():
        if isinstance(metadata[k], str) and metadata[k] in bools:
            metadata[k] = metadata[k] == 'True'


def setup_package():
    with setup_folder():

        config = ConfigParser()
        config.read('setup.cfg')
        metadata = dict(config.items('metadata'))
        metadata['packages'] = find_packages()
        metadata['platforms'] = eval(metadata['platforms'])

        metadata['version'] = get_init_metadata(metadata, 'version')
        metadata['author'] = get_init_metadata(metadata, 'author')
        metadata['author_email'] = get_init_metadata(metadata, 'author_email')
        metadata['name'] = get_init_metadata(metadata, 'name')
        make_list(metadata, 'classifiers')
        make_list(metadata, 'keywords')
        set_long_description(metadata)
        convert_types(metadata)

        setup(**metadata)


if __name__ == '__main__':
    setup_package()
