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
import resources.lib.protvplus.functions as protvplus_functions


def init_AddonCookieJar(NAME, DATA_DIR):
  ####
  #
  # Initialize the common_vars.__protvplus_CookieJar__ variable.
  #
  # Parameters:
  #      NAME: common_vars.__logger__ name to use for sending the log messages
  #      DATA_DIR: The addon's 'userdata' directory.
  #
  ####

  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  # File containing the session cookies
  cookies_file = os.path.join(DATA_DIR, common_vars.__protvplus_CookiesFilename__)
  common_vars.__logger__.debug('[ Addon cookies file ] cookies_file = ' + str(cookies_file))
  common_vars.__protvplus_CookieJar__ = http.cookiejar.MozillaCookieJar(cookies_file)

  # If it doesn't exist already, create a new file where the cookies should be saved
  if not os.path.exists(cookies_file):
    common_vars.__protvplus_CookieJar__.save()
    common_vars.__logger__.debug('[ Addon cookiefile ] Created cookiejar file: ' + str(cookies_file))

  # Load any cookies saved from the last run
  common_vars.__protvplus_CookieJar__.load()
  common_vars.__logger__.debug('[ Addon cookiejar ] Loaded cookiejar from file: ' + str(cookies_file))



def do_auth_check(NAME, COOKIEJAR, SESSION):
  ####
  #
  # Check if the user is logged-in to protvplus.ro
  #
  # Parameters:
  #      NAME: Logger name to use for sending the log messages
  #      COOKIEJAR: The cookiejar to be used with the given session
  #      SESSION: The session to be used for login
  #
  # Return: dict variable with authentication details
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  
  # Setup headers for the request
  MyHeaders = {
    'Host': 'protvplus.ro',
    'User-Agent': common_vars.__protvplus_userAgent__,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
  }

  common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: https://protvplus.ro/api/v1/user/check')
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get('https://protvplus.ro/api/v1/user/check', headers=MyHeaders)
  
  # Save cookies for later use.
  COOKIEJAR.save(ignore_discard=True)
  
  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

  if _request_.status_code == 401:
    _api_response_ = json.loads(_request_.content.decode())
    common_vars.__logger__.debug('_api_response_ = ' + str(_api_response_))

    _return_data_ = _api_response_
  
  else:
    _return_data_ = {}
    _api_response_ = json.loads(_request_.content.decode())
    common_vars.__logger__.debug('_api_response_ = ' + str(_api_response_))
    
    _return_data_['status'] = 'authorized'
    _return_data_['data'] = _api_response_['data']
    common_vars.__logger__.debug('Created: _return_data_ = ' + str(_return_data_))

  common_vars.__logger__.debug('Exit function')
  return _return_data_

