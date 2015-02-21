# -*- coding: utf-8 -*-

#/**
#* mpc.hc.np.py, snippet to display now-playing info for MPC-HC
#* Released under the terms of MIT license
#*
#* https://github.com/mpc-hc/snippets
#*
#* Copyright (C) 2013 MPC-HC Team
#*/

from __future__ import print_function
import hexchat

__module_name__ = "MPC-HC Now Playing"
__module_version__ = "0.2"
__module_description__ = "Displays MPC-HC Player Info!"
__author__ = "https://github.com/mpc-hc"

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import re

MPC_HC_PORT = "13579"      # Default port
MPC_HC_PAGE = "info.html"  # Page where "now playing" info is displayed

MPC_HC_URL = "http://{0}:{1}/{2}".format("localhost", MPC_HC_PORT, MPC_HC_PAGE)

MPC_HC_REGEXP = re.compile(r"\<p\ id\=\"mpchc_np\"\>(.*)\<\/p\>")


def mpc_hc(word, word_eol, userdata):
    data = urllib2.urlopen(MPC_HC_URL).read()
    mpc_hc_np = MPC_HC_REGEXP.findall(data.decode("utf-8"))[0].replace("&laquo;", "«")
    mpc_hc_np = mpc_hc_np.replace("&raquo;", "»")
    mpc_hc_np = mpc_hc_np.replace("&bull;", "•")
    hexchat.command("say %s" % mpc_hc_np)
    return hexchat.EAT_ALL

def unload(userdata):
	print(__module_name__, "v" + __module_version__, "unloaded")

hexchat.hook_command("np", mpc_hc, help="Usage: NP, displays info from what is playing in MPC-HC")
hexchat.hook_unload(unload)
print(__module_name__, "v" + __module_version__, "loaded")