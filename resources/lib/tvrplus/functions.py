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
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import os
import logging
import http.cookiejar
import re
import time
import json
import inputstreamhelper
import resources.lib.common.vars as common_vars
import resources.lib.common.functions as common_functions


def init_AddonCookieJar(NAME, DATA_DIR):
  ####
  #
  # Initialize the common_vars.__tvrplus_CookieJar__ variable.
  #
  # Parameters:
  #      NAME: common_vars.__logger__ name to use for sending the log messages
  #      DATA_DIR: The addon's 'userdata' directory.
  #
  ####

  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  # File containing the session cookies
  cookies_file = os.path.join(DATA_DIR, common_vars.__tvrplus_CookiesFilename__)
  common_vars.__logger__.debug('[ Addon cookies file ] cookies_file = ' + str(cookies_file))
  common_vars.__tvrplus_CookieJar__ = http.cookiejar.MozillaCookieJar(cookies_file)

  # If it doesn't exist already, create a new file where the cookies should be saved
  if not os.path.exists(cookies_file):
    common_vars.__tvrplus_CookieJar__.save()
    common_vars.__logger__.debug('[ Addon cookiefile ] Created cookiejar file: ' + str(cookies_file))

  # Load any cookies saved from the last run
  common_vars.__tvrplus_CookieJar__.load()
  common_vars.__logger__.debug('[ Addon cookiejar ] Loaded cookiejar from file: ' + str(cookies_file))


def list_categories(NAME, COOKIEJAR, SESSION, DATA_DIR):
  ####
  #
  # Create the list of video categories in the Kodi interface.
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  common_vars.__logger__.debug('Exit function')