def do_login(NAME, COOKIEJAR, SESSION):
  ####
  #
  # Login to protvplus.ro for the given session.
  #
  # Parameters:
  #      NAME: Logger name to use for sending the log messages
  #      COOKIEJAR: The cookiejar to be used with the given session
  #      SESSION: The session to be used for login
  #
  # Return: dict variable with authentication details
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  _auth_check_1_ = do_auth_check(NAME, COOKIEJAR, SESSION)
  common_vars.__logger__.debug('_auth_check_1_ = ' + str(_auth_check_1_))
  
  if _auth_check_1_['status'] == "unauthorized":
    common_vars.__logger__.info('Not authenticated.')
    
    
    MyHeaders = {
     'Host': 'protvplus.ro',
     'User-Agent': common_vars.__protvplus_userAgent__,
     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
     'Accept-Language': 'en-US',
     'Accept-Encoding': 'identity',
     'Content-Type': 'application/x-www-form-urlencoded',
     'Connection': 'keep-alive',
     'Upgrade-Insecure-Requests': '1',
     'Cache-Control': 'max-age=0'
    }

    # Setup form data to be sent
    MyFormData = {
     'email': common_vars.__config_protvplus_Username__,
     'password': common_vars.__config_protvplus_Password__,
     '_do': 'content11374-loginForm-form-submit' 
    }

    MyFormData_logger = {
     'email': common_vars.__config_protvplus_Username__,
     'password': '****************',
     '_do': 'content11374-loginForm-form-submit'
    }

    common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
    common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
    common_vars.__logger__.debug('MyFormData: ' + str(MyFormData_logger))
    common_vars.__logger__.debug('URL: https://protvplus.ro/login')
    common_vars.__logger__.debug('Method: POST')

    # Send the POST request
    _request_ = SESSION.post('https://protvplus.ro/login', headers=MyHeaders, data=MyFormData, allow_redirects=False)

    # Save cookies for later use.
    COOKIEJAR.save(ignore_discard=True)

    common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
    common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
    common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
    common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

    _auth_check_2_ = do_auth_check(NAME, COOKIEJAR, SESSION)
    common_vars.__logger__.debug('_auth_check_2_ = ' + str(_auth_check_2_))

    if _auth_check_2_['status'] == "unauthorized":
      common_vars.__logger__.info('Not authorized.')

      common_vars.__logger__.debug('Exit function')
      return _auth_check_2_

    else:
      common_vars.__logger__.info('Authorized.')
      common_vars.__logger__.debug('Exit function')
      return _auth_check_2_
    
  else:
    common_vars.__logger__.info('Already authorized.')  
    common_vars.__logger__.debug('Exit function')
    
    return _auth_check_1_  


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
  
  _auth_ = do_login(NAME, COOKIEJAR, SESSION)
  common_vars.__logger__.debug('_auth_ = ' + str(_auth_))
  
  if _auth_['status'] == "unauthorized":
    common_vars.__logger__.info('[protvplus.ro] => Authentication error => Invalid username or password.')
    xbmcgui.Dialog().ok('[protvplus.ro] => Authentication error', 'Invalid username or password')
    
    common_vars.__logger__.debug('Exit function')
  
  else:
    # Get the URL for the stream metadata

    # Setup headers for the request
    MyHeaders = {
      'Host': 'protvplus.ro',
      'User-Agent': common_vars.__protvplus_userAgent__,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US',
      'Accept-Encoding': 'identity',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Cache-Control': 'max-age=0',
      #'Authorization': 'Bearer ' + _auth_['data']['bearer']
    }

    common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
    common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
    common_vars.__logger__.debug('URL: ' + CHANNEL_ENDPOINT)
    common_vars.__logger__.debug('Method: GET')

    # Send the GET request
    _request_ = SESSION.get(CHANNEL_ENDPOINT, headers=MyHeaders)

    # Save cookies for later use.
    COOKIEJAR.save(ignore_discard=True)

    common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
    common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
    common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
    common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

    _metadata_url_ = re.findall('src="(.+?)\?autoplay', _request_.content.decode(), re.IGNORECASE|re.DOTALL)[0]
    common_vars.__logger__.debug('Found _metadata_url_ = ' + str(_metadata_url_))
    
    _stream_data__host_ = re.findall('//(.+?)/', _metadata_url_, re.IGNORECASE|re.DOTALL)[0]
    common_vars.__logger__.debug('Found _stream_data__host_ = ' + str(_stream_data__host_))

    # Get the stream data
    # Setup headers for the request
    MyHeaders = {
      'Host': _stream_data__host_,
      'Referer': 'https://protvplus.ro',
      'User-Agent': common_vars.__protvplus_userAgent__,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US',
      'Accept-Encoding': 'identity',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Cache-Control': 'max-age=0',
      #'Authorization': 'Bearer ' + _auth_['data']['bearer']
    }

    common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
    common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
    common_vars.__logger__.debug('URL: ' + _metadata_url_)
    common_vars.__logger__.debug('Method: GET')

    # Send the GET request
    _request_ = SESSION.get(_metadata_url_, headers=MyHeaders)

    # Save cookies for later use.
    COOKIEJAR.save(ignore_discard=True)

    common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
    common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
    common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
    common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

    _raw_stream_data_ = re.findall('\'player-1\', (.+?), {"video"', _request_.content.decode(), re.IGNORECASE|re.DOTALL)[0]
    common_vars.__logger__.debug('Found _raw_stream_data_ = ' + str(_raw_stream_data_))
    
    _stream_data_ = json.loads(_raw_stream_data_)
    common_vars.__logger__.debug('_stream_data_ = ' + str(_stream_data_))
    
    _stream_manifest_url_ = _stream_data_['tracks']['HLS'][0]['src']
    common_vars.__logger__.debug('Found _stream_manifest_url_ = ' + _stream_manifest_url_)

    _stream_manifest_host_ = re.findall('//(.+?)/', _stream_manifest_url_, re.IGNORECASE|re.DOTALL)[0]
    common_vars.__logger__.debug('Found _stream_manifest_host_ = ' + _stream_manifest_host_)

    # Set the headers to be used with imputstream.adaptive
    _headers_ = ''
    _headers_ = _headers_ + '&Host=' + _stream_manifest_host_
    _headers_ = _headers_ + '&Origin=https://' + _stream_data__host_
    _headers_ = _headers_ + '&Referer=https://' + _stream_data__host_ + '/'
    _headers_ = _headers_ + '&User-Agent=' + common_vars.__protvplus_userAgent__
    _headers_ = _headers_ + '&Connection=keep-alive'
    _headers_ = _headers_ + '&Accept-Language=en-US'
    _headers_ = _headers_ + '&Accept=*/*'
    _headers_ = _headers_ + '&Accept-Encoding=identity'
    common_vars.__logger__.debug('Created: _headers_ = ' + _headers_)

    # Create a playable item with a path to play.
    # See:  https://github.com/peak3d/inputstream.adaptive/issues/131#issuecomment-375059796
    is_helper = inputstreamhelper.Helper('hls')
    if is_helper.check_inputstream():
      play_item = xbmcgui.ListItem(path=_stream_manifest_url_ + '|' + _headers_)
      play_item.setProperty('inputstream', 'inputstream.adaptive')
      play_item.setProperty('inputstream.adaptive.stream_headers', _headers_)
      play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
      play_item.setMimeType('application/vnd.apple.mpegurl')
      play_item.setContentLookup(False)

      # Pass the item to the Kodi player.
      xbmcplugin.setResolvedUrl(int(common_vars.__handle__), True, listitem=play_item)

  common_vars.__logger__.debug('Exit function')
 

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
  channels = protvplus_functions.get_channels(NAME, COOKIEJAR, SESSION)
  common_vars.__logger__.debug('Received channels = ' + str(channels))

  for channel in channels:
    common_vars.__logger__.debug('Channel data => ' + str(channel))
    common_vars.__logger__.debug('Channel name: ' + channel['name'])
    common_vars.__logger__.debug('Channel url: ' + channel['url'])
    common_vars.__logger__.debug('Channel logo: ' + channel['logo'])
    common_vars.__logger__.debug('Channel ID: ' + channel['id'])
    common_vars.__logger__.debug('Channel data-url: ' + channel['data-url'])

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
    url = common_functions.get_url(action='play', account='protvplus.ro', channel_endpoint=channel['data-url'])
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
  # Get from protvplus.ro the list of channels/streams.
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

  # Setup headers for the request
  MyHeaders = {
    'Host': 'protvplus.ro',
    'User-Agent': common_vars.__protvplus_userAgent__,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
  }

  common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: https://protvplus.ro/tv-live')
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get('https://protvplus.ro/tv-live', headers=MyHeaders)

  # Save cookies for later use.
  COOKIEJAR.save(ignore_discard=True)
  
  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())
  
  _raw_channel_data_ = re.findall('title="TV LIVE(.+?)<nav class="e-navigation">', _request_.content.decode(), re.IGNORECASE|re.DOTALL)
  common_vars.__logger__.debug('Found _raw_channel_data_ = ' + str(_raw_channel_data_))
  
  _raw_channels_ = re.findall('<li>(.+?)</li>', str(_raw_channel_data_), re.IGNORECASE|re.DOTALL)
  common_vars.__logger__.debug('Found _raw_channels_ = ' + str(_raw_channels_))
  
  # Initialize the list of channels
  _channels_ = []

  for _raw_channel_ in _raw_channels_:
    common_vars.__logger__.debug('_raw_channel_ = ' + str(_raw_channel_))

    _channel_record_ = {}

    _channel_name_ = re.findall('title="(.+?)">', _raw_channel_, re.IGNORECASE)[0]
    common_vars.__logger__.debug('_channel_name_ = ' + str(_channel_name_))

    _channel_url_ = re.findall('<a href="(.+?)"', _raw_channel_, re.IGNORECASE)[0]
    common_vars.__logger__.debug('_channel_url_ = ' + str(_channel_url_))

    _channel_logo_ = re.findall('<img src="(.+?)"', _raw_channel_, re.IGNORECASE)[0]
    common_vars.__logger__.debug('_channel_logo_ = ' + str(_channel_logo_))
    
    _channel_id_ = re.findall(_channel_url_ + '" data-channel-id="(.+?)"', _request_.content.decode(), re.IGNORECASE|re.DOTALL)[0]
    common_vars.__logger__.debug('_channel_id_ = ' + str(_channel_id_))

    MyHeaders = {
      'Host': 'protvplus.ro',
      'User-Agent': common_vars.__protvplus_userAgent__,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US',
      'Accept-Encoding': 'identity',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Cache-Control': 'max-age=0'
    }

    common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
    common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
    common_vars.__logger__.debug('URL: ' + str(_channel_url_))
    common_vars.__logger__.debug('Method: GET')

    # Send the GET request
    _request_ = SESSION.get(str(_channel_url_), headers=MyHeaders)

    # Save cookies for later use.
    COOKIEJAR.save(ignore_discard=True)
  
    common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
    common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
    common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
    common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

    _channel_data_url_ = re.findall('data-url="(.+?)">', _request_.content.decode(), re.IGNORECASE|re.DOTALL)[0]
    common_vars.__logger__.debug('Found _channel_data_url_ = ' + str(_channel_data_url_))

    _channel_record_["name"] = _channel_name_
    _channel_record_["url"] = _channel_url_
    _channel_record_["logo"] = _channel_logo_
    _channel_record_["id"] = _channel_id_
    _channel_record_["data-url"] = _channel_data_url_

    common_vars.__logger__.debug('Created: _channel_record_ = ' + str(_channel_record_))
    _channels_.append(_channel_record_)

  common_vars.__logger__.debug('_channels_ = ' + str(_channels_))
  common_vars.__logger__.debug('Exit function')

  return _channels_


