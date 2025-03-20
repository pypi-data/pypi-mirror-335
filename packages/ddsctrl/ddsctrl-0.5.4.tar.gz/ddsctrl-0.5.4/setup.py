# Set __version__ in the setup.py
with open('ddsctrl/version.py') as f: exec(f.read())

from setuptools import setup

setup(name='ddsctrl',
      description='ddscontroller allow basic handling of AD9912 and AD9915 DDS development board.',
      version=__version__,
      packages=['ddsctrl'],
      scripts=["bin/ddscontroller"],
      install_requires=['PyQt5',
                        'ad9xdds',
                        'signalslot'],
      url='https://gitlab.com/bendub/ddsctrl',
      author='Benoit Dubois',
      author_email='benoit.dubois@femto-engineering.fr',
      license = "LGPL-3.0-or-later",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering']
)