def list_channels(NAME, COOKIEJAR, SESSION, DATA_DIR):
  ####
  #
  # Create the list of playable videos in the Kodi interface.
  #
  # Parameters:
  #      NAME: Logger name to use for sending the log messages.
  #      COOKIEJAR: The cookiejar to be used with the given session.
  #      SESSION: The session to be used for login this call
  #      DATA_DIR: The addon's 'userdata' directory.
  #
  # Return: The list of cached video categories
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  # Get the list of videos in the category.
  channels = get_channels(NAME, COOKIEJAR, SESSION)
  common_vars.__logger__.debug('Received channels = ' + str(channels))

  for channel in channels:
    common_vars.__logger__.debug('Channel data => ' + str(channel))
    common_vars.__logger__.debug('Channel name: ' + channel['name'])
    common_vars.__logger__.debug('Channel url: ' + channel['url'])
    common_vars.__logger__.debug('Channel logo: ' + channel['logo'])
    common_vars.__logger__.debug('Channel ID: ' + channel['id'])

    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label=channel['name'])

    # Set additional info for the list item.
    # For available properties see https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
    # 'mediatype' is needed for skin to display info for this ListItem correctly.
    list_item.setInfo('video', {'title': channel['name'],
                                'genre': 'General',
                                'mediatype': 'video'})


    # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
    list_item.setArt({'thumb': channel['logo']})

    # Set 'IsPlayable' property to 'true'.
    # This is mandatory for playable items!
    list_item.setProperty('IsPlayable', 'true')

    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.video.example/?action=play&channel_endpoint=/filme/tnt&channel_metadata=...
    url = common_functions.get_url(action='play', account='tvrplus.ro', channel_endpoint=channel['url'])
    common_vars.__logger__.debug('URL for plugin recursive call: ' + url)

    # This means that this item won't open any sub-list.
    is_folder = False

    # Add our item to the Kodi virtual folder listing.
    xbmcplugin.addDirectoryItem(int(common_vars.__handle__), url, list_item, is_folder)

  # Add a sort method for the virtual folder items (alphabetically, ignore articles)
  xbmcplugin.addSortMethod(int(common_vars.__handle__), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

  # Finish creating a virtual folder.
  xbmcplugin.endOfDirectory(int(common_vars.__handle__))

  common_vars.__logger__.debug('Exit function')


def get_channels(NAME, COOKIEJAR, SESSION):
  ####
  #
  # Get from tvrplus.ro the list of channels/streams.
  #
  # Parameters:
  #      NAME: Logger name to use for sending the log messages
  #      COOKIEJAR: The cookiejar to be used with the given session
  #      SESSION: The session to be used for this call
  #      DATA_DIR: The addon's 'userdata' directory.
  #
  # Return: The list of channels/streams in the given category
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  MyAddon = xbmcaddon.Addon(id=common_vars.__AddonID__)
  __tvrplus_cacert__ = MyAddon.getAddonInfo('path') + 'resources/lib/tvrplus/tvrplus-ro-chain.pem'

  # Setup headers for the request
  MyHeaders = {
    'Host': 'www.tvrplus.ro',
    'User-Agent': common_vars.__tvrplus_userAgent__,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
  }

  common_vars.__logger__.debug('CA_CERT: ' + __tvrplus_cacert__)
  common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: https://www.tvrplus.ro')
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get('https://www.tvrplus.ro', headers=MyHeaders, verify=__tvrplus_cacert__)

  # Save cookies for later use.
  COOKIEJAR.save(ignore_discard=True)
  
  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())
  
  _raw_channels_ = re.findall('<div class="big-gallery">(.+?)</div>', _request_.content.decode(), re.IGNORECASE|re.DOTALL)
  common_vars.__logger__.debug('Found _raw_channels_ = ' + str(_raw_channels_))
  
  # Initialize the list of channels
  _channels_ = []

  for _raw_channel_ in _raw_channels_:
    common_vars.__logger__.debug('_raw_channel_ = ' + str(_raw_channel_))

    _channel_record_ = {}

    _channel_name_ = re.findall('alt="(.+?)"', _raw_channel_, re.IGNORECASE)[0]
    common_vars.__logger__.debug('_channel_name_ = ' + str(_channel_name_))

    _channel_url_ = re.findall('<a href="(.+?)"', _raw_channel_, re.IGNORECASE)[0]
    common_vars.__logger__.debug('_channel_url_ = ' + str(_channel_url_))

    _channel_logo_ = re.findall('<img src="(.+?)"', _raw_channel_, re.IGNORECASE)[0]
    common_vars.__logger__.debug('_channel_logo_ = ' + str(_channel_logo_))

    _channel_id_ = re.findall('live/(.+?)"', _raw_channel_, re.IGNORECASE|re.DOTALL)[0]
    common_vars.__logger__.debug('_channel_id_ = ' + str(_channel_id_))

    _channel_record_["name"] = _channel_name_
    _channel_record_["url"] = _channel_url_
    _channel_record_["logo"] = _channel_logo_
    _channel_record_["id"] = _channel_id_

    common_vars.__logger__.debug('Created: _channel_record_ = ' + str(_channel_record_))
    _channels_.append(_channel_record_)

  common_vars.__logger__.debug('_channels_ = ' + str(_channels_))
  common_vars.__logger__.debug('Exit function')

  return _channels_




def play_video(CHANNEL_ENDPOINT, NAME, COOKIEJAR, SESSION, DATA_DIR):
  ####
  #
  # Play a video by the provided path.
  #
  # Parameters:
  #      path: Fully-qualified video URL
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  
  common_vars.__logger__.debug('Chanel endpoint = ' + CHANNEL_ENDPOINT)

  MyAddon = xbmcaddon.Addon(id=common_vars.__AddonID__)
  __tvrplus_cacert__ = MyAddon.getAddonInfo('path') + 'resources/lib/tvrplus/tvrplus-ro-chain.pem'

  # Get the URL for the stream m3u8 file

  # Setup headers for the request
  MyHeaders = {
    'Host': 'www.tvrplus.ro',
    'User-Agent': common_vars.__tvrplus_userAgent__,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
  }

  common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: ' + CHANNEL_ENDPOINT)
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get(CHANNEL_ENDPOINT, headers=MyHeaders, verify=__tvrplus_cacert__)

  # Save cookies for later use.
  COOKIEJAR.save(ignore_discard=True)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

  _stream_manifest_url_ = re.findall('src: \'(.+?)\'', _request_.content.decode(), re.IGNORECASE|re.DOTALL)[0]
  common_vars.__logger__.debug('Found _stream_manifest_url_ = ' + _stream_manifest_url_)

