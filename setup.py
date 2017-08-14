#!/usr/bin/env python

from digger_cli.__init__ import __version__
from setuptools import setup

setup(
	name='digger_cli',
	version=__version__,
	description='Crate digging tools for the command line.',
	author='Jose Maria Nunez-Izu',
	author_email='jmnunezizu@gmail.com',
	url='https://github.com/jmnunezizu/digger-cli',
	license='MIT',
	packages='digger_cli',
	# install_requires=[
	# 	'click',
	# 	# 'click_repl',
	# 	'discogs_client'
	# ]
)
