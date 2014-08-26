# -*- coding: utf-8 -*-

# Python 3.3 Module
# Chromium 29.0.1547.57 (217859)
# HexChat 2.9.6

__module_name__ = "Now Playing Extended"
__module_version__ = "1.1"
__module_description__ = "Displayes the current song using the /np command"

import hexchat
hexchat.emit_print("Generic Message", "Loading", "{} {} - {}".format(
                   __module_name__, __module_version__,
                   __module_description__))

from mpd import MPDClient

import os
import json
import http.client
import subprocess
from urllib.parse import urlparse
from html import entities
import re


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
    return re.sub(r'&(?:(?P<hex>#x[a-fA-F0-9]+)|(?P<num>#[0-9]+)'
                  '|(?P<name>\w+));', _repl, text, re.I)


def safe_to_send(text):
    '''
    replaces codepoints lower than \x20, to avoid injection of linebreaks etc.
    '''
    return re.sub(r'[\u0000-\u001f]+', ' ', text).strip()


def get_mplayer_string():
    '''
        gets the current title played in mplayer or gnome-mplayer
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
        try:
            ret = subprocess.check_output(['pidof', 'smplayer'])
            player_found = 'smplayer'
        except subprocess.CalledProcessError:
            pass

    if ret is None:
        try:
            ret = subprocess.check_output(['pidof', 'gnome-mplayer'])
            player_found = 'gnome-mplayer'
        except subprocess.CalledProcessError:
            pass

    # smplayer (or other) might invoke the mplayer. so mplayer is last
    if ret is None:
        try:
            ret = subprocess.check_output(['pidof', 'mplayer'])
            player_found = 'mplayer'
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
        return mplayer_string + ' ({})'.format(player_found)


def get_mpd_string():
    '''
        gets the current song using MPDClien library
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

    album = song.get('album', None)
    if isinstance(album, list):
        album = ' ／ '.join(album)

    if artist is None and title is None and album is None:
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
        if album is not None:
            metalist.append(album)
        if title is not None:
            metalist.append(title)

    if len(metalist) == 0:
        hexchat.prnt('Keine Metadaten gefunden.')
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
        hexchat.prnt('Es wird zur zeit nichts abgespielt.')
        return hexchat.EAT_HEXCHAT

    outputstr = '♫ {} ♫'.format(metastr)
    hexchat.command('me is listening to: {}'.format(outputstr))
    return hexchat.EAT_HEXCHAT


hexchat.hook_command("NP", np, help="/NP Displays the current song if "
                     "MPD is playing.")
