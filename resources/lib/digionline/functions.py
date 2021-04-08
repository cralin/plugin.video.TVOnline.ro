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
from datetime import datetime
from datetime import timedelta
import time
import json
import inputstreamhelper
import resources.lib.common.vars as common_vars
import resources.lib.common.functions as common_functions
import resources.lib.digionline.functions as digionline_functions


def init_AddonCookieJar(NAME, DATA_DIR):
  ####
  #
  # Initialize the common_vars.__digionline_CookieJar__ variable.
  #
  # Parameters:
  #      NAME: common_vars.__logger__ name to use for sending the log messages
  #      DATA_DIR: The addon's 'userdata' directory.
  #
  ####

  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  # File containing the session cookies
  cookies_file = os.path.join(DATA_DIR, common_vars.__digionline_CookiesFilename__)
  common_vars.__logger__.debug('[ Addon cookies file ] cookies_file = ' + str(cookies_file))
  common_vars.__digionline_CookieJar__ = http.cookiejar.MozillaCookieJar(cookies_file)

  # If it doesn't exist already, create a new file where the cookies should be saved
  if not os.path.exists(cookies_file):
    common_vars.__digionline_CookieJar__.save()
    common_vars.__logger__.debug('[ Addon cookiefile ] Created cookiejar file: ' + str(cookies_file))

  # Load any cookies saved from the last run
  common_vars.__digionline_CookieJar__.load(ignore_expires=True, ignore_discard=True)
  common_vars.__logger__.debug('[ Addon cookiejar ] Loaded cookiejar from file: ' + str(cookies_file))


def do_login(NAME, COOKIEJAR, SESSION):
  ####
  #
  # Login to Digionline.ro for the given session.
  #
  # Parameters:
  #      NAME: Logger name to use for sending the log messages
  #      COOKIEJAR: The cookiejar to be used with the given session
  #      SESSION: The session to be used for login
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  # Authentication to DigiOnline is done in two stages:
  # 1 - Send a GET request to https://www.digionline.ro/auth/login ('DOSESSV3PRI' session cookie will be set)
  # 2 - Send a PUT request to https://www.digionline.ro/auth/login with the credentials in the form-encoded data ('deviceId' cookie will be set)

  common_vars.__logger__.debug('============== Stage 1: Start ==============')
  # Setup headers for the first request
  MyHeaders = {
    'Host': 'www.digionline.ro',
    'User-Agent': common_vars.__userAgent__,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
  }

  common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: https://www.digionline.ro/auth/login')
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get('https://www.digionline.ro/auth/login', headers=MyHeaders)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())
  common_vars.__logger__.debug('============== Stage 1: End ==============')

  # Save cookies for later use.
  COOKIEJAR.save(ignore_expires=True, ignore_discard=True)

  common_vars.__logger__.debug('============== Stage 2: Start ==============')

  # Setup headers for second request
  MyHeaders = {
    'Host': 'www.digionline.ro',
    'Origin': 'https://www.digionline.ro',
    'Referer': 'https://www.digionline.ro/auth/login',
    'User-Agent': common_vars.__userAgent__,
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
    'form-login-email': common_vars.__config_digionline_Username__,
    'form-login-password': common_vars.__config_digionline_Password__
  }

  MyFormData_logger = {
    'form-login-email': common_vars.__config_digionline_Username__,
    'form-login-password': '****************'
  }

  common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('MyFormData: ' + str(MyFormData_logger))
  common_vars.__logger__.debug('URL: https://www.digionline.ro/auth/login')
  common_vars.__logger__.debug('Method: POST')

  # Send the POST request
  _request_ = SESSION.post('https://www.digionline.ro/auth/login', headers=MyHeaders, data=MyFormData)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())
  common_vars.__logger__.debug('============== Stage 2: End ==============')

  # Authentication error.
  if re.search('<div class="form-error(.+?)>', _request_.content.decode(), re.IGNORECASE):
    common_vars.__logger__.debug('\'form-error\' found.')

    _ERR_SECTION_ = re.findall('<div class="form-error(.+?)>\n(.+?)<\/div>', _request_.content.decode(), re.IGNORECASE|re.DOTALL)[0][1].strip()
    _auth_error_message_ = re.sub('&period;', '.', _ERR_SECTION_, flags=re.IGNORECASE)
    _auth_error_message_ = re.sub('&abreve;', 'ă', _auth_error_message_, flags=re.IGNORECASE)

    common_vars.__logger__.info('[digionline.ro] => Authentication error => Error message: '+ _auth_error_message_)

    common_vars.__logger__.debug('_ERR_SECTION_ = ' + str(_ERR_SECTION_))
    common_vars.__logger__.debug('_auth_error_message_ = ' + _auth_error_message_)
    common_vars.__logger__.debug('[digionline.ro] => Authentication error => Error message: '+ _auth_error_message_)

    _auth_status_ = {}
    _auth_status_['exit_code'] = 1
    _auth_status_['error_message'] = _auth_error_message_

    common_vars.__logger__.debug('_auth_status_ = ' + str(_auth_status_))
    common_vars.__logger__.debug('Exit function')

  else:
    common_vars.__logger__.debug('\'form-error\' not found.')

    common_vars.__logger__.info('Authentication successfull')

    # Save cookies for later use.
    COOKIEJAR.save(ignore_expires=True, ignore_discard=True)

    _auth_status_ = {}
    _auth_status_['exit_code'] = 0
    _auth_status_['error_message'] = ''

    common_vars.__logger__.debug('_auth_status_ = ' + str(_auth_status_))
    common_vars.__logger__.debug('Exit function')

  return _auth_status_