#  # Set the headers to be used with imputstream.adaptive
  _headers_ = ''
#  _headers_ = _headers_ + '&User-Agent=' + common_vars.__digionline_userAgent__

#  common_vars.__logger__.debug('Created: _headers_ = ' + _headers_)

#  # Create a playable item with a path to play.
#  # See:  https://github.com/peak3d/inputstream.adaptive/issues/131#issuecomment-375059796
#  is_helper = inputstreamhelper.Helper('hls')
#  if is_helper.check_inputstream():
#    play_item = xbmcgui.ListItem(path=_stream_manifest_url_ + '|' + _headers_)
#    play_item.setProperty('inputstream', 'inputstream.adaptive')
#    play_item.setProperty('inputstream.adaptive.stream_headers', _headers_)
#    play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
#    play_item.setMimeType('application/vnd.apple.mpegurl')
#    play_item.setContentLookup(False)
#
#    # Pass the item to the Kodi player.
#    xbmcplugin.setResolvedUrl(int(common_vars.__handle__), True, listitem=play_item)

  play_item = xbmcgui.ListItem(path=_stream_manifest_url_)

  # Create a playable item with a path to play.
  is_helper = inputstreamhelper.Helper('hls')
  if is_helper.check_inputstream():
    play_item = xbmcgui.ListItem(path=_stream_manifest_url_ + '|' + _headers_)
    play_item.setProperty('inputstream', 'inputstream.adaptive')
    play_item.setProperty('inputstream.adaptive.manifest_headers', _headers_)
    play_item.setProperty('inputstream.adaptive.stream_headers', _headers_)
    play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    play_item.setMimeType('application/vnd.apple.mpegurl')
    play_item.setContentLookup(False)
    
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(int(common_vars.__handle__), True, listitem=play_item)

  common_vars.__logger__.debug('Exit function')


def PVRIPTVSimpleClientIntegration_update_m3u_file(M3U_FILE, START_NUMBER, NAME, COOKIEJAR, SESSION):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  
  common_vars.__logger__.debug('M3U_FILE = ' + M3U_FILE)
  common_vars.__logger__.debug('START_NUMBER = ' + str(START_NUMBER))
  
  # Get the list of channels in the category.
  channels = get_channels(NAME, COOKIEJAR, SESSION)
  common_vars.__logger__.debug('Received channels = ' + str(channels))
  
  _CHNO_ = START_NUMBER
  _data_file_ = open(M3U_FILE, 'a', encoding='utf-8')
  
  for channel in channels:
    _line_ = "#EXTINF:0 tvg-id=\"tvrplus__" + str(channel['id']) + "\" tvg-name=\"" + channel['name'] + "\" tvg-logo=\"" + channel['logo'] + "\" tvg-chno=\"" + str(_CHNO_) + "\" group-title=\"TVR Plus\"," + channel['name']
    
    _url_ = common_functions.get_url(action='play', account='tvrplus.ro', channel_endpoint=channel['url'])
    _play_url_ = "plugin://" + common_vars.__AddonID__ + "/" + _url_

    _data_file_.write(_line_ + "\n")
    _data_file_.write(_play_url_ + "\n")
        
    _CHNO_ = _CHNO_ + 1
    
  _data_file_.close()

  common_vars.__logger__.debug('Exit function')
  
  return _CHNO_
  