def PVRIPTVSimpleClientIntegration_update_m3u_file(M3U_FILE, START_NUMBER, NAME, COOKIEJAR, SESSION):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  
  common_vars.__logger__.debug('M3U_FILE = ' + M3U_FILE)
  common_vars.__logger__.debug('START_NUMBER = ' + str(START_NUMBER))
  
  # Get the list of channels in the category.
  channels = protvplus_functions.get_channels(NAME, COOKIEJAR, SESSION)
  common_vars.__logger__.debug('Received channels = ' + str(channels))
  
  _CHNO_ = START_NUMBER
  _data_file_ = open(M3U_FILE, 'a', encoding='utf-8')
  
  for channel in channels:
    _line_ = "#EXTINF:0 tvg-id=\"protvplus__" + str(channel['id']) + "\" tvg-name=\"" + channel['name'] + "\" tvg-logo=\"" + channel['logo'] + "\" tvg-chno=\"" + str(_CHNO_) + "\" group-title=\"PRO TV PLUS\"," + channel['name']
    
    _url_ = common_functions.get_url(action='play', account='protvplus.ro', channel_endpoint=channel['data-url'])
    _play_url_ = "plugin://" + common_vars.__AddonID__ + "/" + _url_

    _data_file_.write(_line_ + "\n")
    _data_file_.write(_play_url_ + "\n")
        
    _CHNO_ = _CHNO_ + 1
    
  _data_file_.close()

  common_vars.__logger__.debug('Exit function')
  
  return _CHNO_
  