def list_categories(NAME, COOKIEJAR, SESSION, DATA_DIR):
  ####
  #
  # Create the list of video categories in the Kodi interface.
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  # Set plugin category.
  xbmcplugin.setPluginCategory(int(common_vars.__handle__), 'DigiOnline.ro')

  # Set plugin content.
  xbmcplugin.setContent(int(common_vars.__handle__), 'videos')

  # Get video categories
  categories = digionline_functions.get_cached_categories(NAME, COOKIEJAR, SESSION, DATA_DIR)
  common_vars.__logger__.debug('Received categories = ' + str(categories))

  if categories['status']['exit_code'] != 0:
    common_vars.__logger__.debug('categories[\'status\'][\'exit_code\'] = ' + str(categories['status']['exit_code']))
    xbmcgui.Dialog().ok('[digionline.ro] => Authentication error', categories['status']['error_message'])

    common_vars.__logger__.debug('Exit function')
    #xbmc.executebuiltin("XBMC.Container.Update(path,replace)")

  else:
    for category in categories['cached_categories']:
      common_vars.__logger__.info('Category:  Name = \'' + category['name'] + '\', Title = \'' + category['title'] + '\'')

      # Create a list item with a text label and a thumbnail image.
      list_item = xbmcgui.ListItem(label=category['title'])

      # Set additional info for the list item.
      # For available properties see https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
      # 'mediatype' is needed for a skin to display info for this ListItem correctly.
      list_item.setInfo('video', {'title': category['title'],
                                  'genre': category['title'],
                                  'mediatype': 'video'})

      # Create a URL for a plugin recursive call.
      # Example: plugin://plugin.video.example/?action=listing&category=filme
      url = common_functions.get_url(action='list_channels', account='digionline.ro', category=category['name'])
      common_vars.__logger__.debug('URL for plugin recursive call: ' + url)

      # This means that this item opens a sub-list of lower level items.
      is_folder = True

      # Add our item to the Kodi virtual folder listing.
      xbmcplugin.addDirectoryItem(int(common_vars.__handle__), url, list_item, is_folder)

    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # See: https://romanvm.github.io/Kodistubs/_autosummary/xbmcplugin.html
    xbmcplugin.addSortMethod(int(common_vars.__handle__), xbmcplugin.SORT_METHOD_LABEL)

    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(int(common_vars.__handle__))

    common_vars.__logger__.debug('Exit function')


