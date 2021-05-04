#
#
#    Copyright (C) 2021  Alin Cretu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#

import sys
from urllib.parse import urlencode
from urllib.parse import parse_qsl
import xbmcgui
import xbmcplugin
import xbmcvfs
import xbmcaddon
import os
import re
import json
import requests
import logging
import logging.handlers
import resources.lib.common.vars as common_vars
import resources.lib.common.functions as common_functions
import resources.lib.digionline.functions as digionline_functions
import resources.lib.protvplus.functions as protvplus_functions
import http.cookiejar


__SystemBuildVersion__ = xbmc.getInfoLabel('System.BuildVersion')
__SystemBuildDate__ = xbmc.getInfoLabel('System.BuildDate')

# Kodi uses the following sys.argv arguments:
# [0] - The base URL for this add-on, e.g. 'plugin://plugin.video.demo1/'.
# [1] - The process handle for this add-on, as a numeric string.
# [2] - The query string passed to this add-on, e.g. '?foo=bar&baz=quux'.

# Get the plugin url in plugin:// notation.
common_vars.__plugin_url__ = sys.argv[0]

# Get the plugin handle as an integer number.
common_vars.__handle__ = sys.argv[1]

MyAddon = xbmcaddon.Addon(id=common_vars.__AddonID__)

# The version of the runing Addon
__AddonVersion__ = MyAddon.getAddonInfo('version')

# Initialize the Addon data directory
MyAddon_DataDir = xbmcvfs.translatePath(MyAddon.getAddonInfo('profile'))
if not os.path.exists(MyAddon_DataDir):
    os.makedirs(MyAddon_DataDir)

# Read the user preferences stored in the addon configuration
common_functions.read_AddonSettings(MyAddon, common_vars.__ServiceID__)

# Log file name
addon_logfile_name = os.path.join(MyAddon_DataDir, common_vars.__AddonLogFilename__)

# Configure logging
if common_vars.__config_DebugEnabled__ == 'true':
  logging.basicConfig(level=logging.DEBUG)
else:
  logging.basicConfig(level=logging.INFO)

#logger = logging.getLogger('plugin.video.DigiOnline.log')
common_vars.__logger__ = logging.getLogger(common_vars.__AddonID__)
common_vars.__logger__.propagate = False

# Create a rotating file handler
# TODO: Extend the settings.xml to allow the user to choose the values for maxBytes and backupCount
# TODO: Set the values for maxBytes and backupCount to values defined in the addon settings
handler = logging.handlers.RotatingFileHandler(addon_logfile_name, mode='a', maxBytes=104857600, backupCount=2, encoding='utf-8', delay=False)
if common_vars.__config_DebugEnabled__ == 'true':
  handler.setLevel(logging.DEBUG)
else:
  handler.setLevel(logging.INFO)

# Create a logging format to be used
formatter = logging.Formatter('%(asctime)s %(funcName)s %(levelname)s: %(message)s', datefmt='%Y%m%d_%H%M%S')
handler.setFormatter(formatter)

# add the file handler to the common_vars.__logger__
common_vars.__logger__.addHandler(handler)

# Initialize the CookieJar variable 
digionline_functions.init_AddonCookieJar(common_vars.__AddonID__, MyAddon_DataDir)
protvplus_functions.init_AddonCookieJar(common_vars.__AddonID__, MyAddon_DataDir)

# Start a new requests sessions and initialize the cookiejar
common_vars.__digionline_Session__ = requests.Session()
common_vars.__protvplus_Session__ = requests.Session()

# Put all session cookeis in the cookiejar
common_vars.__digionline_Session__.cookies = common_vars.__digionline_CookieJar__
common_vars.__protvplus_Session__.cookies = common_vars.__protvplus_CookieJar__


def list_enabled_accounts():
  ####
  #
  # Create in the Kodi interface a virtual folder containing the list of accounts enabled in the add-on settings.
  #
  ####
  
  common_vars.__logger__.debug('Enter function')

  # Set plugin category.
  xbmcplugin.setPluginCategory(int(common_vars.__handle__), 'TVOnline.ro')

  # Set plugin content.
  xbmcplugin.setContent(int(common_vars.__handle__), 'videos')

  # digionline.ro
  if common_vars.__config_digionline_Enabled__ == 'true':
    common_vars.__logger__.debug('\'digionline.ro\'  ==> Enabled')

    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label='digionline.ro')

    # Set additional info for the list item.
    # For available properties see https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
    # 'mediatype' is needed for a skin to display info for this ListItem correctly.
    list_item.setInfo('video', {'title': 'digionline.ro',
                                'mediatype': 'video'})

    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.video.example/?action=listing&account=digionline.ro
    url = common_functions.get_url(action='list_categories', account='digionline.ro')
    common_vars.__logger__.debug('URL for plugin recursive call: ' + url)

    # This means that this item opens a sub-list of lower level items.
    is_folder = True

    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(int(common_vars.__handle__), url, list_item, is_folder)

  else:
    common_vars.__logger__.debug('\'digionline.ro\'  ==> Disabled')


  # protvplus.ro
  if common_vars.__config_protvplus_Enabled__ == 'true':
    common_vars.__logger__.debug('\'protvplus.ro\'  ==> Enabled')

    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label='protvplus.ro')

    # Set additional info for the list item.
    # For available properties see https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
    # 'mediatype' is needed for a skin to display info for this ListItem correctly.
    list_item.setInfo('video', {'title': 'protvplus.ro',
                                'mediatype': 'video'})

    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.video.example/?action=listing&account=digionline.ro
    url = common_functions.get_url(action='list_channels', account='protvplus.ro')
    common_vars.__logger__.debug('URL for plugin recursive call: ' + url)

    # This means that this item opens a sub-list of lower level items.
    is_folder = True

    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(int(common_vars.__handle__), url, list_item, is_folder)

  else:
    common_vars.__logger__.debug('\'protvplus.ro\'  ==> Disabled')

  # Add a sort method for the virtual folder items (alphabetically, ignore articles)
  # See: https://romanvm.github.io/Kodistubs/_autosummary/xbmcplugin.html
  xbmcplugin.addSortMethod(int(common_vars.__handle__), xbmcplugin.SORT_METHOD_LABEL)

  # Finish creating a virtual folder.
  xbmcplugin.endOfDirectory(int(common_vars.__handle__))

  common_vars.__logger__.debug('Exit function')


