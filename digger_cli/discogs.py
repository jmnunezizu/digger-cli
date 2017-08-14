# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import click
import textwrap
import json

from discogs_client import Client

from extractors import artist_extractor, label_extractor, release_extractor

class Discogs(object):

    APP_VERSION = 'digger-cli/1.0.0'
    HEADER_COLOUR = 'yellow'
    LABEL_COLOUR = 'cyan'
    ID_COLOUR = 'cyan'
	
    def __init__(self, user_token=None):
        self.client = Client(Discogs.APP_VERSION, user_token=user_token)

    def cheader(self, header):
        return click.style(header, fg=Discogs.HEADER_COLOUR, bold=True)

    def clabel(self, label):
        return click.style(label)

    def cid(self, id):
        return click.style(id, fg=Discogs.ID_COLOUR)

    def _separator(self, title):
        """Renders the ASCII delimiter/separator
        :type title: str
        :param title: A string representing the delimiter title.
        :rtype: str
        :return: A formatted string."""
        MAX = 50
        LEFT = 4
        RIGHT = 3
        return (
          ' -- [ ' + click.style(title, fg=Discogs.LABEL_COLOUR, bold=True) + ' ] {line}'.
                format(title=title, line='-' * (MAX - 4 - len(title) - RIGHT)))

    def _artists(self, artists):
        """Formats the artist name and database id.
        :type artists: list
        :param artists: A list containing 1 or more artists data structures.
        :rtype: list
        :return: List of formatted artist names and ids."""

        try:
            return ['{name} [{id}]'.format(
                name=a['name'],
                id=self.cid(str(a['id']))
            ) for a in artists]
        except TypeError:
            return []

    def _page_artists(self, artists, page=1, end=1):
        """Renders a paginated list of Artist objects.
        :type artists:
        :param title: Paginated list containing artist objects."""

        while page <= end:
            for r in artists.page(page):
                click.echo('{artist} [{id}]'.format(artist=r.name,
                        id=self.cid(str(r.id))), color=True)
            page += 1

    def _page_labels(self, labels, page=1, end=1):
        return self._page_artists(labels, page=page, end=end)

    def _page_releases(self, releases, page=1, end=1, show_artist=False):
        if not show_artist:
            artist = ''

        while page <= end:
            for r in releases.page(page):
                if show_artist:
                    artist = r.data['artist'] + ' - '
                year = getattr(r, 'year', 'MASTER')
                click.echo('{year}\t{artist}{title} [{id}]'.format(year=year,
                title=r.title, id=self.cid(str(r.id)), artist=artist),
                color=True)
            page += 1


class Search(Discogs):

    def __init__(self, query, type='release', pages=1, user_token=None):
        super(Search, self).__init__(user_token=user_token)
        print(type)
        self.query = query
        self.type = type
        self.pages = pages
        self.discogs = self.client.search(query, type=type)

    def show(self):
        out = []
        out.append(self._separator('{n} {qt}(s) matching "{q}. Page {page}/{total_pages}"').format(
            q=self.query, qt=self.type, n=self.discogs.count, page=1, total_pages=self.discogs._num_pages))
        click.echo('\n'.join(out), color=True)

        if self.type == 'release':
            self._page_releases(self.discogs, end=self.pages)
        elif self.type == 'artist':
            self._page_artists(self.discogs, end=self.pages)
        elif self.type == 'label':
            self._page_labels(self.discogs, end=self.pages)


class Artist(Discogs):

    def __init__(self, id):
        super(Artist, self).__init__()
        self.id = id
        self.artist = self.client.artist(self.id)

    def show(self):
        out = []

        out.append(self.cheader(self.artist.name))
        out.append(self.clabel('Members     ') + ': {members}'.format(
            members=', '.join(self._artists(self.artist.data.get('members', []))))
        )
        out.append(self.clabel('Variations  ') + ': {var}'.format(var=', '.join(
            self.artist.data.get('namevariations', []))))
        out.append(self.clabel('In groups   ') + ': {groups}'.format(groups=
            ', '.join(self._artists(self.artist.data.get('groups', [])))))
        out.append(self._separator('Profile'))
        out.append(self.artist.data.get('profile', 'None.'))
        out.append(self._separator('Releases'))
        click.echo('\n'.join(out), color=True)
        self._page_releases(self.artist.releases, page=1, end=
                            self.artist.releases.pages)

