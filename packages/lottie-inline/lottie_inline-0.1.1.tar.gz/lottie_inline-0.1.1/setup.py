import importlib.util
import importlib.machinery
from setuptools import setup, find_packages
import os, json

def load_source(modname, filename):
    loader = importlib.machinery.SourceFileLoader(modname, filename)
    spec = importlib.util.spec_from_file_location(modname, filename, loader=loader)
    module = importlib.util.module_from_spec(spec)
    # The module is always executed and not cached in sys.modules.
    # Uncomment the following line to cache the module.
    # sys.modules[module.__name__] = module
    loader.exec_module(module)
    return module


PROJ_NAME = 'lottie-inline'
PACKAGE_NAME = 'lottie_inline'
PROJ_METADATA_PATH = '%s.json' % PROJ_NAME

here = os.path.abspath(os.path.dirname(__file__))
proj_info = json.loads(open(os.path.join(here, PROJ_METADATA_PATH), encoding='utf-8').read())

VERSION = load_source('version', os.path.join(here, 'src/%s/version.py' % PACKAGE_NAME)).__version__

setup(
    name=proj_info['name'],
    version=VERSION,
    description=proj_info['description'],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author=proj_info['author'],
    author_email=proj_info['author_email'],
    url=proj_info['url'],
    packages=find_packages(),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': proj_info['console_scripts'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