def router(paramstring):
  ####
  #
  # Router function that calls other functions depending on the provided paramster
  #
  # Parameters:
  #      paramstring: URL encoded plugin paramstring
  #
  ####

  common_vars.__logger__.debug('Enter function')

  # Parse a URL-encoded paramstring to the dictionary of {<parameter>: <value>} elements
  params = dict(parse_qsl(paramstring))

  # Check the parameters passed to the plugin
  if params:
      if params['action'] == 'list_categories':
        # Display the list of categories in a provided account.    

        # digionline.ro
        if params['account'] == 'digionline.ro':
          if common_vars.__config_digionline_Enabled__ == 'true':
            common_vars.__logger__.debug('\'digionline.ro\'  ==> Enabled')
            digionline_functions.digionline__listCategories(common_vars.__AddonID__, common_vars.__digionline_Session__, MyAddon_DataDir)
          else:
            common_vars.__logger__.debug('\'digionline.ro\'  ==> Disabled')

#        # protvplus.ro
#        if params['account'] == 'protvplus.ro':
#          if common_vars.__config_protvplus_Enabled__ == 'true':
#            common_vars.__logger__.debug('\'protvplus.ro\'  ==> Enabled')
#            protvplus_functions.list_categories(common_vars.__AddonID__, common_vars.__protvplus_CookieJar__, common_vars.__protvplus_Session__, MyAddon_DataDir)
#          else:
#            common_vars.__logger__.debug('\'protvplus.ro\'  ==> Disabled')

      elif params['action'] == 'list_channels':
        # Display the list of channels in the provided category from provided account.

        # digionline.ro
        if params['account'] == 'digionline.ro':
          if common_vars.__config_digionline_Enabled__ == 'true':
            common_vars.__logger__.debug('\'digionline.ro\'  ==> Enabled')
            digionline_functions.digionline__listChannels(params['category_name'], params['channel_list'], common_vars.__AddonID__, common_vars.__digionline_Session__, MyAddon_DataDir)
          else:
            common_vars.__logger__.debug('\'digionline.ro\'  ==> Disabled')

        # protvplus.ro
        if params['account'] == 'protvplus.ro':
          if common_vars.__config_protvplus_Enabled__ == 'true':
            common_vars.__logger__.debug('\'protvplus.ro\'  ==> Enabled')
            protvplus_functions.list_channels(common_vars.__AddonID__, common_vars.__protvplus_CookieJar__, common_vars.__protvplus_Session__, MyAddon_DataDir)
          else:
            common_vars.__logger__.debug('\'protvplus.ro\'  ==> Disabled')      
      
      elif params['action'] == 'play':
        # Play a video from the provided URL.
        
        # digionline.ro
        if params['account'] == 'digionline.ro':
          if common_vars.__config_digionline_Enabled__ == 'true':
            common_vars.__logger__.debug('\'digionline.ro\'  ==> Enabled')
            digionline_functions.digionline__playVideo(params['channel_id'], common_vars.__AddonID__, common_vars.__digionline_Session__, MyAddon_DataDir)
          else:
            common_vars.__logger__.debug('\'digionline.ro\'  ==> Disabled')
            xbmcgui.Dialog().ok('\'Digionline.ro\' not enabled', 'The credentials for this media source are not enabled.')
            
        # protvplus.ro
        if params['account'] == 'protvplus.ro':
          if common_vars.__config_protvplus_Enabled__ == 'true':
            common_vars.__logger__.debug('\'protvplus.ro\'  ==> Enabled')
            protvplus_functions.play_video(params['channel_endpoint'], common_vars.__AddonID__, common_vars.__protvplus_CookieJar__, common_vars.__protvplus_Session__, MyAddon_DataDir)
          else:
            common_vars.__logger__.debug('\'protvplus.ro\'  ==> Disabled')
            xbmcgui.Dialog().ok('\'protvplus.ro\' not enabled', 'The credentials for this media source are not enabled.')

      else:
        # Raise an exception if the provided paramstring does not contain a supported action
        # This helps to catch coding errors,
        raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
  else:
    # If the plugin is called from Kodi UI without any parameters:

    # Display the list of accounts enabled in the add-on
    list_enabled_accounts()

  common_vars.__logger__.debug('Exit function')


if __name__ == '__main__':
  common_vars.__logger__.debug('Enter function')
  common_vars.__logger__.debug('=== SYSINFO ===  Addon version: ' + str(__AddonVersion__))
  common_vars.__logger__.debug('=== SYSINFO ===  System.BuildVersion: ' + str(__SystemBuildVersion__))
  common_vars.__logger__.debug('=== SYSINFO ===  System.BuildDate: ' + str(__SystemBuildDate__))

  # Read the user preferences stored in the addon configuration
  common_functions.read_AddonSettings(MyAddon, common_vars.__ServiceID__)

  # Call the router function and pass the plugin call parameters to it.
  router(sys.argv[2][1:])

  common_vars.__logger__.debug('Exit function')

