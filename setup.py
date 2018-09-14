import os
import io
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

classifiers = ['Development Status :: 4 - Beta',
               'Operating System :: POSIX :: Linux',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: System :: Hardware']

setup(name              = 'Python_ST7789',
      version           = '1.0.0',
      author            = 'Mitsunao Hyodo',
      author_email      = 'hyodo.mitsunao@solinnovay.com',
      description       = 'Python library to use ST7789-based 240x240 pixel IPS displays with Raspberry Pi.',
      long_description  = long_description,
      license           = 'Solinnovay Laboratory',
      classifiers       = classifiers,
      url               = 'https://github.com/solinnovay/Python_ST7789/',
      dependency_links  = ['https://github.com/adafruit/Adafruit_Python_GPIO/tarball/master#egg=Adafruit-GPIO-0.6.5'],
      install_requires  = ['Adafruit-GPIO>=0.6.5'],
      packages          = find_packages())
