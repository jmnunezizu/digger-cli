# -*- coding: utf-8 -*-

import click

def title_extractor(func):
	def decorated(*args, **kwargs):
		click.echo(args[1].data['title'])
		return func(*args, **kwargs)

	return decorated

def artist_extractor(func):
	def decorated(*args, **kwargs):
		artists = [
			'{name} [{id}]'.format(
				name=a['name'],
				id=click.style(str(a.get('id')), fg='cyan')
			) for a in args[1].data['artists']
		]

		click.echo(', '.join(artists))
		return func(*args, **kwargs)

	return decorated

def release_extractor(func):
	@artist_extractor
	@title_extractor
	def decorated(*args, **kwargs):
		return func(*args, **kwargs)
	
	return decorated

def label_extractor(func):
	def decorated(*args, **kwargs):
		labels = [
			'{label} – {cat} [{id}]'.format(
				label=l.get('name'), 
				cat=l.get('catno'), 
				id=click.style(str(l.get('id')), fg='cyan')
            ) for l in args[1].data['labels']
        ]
		click.echo('Label: {0}'.format(', '.join(labels)))
		return func(*args, **kwargs)

	return decorated