def get_cached_categories(NAME, COOKIEJAR, SESSION, DATA_DIR):
  ####
  #
  # Get the list of cached video categories.
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

  _return_data_ = {}
  _return_data_['status'] = {'exit_code': 0, 'error_message': ''}
  _return_data_['cached_categories'] = ''

  _cached_data_file_ = os.path.join(DATA_DIR, common_vars.__digionline_cache_dir__, common_vars.__categoriesCachedDataFilename__)
  common_vars.__logger__.debug('Cached data file: ' + _cached_data_file_)

  if os.path.exists(_cached_data_file_) and os.path.getsize(_cached_data_file_) != 0:
    # The data file with cached categories exists and is not empty.
    
    # Get the value (seconds since epoch) of the last modification time for the file containing cached data.
    _last_update_ = os.path.getmtime(_cached_data_file_)
    common_vars.__logger__.debug('Cached data file last update: ' + time.strftime("%Y%m%d_%H%M%S", time.gmtime(_last_update_)))
    
    if _last_update_ > time.time() - common_vars.__categoriesCachedDataRetentionInterval__:
      # Cached data is not yet expired.
      common_vars.__logger__.debug('Read cached categories from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _return_data_['cached_categories'] = json.load(_data_file_)
      _data_file_.close()

    else:
      # Cached data is expired.
      # Call the function to update the cached data
      common_vars.__logger__.debug('Cached data requires update.')

      # Login to DigiOnline for this session
#      login = digionline_functions.do_login(NAME, COOKIEJAR, SESSION)

#      if login['exit_code'] != 0:
      if 0 != 0:
        common_vars.__logger__.debug('[digionline.ro] => Authentication error => Error message: '+ login['error_message'])
        _return_data_['status']['exit_code'] = login['exit_code']
        _return_data_['status']['error_message'] = login['error_message']

      else: 
        digionline_functions.update_cached_categories(NAME, COOKIEJAR, SESSION, DATA_DIR)

        common_vars.__logger__.debug('Read cached categories from data file: ' + _cached_data_file_)
        _data_file_ = open(_cached_data_file_, 'r')
        _return_data_['cached_categories'] = json.load(_data_file_)
        _data_file_.close()

  else:
    # The data file with cached categories does not exist or it is empty.

    # Call the function to update the cached data
    common_vars.__logger__.debug('Cached data file does not exist.')

    # Login to DigiOnline for this session
#    login = digionline_functions.do_login(NAME, COOKIEJAR, SESSION)

#    if login['exit_code'] != 0:
    if 0 != 0:
      common_vars.__logger__.debug('[digionline.ro] => Authentication error => Error message: '+ login['error_message'])
      _return_data_['status']['exit_code'] = login['exit_code']
      _return_data_['status']['error_message'] = login['error_message']      

    else:
      digionline_functions.update_cached_categories(NAME, COOKIEJAR, SESSION, DATA_DIR)

      common_vars.__logger__.debug('Read cached categories from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _return_data_['cached_categories'] = json.load(_data_file_)
      _data_file_.close()

  common_vars.__logger__.debug('_return_data_ = ' + str(_return_data_))
  common_vars.__logger__.debug('Exit function')

  return _return_data_


def update_cached_categories(NAME, COOKIEJAR, SESSION, DATA_DIR):
  ####
  #
  # Updates the file with cached video categories.
  #
  # Parameters:
  #      NAME: Logger name to use for sending the log messages.
  #      COOKIEJAR: The cookiejar to be used with the given session.
  #      SESSION: The session to be used for this call
  #      DATA_DIR: The addon's 'userdata' directory.
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  categories = digionline_functions.get_categories(NAME, COOKIEJAR, SESSION)
  common_vars.__logger__.debug('Received categories = ' + str(categories))

  if not os.path.exists(DATA_DIR + '/' + common_vars.__digionline_cache_dir__ ):
    os.makedirs(DATA_DIR + '/' + common_vars.__digionline_cache_dir__)

  _cache_data_file_ = os.path.join(DATA_DIR, common_vars.__digionline_cache_dir__, common_vars.__categoriesCachedDataFilename__)
  common_vars.__logger__.debug('Cached data file: ' + _cache_data_file_)

  _data_file_ = open(_cache_data_file_, 'w')
  json.dump(categories, _data_file_)
  _data_file_.close()

  common_vars.__logger__.debug('Exit function')


def get_categories(NAME, COOKIEJAR, SESSION):
  ####
  #
  # Get from DigiOnline.ro the list of video categories
  #
  # Parameters:
  #      NAME: Logger name to use for sending the log messages
  #      COOKIEJAR: The cookiejar to be used with the given session
  #      SESSION: The session to be used for this call
  #
  # Return: The list of video categories
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  MyHeaders = {
    'Host': 'www.digionline.ro',
    'Referer': 'https://www.digionline.ro/',
    'User-Agent': common_vars.__userAgent__,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
  }

  common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: https://www.digionline.ro')
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get('https://www.digionline.ro', headers=MyHeaders)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

  # Save cookies for later use.
  COOKIEJAR.save(ignore_expires=True, ignore_discard=True)

  # Get the raw list of categories
  _raw_categories_ = re.findall('<a href=(.+?)class="nav-menu-item-link ">', _request_.content.decode(), re.IGNORECASE)
  common_vars.__logger__.debug('Found: _raw_categories_ = ' + str(_raw_categories_))

  # Cleanup special characters
  #_raw_categories_ = str(_raw_categories_).replace('\\xc8\\x98', 'S')
  #_raw_categories_ = str(_raw_categories_).replace('\\xc4\\x83', 'a')
  #common_vars.__logger__.debug('Cleaned-up _raw_categories_ = ' + str(_raw_categories_))

  # Build the list of categories names and their titles
  _raw_categories_ = re.findall('"/(.+?)" title="(.+?)"',str(_raw_categories_), re.IGNORECASE)
  common_vars.__logger__.debug('Found: _raw_categories_ = ' + str(_raw_categories_))

  # Initialize the list of categories
  _categories_list_ = []

  for _cat_ in _raw_categories_:
    common_vars.__logger__.info('Found category: ' + _cat_[1])
    _cat_record_ = {}
    _cat_record_["name"] = _cat_[0]
    _cat_record_["title"] = _cat_[1]

    common_vars.__logger__.debug('Created: _cat_record_ = ' + str(_cat_record_))
    _categories_list_.append(_cat_record_)

  common_vars.__logger__.debug('_categories_list_ = ' + str(_categories_list_))

  common_vars.__logger__.debug('Exit function')

  return _categories_list_


def list_channels(category, NAME, COOKIEJAR, SESSION, DATA_DIR):
  ####
  #
  # Create the list of playable videos in the Kodi interface.
  #
  # Parameters:
  #      category: Category name
  #
  ####

  common_vars.__logger__.debug('Enter function')
  common_vars.__logger__.debug('Called with parameters:  Category = ' + category)

  # Set plugin category.
  xbmcplugin.setPluginCategory(int(common_vars.__handle__), category)

  # Set plugin content.
  xbmcplugin.setContent(int(common_vars.__handle__), 'videos')

  # Get the list of videos in the category.
  channels = digionline_functions.get_cached_channels(category, NAME, COOKIEJAR, SESSION, DATA_DIR)
  common_vars.__logger__.debug('Received channels = ' + str(channels))

  if channels['status']['exit_code'] != 0:
    common_vars.__logger__.debug('channels[\'status\'][\'exit_code\'] = ' + str(channels['status']['exit_code']))
    xbmcgui.Dialog().ok('[digionline.ro] => Authentication error', channels['status']['error_message'])

    common_vars.__logger__.debug('Exit function')
    # xbmc.executebuiltin("XBMC.Container.Update(path,replace)")

  else:
    for channel in channels['cached_channels']:
      common_vars.__logger__.debug('Channel data => ' +str(channel))
      common_vars.__logger__.debug('Channel name: ' + channel['name'])
      common_vars.__logger__.debug('Channel logo: ' + channel['logo'])
      common_vars.__logger__.debug('Channel endpoint: ' + channel['endpoint'])
      common_vars.__logger__.debug('Channel metadata: ' + str(channel['metadata']))

      # Create a list item with a text label and a thumbnail image.
      list_item = xbmcgui.ListItem(label=channel['name'])

      _ch_metadata_ = json.loads(channel['metadata'])
      _ch_epg_data_ = json.loads(digionline_functions.get_cached_epg_data(_ch_metadata_['new-info']['meta']['streamId'], common_vars.__AddonID__, SESSION, DATA_DIR))
      common_vars.__logger__.debug('_ch_epg_data_ = ' + str(_ch_epg_data_))

      if _ch_epg_data_:
        common_vars.__logger__.debug('Channel has EPG data')
        common_vars.__logger__.debug('Channel EPG data => [title]: ' + _ch_epg_data_['title'])
        common_vars.__logger__.debug('Channel EPG data => [synopsis]: ' + _ch_epg_data_['synopsis'])

        # Set additional info for the list item.
        # For available properties see https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        if common_vars.__config_ShowTitleInChannelList__ == 'false':
          list_item.setInfo('video', {'title': channel['name'],
                                      'genre': category,
                                      'plotoutline': _ch_epg_data_['title'],
                                      'plot': _ch_epg_data_['synopsis'],
                                      'mediatype': 'video'})

        else:
          list_item.setInfo('video', {'title': channel['name'] + '  [ ' + _ch_epg_data_['title'] + ' ]',
                                      'genre': category,
                                      'plotoutline': _ch_epg_data_['title'],
                                      'plot': _ch_epg_data_['synopsis'],
                                      'mediatype': 'video'})

      else:
        common_vars.__logger__.debug('Channel does not have EPG data')

        list_item.setInfo('video', {'title': channel['name'],
                                    'genre': category,
                                    'mediatype': 'video'})


      # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
      list_item.setArt({'thumb': channel['logo']})

      # Set 'IsPlayable' property to 'true'.
      # This is mandatory for playable items!
      list_item.setProperty('IsPlayable', 'true')

      # Create a URL for a plugin recursive call.
      # Example: plugin://plugin.video.example/?action=play&channel_endpoint=/filme/tnt&channel_metadata=...
      url = common_functions.get_url(action='play', account='digionline.ro', channel_endpoint=channel['endpoint'], channel_metadata=channel['metadata'])
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


def get_cached_channels(category, NAME, COOKIEJAR, SESSION, DATA_DIR):
  ####
  #
  # Get the cached list of channels/streams.
  #
  # Parameters:
  #      category: Category name
  #      NAME: Logger name to use for sending the log messages.
  #      COOKIEJAR: The cookiejar to be used with the given session.
  #      SESSION: The session to be used for this call
  #      DATA_DIR: The addon's 'userdata' directory.
  #
  # Return: The list of cached channels/streams in the given category
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  _return_data_ = {}
  _return_data_['status'] = {'exit_code': 0, 'error_message': ''}
  _return_data_['cached_channels'] = ''

  _cached_data_file_ = os.path.join(DATA_DIR, common_vars.__digionline_cache_dir__, 'channels__' + category + '__.json')
  common_vars.__logger__.debug('Cached data file: ' + _cached_data_file_)

  if os.path.exists(_cached_data_file_) and os.path.getsize(_cached_data_file_) != 0:
    # The data file with cached channels exists and is not empty.
    
    # Get the value (seconds since epoch) of the last modification time for the file containing cached data.
    _last_update_ = os.path.getmtime(_cached_data_file_)
    common_vars.__logger__.debug('Cached data file last update: ' + time.strftime("%Y%m%d_%H%M%S", time.gmtime(_last_update_)))
    
    if _last_update_ > time.time() - common_vars.__channelsCachedDataRetentionInterval__:
      # Cached data is not yet expired.
      common_vars.__logger__.debug('Read cached channels from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _return_data_['cached_channels'] = json.load(_data_file_)
      _data_file_.close()

    else:
      # Cached data is expired.
      # Call the function to update the cached data
      common_vars.__logger__.debug('Cached data requires update.')

      # Login to DigiOnline for this session
#      login = digionline_functions.do_login(NAME, COOKIEJAR, SESSION)

#      if login['exit_code'] != 0:
      if 0 != 0:
        common_vars.__logger__.debug('[digionline.ro] => Authentication error => Error message: '+ login['error_message'])
        _return_data_['status']['exit_code'] = login['exit_code']
        _return_data_['status']['error_message'] = login['error_message']

      else: 
        digionline_functions.update_cached_channels(category, NAME, COOKIEJAR, SESSION, DATA_DIR)

        common_vars.__logger__.debug('Read cached channels from data file: ' + _cached_data_file_)
        _data_file_ = open(_cached_data_file_, 'r')
        _return_data_['cached_channels'] = json.load(_data_file_)
        _data_file_.close()

  else:
    # The data file with cached categories does not exist or it is empty.

    # Call the function to update the cached data
    common_vars.__logger__.debug('Cached data file does not exist.')

    # Login to DigiOnline for this session
#    login = digionline_functions.do_login(NAME, COOKIEJAR, SESSION)

#    if login['exit_code'] != 0:
    if 0 != 0:
      common_vars.__logger__.debug('[digionline.ro] => Authentication error => Error message: '+ login['error_message'])
      _return_data_['status']['exit_code'] = login['exit_code']
      _return_data_['status']['error_message'] = login['error_message']      

    else:
      digionline_functions.update_cached_channels(category, NAME, COOKIEJAR, SESSION, DATA_DIR)

      common_vars.__logger__.debug('Read cached channels from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _return_data_['cached_channels'] = json.load(_data_file_)
      _data_file_.close()

  common_vars.__logger__.debug('_return_data_ = ' + str(_return_data_))
  common_vars.__logger__.debug('Exit function')

  return _return_data_


def get_channels(category, NAME, COOKIEJAR, SESSION):
  ####
  #
  # Get from DigiOnline.ro the list of channels/streams.
  #
  # Parameters:
  #      category: Category name
  #      NAME: Logger name to use for sending the log messages
  #      COOKIEJAR: The cookiejar to be used with the given session
  #      SESSION: The session to be used for this call
  #
  # Return: The list of channels/streams in the given category
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  common_vars.__logger__.debug('Called with parameters:  category = ' + category)

  common_vars.__logger__.info('Looking for channels in category: ' + category)
  common_vars.__logger__.debug('Looking for channels in category: ' + category)

  # Get the list of channels in this category
  MyHeaders = {
    'Host': 'www.digionline.ro',
    'Referer': 'https://www.digionline.ro/',
    'User-Agent': common_vars.__userAgent__,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
  }

  common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: https://www.digionline.ro/' + category)
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get('https://www.digionline.ro/' + category, headers=MyHeaders)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

  # Save cookies for later use.
  COOKIEJAR.save(ignore_expires=True, ignore_discard=True)

  _raw_channel_boxes_ = re.findall('<div class="box-container">(.+?)<figcaption>', _request_.content.decode(), re.IGNORECASE|re.DOTALL)
  common_vars.__logger__.debug('Found _raw_channel_boxes = ' + str(_raw_channel_boxes_))

  # Initialize the list of channels
  _channels_ = []

  for _raw_channel_box_ in _raw_channel_boxes_:
    common_vars.__logger__.debug('_raw_channel_box_ = ' + str(_raw_channel_box_))

    _channel_record_ = {}

    _channel_endpoint_ = re.findall('<a href="(.+?)" class="box-link"></a>', _raw_channel_box_, re.IGNORECASE)
    _channel_endpoint_ = _channel_endpoint_[0]
    common_vars.__logger__.debug('Found: _channel_endpoint_ = ' + _channel_endpoint_)

    _channel_logo_ = re.findall('<img src="(.+?)" alt="logo">', _raw_channel_box_, re.IGNORECASE)
    _channel_logo_ = _channel_logo_[0]
    common_vars.__logger__.debug('Found: _channel_logo_ = ' + _channel_logo_)

    # Get additional details of the current channel
    MyHeaders = {
      'Host': 'www.digionline.ro',
      'Referer': 'https://www.digionline.ro/' + category,
      'User-Agent': common_vars.__userAgent__,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US',
      'Accept-Encoding': 'identity',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Cache-Control': 'max-age=0'
    }

    common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
    common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
    common_vars.__logger__.debug('URL: https://www.digionline.ro' + _channel_endpoint_)
    common_vars.__logger__.debug('Method: GET')

    # Send the GET request
    _request_ = SESSION.get('https://www.digionline.ro' + _channel_endpoint_, headers=MyHeaders)

    common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
    common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
    common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
    common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

    # Save cookies for later use.
    COOKIEJAR.save(ignore_expires=True, ignore_discard=True)

    _raw_channel_details_box_ = re.findall('<div class="entry-video video-player(.+?)</div>', _request_.content.decode(), re.IGNORECASE|re.DOTALL)
    if not _raw_channel_details_box_:
      _raw_channel_details_box_ = re.findall('<div class="video-player entry-video(.+?)</div>', _request_.content.decode(), re.IGNORECASE|re.DOTALL)

    common_vars.__logger__.debug('_raw_channel_details_box_ = ' + str(_raw_channel_details_box_))

    _channel_details_box_ = _raw_channel_details_box_[0]
    _channel_details_box_ = _channel_details_box_.replace('\n', '')
    _channel_details_box_ = _channel_details_box_.strip()
    common_vars.__logger__.debug('_channel_details_box_ = ' + _channel_details_box_)

    _channel_metadata_ = re.findall('<script type="text/template">(.+?)</script>', _channel_details_box_, re.IGNORECASE)
    _channel_metadata_ = _channel_metadata_[0].strip()
    common_vars.__logger__.debug('Found: _channel_metadata_ = ' + str(_channel_metadata_))

    _ch_meta_ = json.loads(_channel_metadata_)
    common_vars.__logger__.info('Found channel: ' + _ch_meta_['new-info']['meta']['channelName'])
    common_vars.__logger__.debug('Found: _channel_name_ = ' + _ch_meta_['new-info']['meta']['channelName'])
    common_vars.__logger__.debug('Found: _channel_streamId_ = ' + str(_ch_meta_['new-info']['meta']['streamId']))

    _channel_record_["endpoint"] = _channel_endpoint_
    _channel_record_["name"] = _ch_meta_['new-info']['meta']['channelName']
    _channel_record_["logo"] = _channel_logo_
    _channel_record_["metadata"] = _channel_metadata_

    common_vars.__logger__.debug('Created: _channel_record_ = ' + str(_channel_record_))
    _channels_.append(_channel_record_)

  common_vars.__logger__.debug('_channels_ = ' + str(_channels_))
  common_vars.__logger__.debug('Exit function')

  return _channels_


def update_cached_channels(category, NAME, COOKIEJAR, SESSION, DATA_DIR):
  ####
  #
  # Updates the file with cached video channels for the given category.
  #
  # Parameters:
  #      category: The given category name
  #      NAME: Logger name to use for sending the log messages.
  #      COOKIEJAR: The cookiejar to be used with the given session.
  #      SESSION: The session to be used for this call
  #      DATA_DIR: The addon's 'userdata' directory.
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  channels = digionline_functions.get_channels(category, NAME, COOKIEJAR, SESSION)
  common_vars.__logger__.debug('Received channels = ' + str(channels))

  if not os.path.exists(DATA_DIR + '/' + common_vars.__digionline_cache_dir__ ):
    os.makedirs(DATA_DIR + '/' + common_vars.__digionline_cache_dir__)

  _cache_data_file_ = os.path.join(DATA_DIR, common_vars.__digionline_cache_dir__, 'channels__' + category + '__.json')
  common_vars.__logger__.debug('Cached data file: ' + _cache_data_file_)

  _data_file_ = open(_cache_data_file_, 'w')
  json.dump(channels, _data_file_)
  _data_file_.close()

  common_vars.__logger__.debug('Exit function')




def get_epg_data(STREAM_ID, NAME, SESSION):
  ####
  #
  # Get from DigiOnline.ro the EPG data for the given stream ID
  #
  # Parameters:
  #      STREAM_ID: The ID of the stream
  #      NAME: Logger name to use for sending the log messages
  #      SESSION: The session to be used for this call
  #
  # Return: The EPG data for the given stream
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  # Get the EPG details for the current channel
  MyHeaders = {
    'Host': 'www.digionline.ro',
#    'Referer': 'https://www.digionline.ro/' + _channel_endpoint_,
    'User-Agent': common_vars.__userAgent__,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
  }

#  common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: https://www.digionline.ro/epg-xhr?channelId=' + str(STREAM_ID))
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get('https://www.digionline.ro/epg-xhr?channelId=' + str(STREAM_ID), headers=MyHeaders)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
#  common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

  _epgdata_ = _request_.content.decode()
  common_vars.__logger__.debug('_epgdata_ = ' + _epgdata_)

  common_vars.__logger__.debug('Exit function')

  return _epgdata_


def update_cached_epg_data(STREAM_ID, NAME, SESSION, DATA_DIR):
  ####
  #
  # Updates the file with cached EPG data for the given stream ID.
  #
  # Parameters:
  #      STREAM_ID: ID of the stream
  #      NAME: Logger name to use for sending the log messages.
  #      SESSION: The session to be used for this call
  #      DATA_DIR: The addon's 'userdata' directory.
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  _epg_data_ = get_epg_data(STREAM_ID, NAME, SESSION)
  common_vars.__logger__.debug('Received _epg_data_ = ' + str(_epg_data_))

  if not os.path.exists(DATA_DIR + '/' + common_vars.__digionline_cache_dir__ + '/EPG'):
    os.makedirs(DATA_DIR + '/' + common_vars.__digionline_cache_dir__ + '/EPG')

  _cached_data_file_ = os.path.join(DATA_DIR, common_vars.__digionline_cache_dir__, 'EPG', str(STREAM_ID) + '.json')
  common_vars.__logger__.debug('Cached data file: ' + _cached_data_file_)

  _data_file_ = open(_cached_data_file_, 'w')
  json.dump(_epg_data_, _data_file_)
  _data_file_.close()

  common_vars.__logger__.debug('Exit function')


def get_cached_epg_data(STREAM_ID, NAME, SESSION, DATA_DIR):
  ####
  #
  # Get the cached EPG data for the given streamID.
  #
  # Parameters:
  #      STREAM_ID: ID of the stream
  #      NAME: Logger name to use for sending the log messages.
  #      SESSION: The session to be used for this call
  #      DATA_DIR: The addon's 'userdata' directory.
  #
  # Return: The cached EPG data for the given streamID.
  #
  ####
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  _cached_data_file_ = os.path.join(DATA_DIR, common_vars.__digionline_cache_dir__, 'EPG', str(STREAM_ID) + '.json')
  common_vars.__logger__.debug('Cached data file: ' + _cached_data_file_)

  if os.path.exists(_cached_data_file_) and os.path.getsize(_cached_data_file_) != 0:
    # The data file with cached channels exists and is not empty.
    
    # Get the value (seconds since epoch) of the last modification time for the file containing cached data.
    _last_update_ = os.path.getmtime(_cached_data_file_)
    common_vars.__logger__.debug('Cached data file last update: ' + time.strftime("%Y%m%d_%H%M%S", time.gmtime(_last_update_)))
    
    if _last_update_ > time.time() - common_vars.__EPGDataCachedDataRetentionInterval__:
      # Cached data is not yet expired.
      common_vars.__logger__.debug('Read cached EPG data from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _return_data_ = json.load(_data_file_)
      _data_file_.close()

    else:
      # Cached data is expired.
      # Call the function to update the cached data
      common_vars.__logger__.debug('Cached data requires update.')

      digionline_functions.update_cached_epg_data(STREAM_ID, NAME, SESSION, DATA_DIR)

      common_vars.__logger__.debug('Read cached EPG data from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _return_data_ = json.load(_data_file_)
      _data_file_.close()

  else:
    # The data file with cached categories does not exist or it is empty.

    # Call the function to update the cached data
    common_vars.__logger__.debug('Cached data file does not exist.')

    digionline_functions.update_cached_epg_data(STREAM_ID, NAME, SESSION, DATA_DIR)

    common_vars.__logger__.debug('Read cached EPG data from data file: ' + _cached_data_file_)
    _data_file_ = open(_cached_data_file_, 'r')
    _return_data_ = json.load(_data_file_)
    _data_file_.close()

  common_vars.__logger__.debug('_return_data_ = ' + str(_return_data_))
  common_vars.__logger__.debug('Exit function')

  return _return_data_


def play_video(endpoint, metadata, NAME, COOKIEJAR, SESSION, DATA_DIR):
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

  # Login to DigiOnline for this session
#  login = digionline_functions.do_login(common_vars.__AddonID__, COOKIEJAR, SESSION)

#  if login['exit_code'] != 0:
  if 0 != 0:
    xbmcgui.Dialog().ok('[digionline.ro] => Authentication error', login['error_message'])
    common_vars.__logger__.debug('Exit function')
    xbmc.executebuiltin("XBMC.Container.Update(path,replace)")

  else:
    common_vars.__logger__.debug('Called with parameters: endpoint = ' + endpoint)
    common_vars.__logger__.debug('Called with parameters: metadata = ' + str(metadata))

    # Set a flag so we know whether to enter in the last "if" clause
    known_video_type = 0

    _channel_metadata_ = json.loads(metadata)

    common_vars.__logger__.info('Play channel: ' + _channel_metadata_['new-info']['meta']['channelName'])

    common_vars.__logger__.debug('_channel_metadata_[\'shortcode\'] = ' + _channel_metadata_['shortcode'])

    if _channel_metadata_['shortcode'] == 'livestream':
      common_vars.__logger__.info('Playing a \'livestream\' video.')

      # Set the flag so we won't enter in the last "if" clause
      known_video_type = 1

      # Get the stream data (contains the URL for the stream to be played)
      MyHeaders = {
        'Host': 'www.digionline.ro',
        'Referer': 'https://www.digionline.ro' + endpoint,
        'Origin':  'https://www.digionline.ro',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': common_vars.__userAgent__,
        'Accept': '*/*',
        'Accept-Language': 'en-US',
        'Accept-Encoding': 'identity',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
      }

      MyPostData = {'id_stream': _channel_metadata_['new-info']['meta']['streamId'], 'quality': 'hq'}

      common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
      common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
      common_vars.__logger__.debug('MyPostData: ' + str(MyPostData))
      common_vars.__logger__.debug('URL: https://www.digionline.ro' + _channel_metadata_['new-info']['meta']['streamUrl'])
      common_vars.__logger__.debug('Method: POST')

      # Send the POST request
      _request_ = SESSION.post('https://www.digionline.ro' + _channel_metadata_['new-info']['meta']['streamUrl'], data=MyPostData, headers=MyHeaders)

      common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
      common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
      common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
      common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

      # Save cookies for later use.
      COOKIEJAR.save(ignore_expires=True, ignore_discard=True)

      _stream_data_ = json.loads(_request_.content.decode())
      common_vars.__logger__.debug('_stream_data_ = ' + str(_stream_data_))

      # Get the host needed to be set in the headers
      _headers_host_ = re.findall('//(.+?)/', _stream_data_['stream_url'], re.IGNORECASE)[0]
      common_vars.__logger__.debug('Found: _headers_host_ = ' + _headers_host_)

      # If needed, append the "https:" to the stream_url
      if 'https://' not in _stream_data_['stream_url']:
        _stream_url_ = 'https:' + _stream_data_['stream_url']
        common_vars.__logger__.debug('Created: _stream_url_ = ' + _stream_url_)
      else:
        _stream_url_ = _stream_data_['stream_url']
        common_vars.__logger__.debug('Found: _stream_url_ = ' + _stream_url_)

      # Set the headers to be used with imputstream.adaptive
      _headers_ = ''
      _headers_ = _headers_ + 'Host=' + _headers_host_
      _headers_ = _headers_ + '&User-Agent=' + common_vars.__userAgent__
      _headers_ = _headers_ + '&Referer=' + 'https://www.digionline.ro' + endpoint
      _headers_ = _headers_ + '&Origin=https://www.digionline.ro'
      _headers_ = _headers_ + '&Connection=keep-alive'
      _headers_ = _headers_ + '&Accept-Language=en-US'
      _headers_ = _headers_ + '&Accept=*/*'
      _headers_ = _headers_ + '&Accept-Encoding=identity'
      common_vars.__logger__.debug('Created: _headers_ = ' + _headers_)

      # Create a playable item with a path to play.
      # See:  https://github.com/peak3d/inputstream.adaptive/issues/131#issuecomment-375059796
      is_helper = inputstreamhelper.Helper('hls')
      if is_helper.check_inputstream():
        play_item = xbmcgui.ListItem(path=_stream_url_ + '|' + _headers_)
        play_item.setProperty('inputstream', 'inputstream.adaptive')
        play_item.setProperty('inputstream.adaptive.stream_headers', _headers_)
        play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        play_item.setMimeType('application/vnd.apple.mpegurl')
        play_item.setContentLookup(False)

        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(int(common_vars.__handle__), True, listitem=play_item)

    if _channel_metadata_['shortcode'] == 'nagra-livestream':
      common_vars.__logger__.info('Playing a \'nagra-livestream\' video.')

      # Set the flag so we won't enter in the last if clause
      known_video_type = 1

      for cookie in COOKIEJAR:
        if cookie.name == "deviceId":
          _deviceId_ = cookie.value
          common_vars.__logger__.debug(' _deviceID_ = ' + _deviceId_ )

      # Get the stream data (contains the URL for the stream to be played)
      MyHeaders = {
        'Host': 'www.digionline.ro',
        'Referer': 'https://www.digionline.ro' + endpoint,
        'Origin':  'https://www.digionline.ro',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': common_vars.__userAgent__,
        'Accept': '*/*',
        'Accept-Language': 'en-US',
        'Accept-Encoding': 'identity',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
      }

      MyPostData = {'id_stream': _channel_metadata_['new-info']['meta']['streamId'], 'quality': 'hq', 'id_device': _deviceId_}

      common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
      common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
      common_vars.__logger__.debug('MyPostData: ' + str(MyPostData))
      common_vars.__logger__.debug('URL: https://www.digionline.ro' + _channel_metadata_['new-info']['meta']['streamUrl'])
      common_vars.__logger__.debug('Method: POST')

      # Send the POST request
      _request_ = SESSION.post('https://www.digionline.ro' + _channel_metadata_['new-info']['meta']['streamUrl'], data=MyPostData, headers=MyHeaders)

      common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
      common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
      common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
      common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

      # Save cookies for later use.
      COOKIEJAR.save(ignore_expires=True, ignore_discard=True)

      _stream_data_ = json.loads(_request_.content.decode())
      common_vars.__logger__.debug('_stream_data_ = ' + str(_stream_data_))

      if _stream_data_['error']['error_code'] == 0:
        common_vars.__logger__.debug('_stream_data_[\'error\'][\'error_code\'] = ' + str(_stream_data_['error']['error_code']))

        # Get the host needed to be set in the headers for the manifest file
        _headers_host_ = re.findall('//(.+?)/', _stream_data_['data']['content']['stream.manifest.url'], re.IGNORECASE)[0]
        common_vars.__logger__.debug('Found: _headers_host_ = ' + _headers_host_)

        # If needed, append the "https:" to the stream_url
        if 'https://' not in _stream_data_['data']['content']['stream.manifest.url']:
          _stream_manifest_url_ = 'https:' + _stream_data_['data']['content']['stream.manifest.url']
          common_vars.__logger__.debug('Created: _stream_manifest_url_ = ' + _stream_manifest_url_)
        else:
          _stream_manifest_url_ = _stream_data_['data']['content']['stream.manifest.url']
          common_vars.__logger__.debug('Found: _stream_manifest_url_ = ' + _stream_manifest_url_)

        # Set the headers to be used with imputstream.adaptive
        _headers_ = ''
        _headers_ = _headers_ + 'Host=' + _headers_host_
        _headers_ = _headers_ + '&User-Agent=' + common_vars.__userAgent__
        _headers_ = _headers_ + '&Referer=' + 'https://www.digionline.ro' + endpoint
        _headers_ = _headers_ + '&Origin=https://www.digionline.ro'
        _headers_ = _headers_ + '&Connection=keep-alive'
        _headers_ = _headers_ + '&Accept-Language=en-US'
        _headers_ = _headers_ + '&Accept=*/*'
        _headers_ = _headers_ + '&Accept-Encoding=identity'
        common_vars.__logger__.debug('Created: _headers_ = ' + _headers_)

        # Get the host needed to be set in the headers for the DRM license request
        _lic_headers_host_ = re.findall('//(.+?)/', _stream_data_['data']['content']['widevine.proxy'], re.IGNORECASE)[0]
        common_vars.__logger__.debug('Found: _lic_headers_host_ = ' + _lic_headers_host_)

        # Set the headers to be used when requesting license key
        _lic_headers_ = ''
        _lic_headers_ = _lic_headers_ + 'Host=' + _lic_headers_host_
        _lic_headers_ = _lic_headers_ + '&User-Agent=' + common_vars.__userAgent__
        _lic_headers_ = _lic_headers_ + '&Referer=' + 'https://www.digionline.ro' + endpoint
        _lic_headers_ = _lic_headers_ + '&Origin=https://www.digionline.ro'
        _lic_headers_ = _lic_headers_ + '&Connection=keep-alive'
        _lic_headers_ = _lic_headers_ + '&Accept-Language=en-US'
        _lic_headers_ = _lic_headers_ + '&Accept=*/*'
        _lic_headers_ = _lic_headers_ + '&Accept-Encoding=identity'
        _lic_headers_ = _lic_headers_ + '&verifypeer=false'
        common_vars.__logger__.debug('Created: _lic_headers_ = ' + _lic_headers_)

        # Create a playable item with a path to play.
        ### See:
        ###    https://github.com/peak3d/inputstream.adaptive/wiki
        ###    https://github.com/peak3d/inputstream.adaptive/wiki/Integration
        ###    https://github.com/emilsvennesson/script.module.inputstreamhelper

        is_helper = inputstreamhelper.Helper('mpd', drm='com.widevine.alpha')
        if is_helper.check_inputstream():
          play_item = xbmcgui.ListItem(path=_stream_manifest_url_)
          play_item.setProperty('inputstream', 'inputstream.adaptive')
          play_item.setProperty('inputstream.adaptive.stream_headers', _headers_)
          play_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
          play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
          play_item.setProperty('inputstream.adaptive.license_key', _stream_data_['data']['content']['widevine.proxy'] + '|' + _lic_headers_ + '|R{SSM}|')
          play_item.setMimeType('application/dash+xml')

          # Pass the item to the Kodi player.
          xbmcplugin.setResolvedUrl(int(common_vars.__handle__), True, listitem=play_item)

      else:
        # The DigiOnline.ro account configured in the addon's settings is not entitled to play this stream.
        common_vars.__logger__.debug('_stream_data_[\'error\'][\'error_code\'] = ' + str(_stream_data_['error']['error_code']))
        common_vars.__logger__.debug('_stream_data_[\'error\'][\'error_message\'] = ' + _stream_data_['error']['error_message'])

        common_vars.__logger__.info('[Error code: ' + str(_stream_data_['error']['error_code']) + ']  => ' + _stream_data_['error']['error_message'])
        common_vars.__logger__.debug('[Error code: ' + str(_stream_data_['error']['error_code']) + ']  => ' + _stream_data_['error']['error_message'])

        xbmcgui.Dialog().ok('[Error code: ' + str(_stream_data_['error']['error_code']) + ']', str(_stream_data_['error']['error_message']))

    # A 'catch-all'-type condition to cover for the unknown cases
    if known_video_type == 0:
      common_vars.__logger__.info('Don\'t know (yet ?) how to play a \'' + _channel_metadata_['shortcode'] + '\' video type.')

  common_vars.__logger__.debug('Exit function')


def PVRIPTVSimpleClientIntegration_update_m3u_file(M3U_FILE, START_NUMBER, NAME, COOKIEJAR, SESSION):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  
  common_vars.__logger__.debug('M3U_FILE = ' + M3U_FILE)
  common_vars.__logger__.debug('START_NUMBER = ' + str(START_NUMBER))
  
  _CHNO_ = START_NUMBER

  # Login to DigiOnline for this session
#  login = digionline_functions.do_login(NAME, COOKIEJAR, SESSION)

#  if login['exit_code'] != 0:
  if 0 != 0:
    common_vars.__logger__.debug('[digionline.ro] => Authentication error => Error message: '+ login['error_message'])
    xbmcgui.Dialog().ok('[digionline.ro] => Authentication error', login['error_message'])

  else:
    _data_file_ = open(M3U_FILE, 'a', encoding='utf-8')

    # Get video categories
    categories = digionline_functions.get_categories(NAME, COOKIEJAR, SESSION)
    common_vars.__logger__.debug('Received categories = ' + str(categories))
    
    for category in categories:
      common_vars.__logger__.debug('Category name = ' + category['name'])
      
      # Get the list of channels in the category.
      channels = digionline_functions.get_channels(category['name'], NAME, COOKIEJAR, SESSION)
      common_vars.__logger__.debug('Received channels = ' + str(channels))
      
      for channel in channels:
        common_vars.__logger__.debug('Channel data => ' +str(channel))
        common_vars.__logger__.debug('Channel name: ' + channel['name'])
        common_vars.__logger__.debug('Channel logo: ' + channel['logo'])
        common_vars.__logger__.debug('Channel endpoint: ' + channel['endpoint'])
        common_vars.__logger__.debug('Channel metadata: ' + str(channel['metadata']))
        
        _channel_metadata_ = json.loads(channel['metadata'])
        common_vars.__logger__.debug('Channel streamId: ' + str(_channel_metadata_['new-info']['meta']['streamId']))
        
        _line_ = "#EXTINF:0 tvg-id=\"digionline__" + str(_channel_metadata_['new-info']['meta']['streamId']) + "\" tvg-name=\"" + channel['name'] + "\" tvg-logo=\"" + channel['logo'] + "\" tvg-chno=\"" + str(_CHNO_) + "\" group-title=\"" + category['title'] + "\"," + channel['name']

        _url_ = common_functions.get_url(action='play', account='digionline.ro', channel_endpoint=channel['endpoint'], channel_metadata=channel['metadata'])
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

  _raw_epg_data_ = json.loads(digionline_functions.PVRIPTVSimpleClientIntegration_getEPG_data(NAME, COOKIEJAR, SESSION))
  common_vars.__logger__.debug('_raw_epg_data_ = ' + str(_raw_epg_data_))
  
  # Login to DigiOnline for this session
#  login = digionline_functions.do_login(NAME, COOKIEJAR, SESSION)

#  if login['exit_code'] != 0:
  if 0 != 0:
    common_vars.__logger__.debug('[Authentication error] => Error message: '+ login['error_message'])
    xbmcgui.Dialog().ok('[digionline.ro] => Authentication error', login['error_message'])

  else:
    _data_file_ = open(XML_FILE, 'a', encoding='utf-8')

    # Get video categories
    categories = digionline_functions.get_categories(NAME, COOKIEJAR, SESSION)
    common_vars.__logger__.debug('Received categories = ' + str(categories))
    
    for category in categories:
      common_vars.__logger__.debug('category name = ' + category['name'])
      
      # Get the list of channels in the category.
      channels = digionline_functions.get_channels(category['name'], NAME, COOKIEJAR, SESSION)
      common_vars.__logger__.debug('Received channels = ' + str(channels))
      
      for channel in channels:
        common_vars.__logger__.debug('Channel data => ' +str(channel))
       
        _channel_metadata_ = json.loads(channel['metadata'])
        
        common_vars.__logger__.debug('Channel name: ' + channel['name'])
        common_vars.__logger__.debug('Channel streamId: ' + str(_channel_metadata_['new-info']['meta']['streamId']))

        _line_ = "  <channel id=\"digionline__" + str(_channel_metadata_['new-info']['meta']['streamId']) + "\">"
        _data_file_.write(_line_ + "\n")
        _line_ = "    <display-name>" + channel['name'] + "</display-name>"
        _data_file_.write(_line_ + "\n")
        _line_ = "  </channel>"
        _data_file_.write(_line_ + "\n")
        
        for _ch_data_ in _raw_epg_data_['data']['channels']:
          common_vars.__logger__.debug('streamId = ' + str(_channel_metadata_['new-info']['meta']['streamId']) + '  |  id_channel = ' + str(_ch_data_['id_channel']))
          if int(_ch_data_['id_channel']) == int(_channel_metadata_['new-info']['meta']['streamId']):
            common_vars.__logger__.debug('Channel EPG data: ' + str(_ch_data_))

            if _ch_data_['epg']:
              for _program_data_ in _ch_data_['epg']:
                _start_date_time_object_ = datetime.utcfromtimestamp(int(_program_data_['start_ts']))
                _stop_date_time_object_ = datetime.utcfromtimestamp(int(_program_data_['end_ts']))
                _line_ = "  <programme start=\"" + str(_start_date_time_object_.strftime("%Y%m%d%H%M%S")) + "\" stop=\"" + str(_stop_date_time_object_.strftime("%Y%m%d%H%M%S")) + "\" channel=\"digionline__" + str(_ch_data_['id_channel']) + "\">"
                _data_file_.write(_line_ + "\n")

                # Escape special characters in the program name
                _program_data_['program_name'] = re.sub('<', '&lt;', _program_data_['program_name'], flags=re.IGNORECASE)
                _program_data_['program_name'] = re.sub('>', '&gt;', _program_data_['program_name'], flags=re.IGNORECASE)
                _program_data_['program_name'] = re.sub('&', '&amp;', _program_data_['program_name'], flags=re.IGNORECASE)
                _line_ = "    <title>" + _program_data_['program_name'] + "</title>"
                _data_file_.write(_line_ + "\n")

                # Escape special characters in the program description
                _program_data_['program_description'] = re.sub('<', '&lt;', _program_data_['program_description'], flags=re.IGNORECASE)
                _program_data_['program_description'] = re.sub('>', '&gt;', _program_data_['program_description'], flags=re.IGNORECASE)
                _program_data_['program_description'] = re.sub('&', '&amp;', _program_data_['program_description'], flags=re.IGNORECASE)
                _program_data_['program_description_l'] = re.sub('<', '&lt;', _program_data_['program_description_l'], flags=re.IGNORECASE)
                _program_data_['program_description_l'] = re.sub('>', '&gt;', _program_data_['program_description_l'], flags=re.IGNORECASE)
                _program_data_['program_description_l'] = re.sub('&', '&amp;', _program_data_['program_description_l'], flags=re.IGNORECASE)
                _line_ = "    <desc>" + _program_data_['program_description'] + "\n\n    " + _program_data_['program_description_l'] + "\n    </desc>"
                _data_file_.write(_line_ + "\n")

                _line_ = "  </programme>"
                _data_file_.write(_line_ + "\n")

    _data_file_.close()
    
  common_vars.__logger__.debug('Exit function')


def PVRIPTVSimpleClientIntegration_getEPG_data(NAME, COOKIEJAR, SESSION):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  _url_ = "https://digiapis.rcs-rds.ro/digionline/api/v13/epg.php"
  common_vars.__logger__.debug('URL = ' + str(_url_))

  # Setup headers for the request
  MyHeaders = {
    'Host': 'digiapis.rcs-rds.ro',
    'User-Agent': common_vars.__userAgent__,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'identity',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
  }

  common_vars.__logger__.debug('Cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: ' + str(_url_))
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get(_url_, headers=MyHeaders)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received cookies: ' + str(list(COOKIEJAR)))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

  # Save cookies for later use.
  COOKIEJAR.save(ignore_expires=True, ignore_discard=True)

  common_vars.__logger__.debug('Exit function')
  return _request_.content.decode()
  

