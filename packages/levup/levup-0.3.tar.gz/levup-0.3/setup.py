import os
from setuptools import setup
from setuptools.command.test import test
__dir__ = os.path.dirname(__file__)
about = {}
with open(os.path.join(__dir__, 'levup', '__about__.py')) as f:
    exec(f.read(), about)
def run_tests(self):
    raise SystemExit(__import__('pytest').main(['-v']))
test.run_tests = run_tests
setup(
    name='levup',
    version=about['__version__'],
    packages=['levup'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    description=about['__description__'],
    keywords=about['__keywords__'],
    url=about['__url__'],
    install_requires=['six'],
    tests_require=['pytest'],
)