class List(Discogs):

    def __init__(self, id, user_token=None):
        super(List, self).__init__(user_token=user_token)
        self.id = id
        self.list = self.client.userlist(self.id)

    def show(self, comments):
        click.echo('Name: {name}'.format(name=self.list.name), color=True)

        for i in self.list.items:
            #  - Lowest Price: {lowest_price} # , lowest_price=i.release.lowest_price
            click.echo('{title} [{id}]'.format(title=i.display_title, id=Id(i.id)), color=True)
            if comments:
                click.echo(i.comment)

    def showSingle(self, comments, release):
        for i in self.list.items:
            if release == i.id:
                click.echo('{title} [{id}]'.format(title=i.display_title, id=Id(i.id)), color=True)
                if comments:
                    click.echo(i.comment)
                break
        # click.echo('Could not find release {release}'.format(release=release))

    def export(self, comments):
        # click.echo(json.dumps(self.list.items.__dict__))
        releases = []
        for i in self.list.items:
            a=2
            releases.append({'id': i.id, 'title': i.display_title, 'comment': i.comment})
            # click.echo(json.dumps({'id': i.id, 'title': i.display_title, 'comment': i.comment}))

        click.echo(json.dumps({ 'releases': releases })) # sort_keys=True, indent=2


class Release(Discogs):

    TEMPLATE = textwrap.dedent("""\
        {artists} - {title}
        {huri}:         {uri}
        {hlabel}:       {label}
        {hformat}:      {format}
        {hcountry}:     {country}
        {hreleased}:    {released}
        {hgenre}:       {genre}
        {hstyle}:       {style}

        {htracklist}
        {tracklist}

        {hnotes}
        {notes}
    """)

    def __init__(self, id):
        super(Release, self).__init__()
        self.id = id
        self.discogs = self.client.release(self.id)

    @release_extractor
    @label_extractor
    def format(self, data):
        return 'format'
    
    def show1(self):
        year = self.discogs.year # read any property to force an API fetch
        click.echo(self.format(self.discogs))

    def show(self):
        year = self.discogs.year # read any property to force an API fetch
        data = self.discogs.data

        click.echo(
            self.TEMPLATE.format(
                artists=ArtistFormatter(data['artists']), title=self.discogs.title,
                huri=self.clabel('URL'), uri=self.discogs.url,
                hlabel=self.clabel('Label'), label=LabelFormatter().format(data['labels']),
                hformat=self.clabel('Format'), format=FormatFormatter().format(self.discogs.formats),
                hcountry=self.clabel('Country'), country=self.discogs.country,
                hreleased=self.clabel('Released'), released=year,
                hgenre=self.clabel('Genre'), genre=', '.join(self.discogs.genres),
                hstyle=self.clabel('Style'), style=', '.join(self.discogs.styles),
                htracklist=click.style('>> Tracklist', bold=True), tracklist=TracklistFormatter().format(data['tracklist']),
                hnotes=click.style('>> Notes', bold=True), notes=data.get('notes', 'None.')
            ),
            color=True
        )

class Id():
    
    def __init__(self, id):
        self.id = id
    
    def __format__(self, format):
        return click.style(str(self.id), fg='cyan')

class ArtistFormatter():

    def __init__(self, artists):
        self.artists = artists

    def __format__(self, format):
        return ','.join(['{name} [{id}]'.format(
            name=a['name'],
            id=Id(a.get('id'))
        ) for a in self.artists])        

class LabelFormatter():

    def format(self, labels):
        return ', '.join([
            '{label} – {cat} [{id}]'.format(
                label=l.get('name'), 
                cat=l.get('catno'), 
                id=Id(l.get('id'))
            ) for l in labels
        ])

class FormatFormatter():

    def format(self, formats):
        return ', '.join([
            '{name}, {desc}, {text}'.format(
                name=f.get('name'),
                desc=', '.join(f.get('descriptions', [])),
                text=f.get('text')
            ) for f in formats
        ])

class TracklistFormatter():

    def format(self, tracklist):
        return '\n'.join([
            '{position}\t{title: <50} {duration}'.format(
                position=t['position'],
                title=t['title'], 
                duration='   {0}'.format(t.get('duration'))
            ) for t in tracklist
        ])
