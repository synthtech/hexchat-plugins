from __future__ import print_function
import hexchat

__module_name__ = 'Slap'
__module_version__ = '1.1'
__module_description__ = 'Slaps specified users'
__author__ = 'https://github.com/TingPing'

def slap_cb(word, word_eol, userdata):
  if len(word) > 1:
    hexchat.command('me slaps {} around a bit with an unusually large trout'.format(word[1]))
  else:
    hexchat.command('help slap')

  return hexchat.EAT_ALL

def unload_cb(userdata):
  print(__module_name__, 'v' + __module_version__, 'unloaded')

hexchat.hook_command('slap', slap_cb, help='Usage: SLAP <nick>')
hexchat.hook_unload(unload_cb)
print(__module_name__, 'v' + __module_version__, 'loaded')