def PVRIPTVSimpleClientIntegration_update_EPG_file(XML_FILE, NAME, COOKIEJAR, SESSION):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  
  common_vars.__logger__.debug('XML_FILE = ' + XML_FILE)

  # Get the list of channels in the category.
  channels = protvplus_functions.get_channels(NAME, COOKIEJAR, SESSION)
  common_vars.__logger__.debug('Received channels = ' + str(channels))

  epg = protvplus_functions.get_epg_data(NAME, COOKIEJAR, SESSION)
  common_vars.__logger__.debug('Received epg = ' + str(epg))

  _data_file_ = open(XML_FILE, 'a', encoding='utf-8')

  for channel in channels:
     #common_vars.__logger__.debug('Channel name = ' + channel['name'])
     #common_vars.__logger__.debug('Channel url = ' + channel['url'])
     #common_vars.__logger__.debug('Channel logo = ' + channel['logo'])
     #common_vars.__logger__.debug('Channel id = ' + channel['id'])
     #common_vars.__logger__.debug('Channel data-url = ' + channel['data-url'])

     _line_ = "  <channel id=\"protvplus__" + channel['id'] + "\">"
     _data_file_.write(_line_ + "\n")
     _line_ = "    <display-name>" + channel['name'] + "</display-name>"
     _data_file_.write(_line_ + "\n")
     _line_ = "  </channel>"
     _data_file_.write(_line_ + "\n")
     
     for program in epg[channel['id']]:

       ###### Probably there is a better way to deal with this ######
       program['start_at'] = re.sub('-', '', program['start_at'], flags=re.IGNORECASE)
       program['start_at'] = re.sub('T', '', program['start_at'], flags=re.IGNORECASE)
       program['start_at'] = re.sub(':', '', program['start_at'], flags=re.IGNORECASE)
       program['start_at'] = re.sub('\+', ' +', program['start_at'], flags=re.IGNORECASE)

       program['end_at'] = re.sub('-', '', program['end_at'], flags=re.IGNORECASE)
       program['end_at'] = re.sub('T', '', program['end_at'], flags=re.IGNORECASE)
       program['end_at'] = re.sub(':', '', program['end_at'], flags=re.IGNORECASE)
       program['end_at'] = re.sub('\+', ' +', program['end_at'], flags=re.IGNORECASE)
       ###### Probably there is a better way to deal with this ######

       _line_ = "  <programme start=\"" + program['start_at'] + "\" stop=\"" + program['end_at'] + "\" channel=\"protvplus__" + channel['id'] + "\">"
       _data_file_.write(_line_ + "\n")

       # Replace unwanted characters in the program name
       program['title'] = re.sub('&nbsp;', ' ', program['title'], flags=re.IGNORECASE)
       program['title'] = re.sub('&apos;', '\'', program['title'], flags=re.IGNORECASE)
       _line_ = "    <title>" + program['title'] + "</title>"
       _data_file_.write(_line_ + "\n")

       # Replace unwanted characters in the program description
       program['short_description'] = re.sub('&nbsp;', ' ', program['short_description'], flags=re.IGNORECASE)
       program['short_description'] = re.sub('&apos;', '\'', program['short_description'], flags=re.IGNORECASE)
       program['description'] = re.sub('&nbsp;', ' ', program['description'], flags=re.IGNORECASE)
       program['description'] = re.sub('&apos;', '\'', program['description'], flags=re.IGNORECASE)
       
       _line_ = "    <desc>" + program['short_description'] + "\n\n    " + program['description'] + "\n    </desc>"
       _data_file_.write(_line_ + "\n")

       _line_ = "  </programme>"
       _data_file_.write(_line_ + "\n")
       
  _data_file_.close

  common_vars.__logger__.debug('Exit function')



def get_epg_data(NAME, COOKIEJAR, SESSION):
  ####
  #
  # Get from protvplus.ro the EPG data.
  #
  # Parameters:
  #      NAME: Logger name to use for sending the log messages
  #      COOKIEJAR: The cookiejar to be used with the given session
  #      SESSION: The session to be used for this call
  #
  # Return: A dict object containing the EPG data
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  # Setup headers for the request
  MyHeaders = {
    'Host': 'protvplus.ro',
    'User-Agent': common_vars.__protvplus_userAgent__,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
  }

  common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: https://protvplus.ro/tv-program')
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get('https://protvplus.ro/tv-program', headers=MyHeaders)

  # Save cookies for later use.
  COOKIEJAR.save(ignore_discard=True)
  
  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())
  
  _raw_epg_data_ = re.findall('EPG_program = (.+?);\n', _request_.content.decode(), re.IGNORECASE|re.DOTALL)[0]
  common_vars.__logger__.debug('Found _raw_epg_data_ = ' + str(_raw_epg_data_))

  _epg_data_ = json.loads(_raw_epg_data_)

  common_vars.__logger__.debug('Exit function')
  
  return _epg_data_

