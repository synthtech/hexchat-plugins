# -*- coding: utf-8 -*-

# Originally made for Python 3.3

from __future__ import print_function
import hexchat

__module_name__ = 'Now Playing'
__module_version__ = '1.2'
__module_description__ = 'Displays the current song using the /np command'
__author__ = 'https://github.com/knitori'

from mpd import MPDClient

import os
import json
import subprocess
import re

#Only works using Python 3 (might be obsolete)
#import http.client
#from urllib.parse import urlparse
#from html import entities

def _repl(m):
    '''helper function for unescape_entities()'''
    if m.group('hex') is not None:
        return chr(int(m.group('hex'), 16))
    elif m.group('hex') is not None:
        return chr(int(m.group('num')))
    elif m.group('name') is not None:
        if m.group('name') in entities.name2codepoint:
            return chr(entities.name2codepoint[m.group('name')])
        else:
            return ''


def unescape_entities(text):
    '''
    unescapes html entities such as &quot; &lt; etc and
    also &#x12af; and &#123; codepoints.
    '''
    return re.sub(r'&(?:(?P<hex>#x[a-fA-F0-9]+)|(?P<num>#[0-9]+)|(?P<name>\w+));', _repl, text, re.I)


def safe_to_send(text):
    '''
    replaces codepoints lower than \x20, to avoid injection of linebreaks etc.
    '''
    return re.sub(r'[\u0000-\u001f]+', ' ', text).strip()


def get_mplayer_string():
    '''
        gets the current title played in mpv
        using the cheap method of reading it from the `ps` command.
    '''
    ret = None
    player_found = None

    try:
        ret = subprocess.check_output(['pidof', 'mpv'])
        player_found = 'mpv'
    except subprocess.CalledProcessError:
        pass

    if ret is None:
        return

    try:
        mplayer_pid = int(ret.strip())
    except (ValueError, TypeError):
        return

    with open('/proc/{}/cmdline'.format(mplayer_pid), 'rb') as f:
        ret = f.read()

    cmdargs = ret.split(b'\x00')
    cmdargs = [arg for arg in cmdargs if arg]

    # assuming the path is the *last* argument
    filepath = cmdargs[-1]

    # and assuming utf-8 (might want to check the locale or something)
    mplayer_string = os.path.basename(filepath.decode('utf-8', 'replace')).strip()
    mplayer_string = mplayer_string.replace('_', ' ')
    filename, _, ext = mplayer_string.rpartition('.')
    if len(ext) <= 5:
        mplayer_string = filename
    if mplayer_string != '':
        return mplayer_string


def get_mpd_string():
    '''
        gets the current song using MPDClient library
        https://github.com/Mic92/python-mpd2
        $ pip install python-mpd2
    '''
    c = MPDClient()
    c.timeout = 2
    try:
        c.connect('localhost', 6600)
    except:
        return None

    status = c.status()

    if status['state'] != 'play':
        return None

    metalist = []
    song = c.currentsong()

    artist = song.get('artist', None)
    if isinstance(artist, list):
    	artist = ' ／ '.join(artist)

    title = song.get('title', None)
    if isinstance(title, list):
    	title = ' ／ '.join(title)

    if artist is None and title is None:
        filename = song.get('file', None)
        if filename is not None:
            filename = filename
            filename = os.path.basename(filename).replace('_', ' ')
            filename, _, ext = filename.rpartition('.')
            if filename == '':
                filename = ext
            metalist.append(filename)
    else:
        if artist is not None:
            metalist.append(artist)
        if title is not None:
            metalist.append(title)

    if len(metalist) == 0:
        hexchat.prnt('Metadata not found.')
        return None

    metastr = ' - '.join(metalist)

    seconds = int(song.get('time', None))
    minutes = seconds // 60
    seconds = seconds % 60

    d = {'meta': metastr, 'sec': seconds, 'min': minutes}
    metastr = '{meta} - {min}:{sec:02d}'.format(**d)

    return metastr


def np(word, word_eol, userdata):

    metastr = get_mpd_string()

    if metastr is None:
        metastr = get_mplayer_string()

    if metastr is None:
        hexchat.prnt('Nothing is playing at this time.')
        return hexchat.EAT_HEXCHAT

    hexchat.command('me is listening to {}'.format(metastr))
    return hexchat.EAT_HEXCHAT


def unload(userdata):
  print(__module_name__, 'v' + __module_version__, 'unloaded')

hexchat.hook_command('np', np, help='Usage: NP, displays the current song that is playing')
hexchat.hook_unload(unload)
print(__module_name__, 'v' + __module_version__, 'loaded')