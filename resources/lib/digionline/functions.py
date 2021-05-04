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
import xbmcgui
import xbmcplugin
import xbmcvfs
import xbmcaddon
import os
import logging
import http.cookiejar
import re
from datetime import datetime
from datetime import timedelta
import time
import json
import uuid
import hashlib
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
  common_vars.__digionline_CookieJar__.load()
  common_vars.__logger__.debug('[ Addon cookiejar ] Loaded cookiejar from file: ' + str(cookies_file))


def digionline__check_DefaultUserSettings(NAME):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  __ret__ = 0
  common_vars.__logger__.debug('1. __ret__ = ' + str(__ret__))

  if str(common_vars.__config_digionline_Username__) == "__DEFAULT_USER__":
    __ret__ = 1
    common_vars.__logger__.debug('2. __ret__ = ' + str(__ret__))
  
  if str(common_vars.__config_digionline_Username__) == "":
    __ret__ = 1
    common_vars.__logger__.debug('3. __ret__ = ' + str(__ret__))
      
  if str(common_vars.__config_digionline_Password__) == "__DEFAULT_PASSWORD__":
    __ret__ = 1
    common_vars.__logger__.debug('4. __ret__ = ' + str(__ret__))
  
  if str(common_vars.__config_digionline_Password__) == "":
    __ret__ = 1
    common_vars.__logger__.debug('5. __ret__ = ' + str(__ret__))
     
  if str(common_vars.__config_digionline_DeviceManufacturer__) == "__DEFAULT_DEVICE_MAUFACTURER__":
    __ret__ = 1
    common_vars.__logger__.debug('6. __ret__ = ' + str(__ret__))
  
  if str(common_vars.__config_digionline_DeviceManufacturer__) == "":
    __ret__ = 1
    common_vars.__logger__.debug('7. __ret__ = ' + str(__ret__))
   
  if str(common_vars.__config_digionline_DeviceModel__) == "__DEFAULT_DEVICE_MODEL__":
    __ret__ = 1
    common_vars.__logger__.debug('8. __ret__ = ' + str(__ret__))
  
  if str(common_vars.__config_digionline_DeviceModel__) == "":
    __ret__ = 1
    common_vars.__logger__.debug('9. __ret__ = ' + str(__ret__))
   
  if str(common_vars.__config_digionline_AndroidVersion__) == "__DEFAULT_ANDROID_DEVICE__":
    __ret__ = 1
    common_vars.__logger__.debug('10. __ret__ = ' + str(__ret__))
  
  if str(common_vars.__config_digionline_AndroidVersion__) == "":
    __ret__ = 1
    common_vars.__logger__.debug('11. __ret__ = ' + str(__ret__))

  common_vars.__logger__.debug(' __ret__ = ' + str(__ret__))
  common_vars.__logger__.debug('Exit function')
  
  return __ret__


def digionline__write_stateData(STATE_DATA, NAME, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  __state_file__ = os.path.join(DATA_DIR, common_vars.__digionline_StateFilename__)
  common_vars.__logger__.debug('Writting to \'' + __state_file__ +'\'')
  _file_ = open(__state_file__, 'w')
  json.dump(STATE_DATA, _file_)
  _file_.close()
  

def digionline__read_stateData(NAME, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  __state_file__ = os.path.join(DATA_DIR, common_vars.__digionline_StateFilename__)
  
  if not os.path.exists(__state_file__) or os.path.getsize(__state_file__) == 0:
    common_vars.__logger__.debug('\'' + __state_file__ +'\' does not exist or it is empty.')
    
    _read_data_ = {}
    _read_data_['exit_status'] = 1
    _read_data_['state_data'] = ""
    __ret__ = _read_data_
    
  else:
    common_vars.__logger__.debug('Reading from \'' + __state_file__ +'\'')
    _file_ = open(__state_file__, 'r')
    _data_ = json.load(_file_)
    _file_.close()
    
    _read_data_ = {}
    _read_data_['exit_status'] = 0
    _read_data_['state_data'] = _data_
    __ret__ = _read_data_

  common_vars.__logger__.debug('Return data: ' + str(__ret__))
  common_vars.__logger__.debug('Exit function')
  return __ret__


def digionline__init_stateData(NAME, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  __rsd__ = digionline__read_stateData(NAME, DATA_DIR)
  common_vars.__logger__.debug('__rsd__["exit_status"]: ' + str(__rsd__["exit_status"]))
  
  if __rsd__['exit_status'] != 0:
    common_vars.__logger__.debug('Initializing stateData.')
    
    __registeredUser__ = {}
    __registeredUser__['userName'] = ""
    __registeredUser__['passwordHash'] = ""
    __registeredUser__['receivedHash'] = ""
    __registeredUser__['registeredTS'] = ""

    __state_data__ = {}
    __state_data__['deviceID'] = ""
    __state_data__['deviceManufacturer'] = ""
    __state_data__['deviceModel'] = ""
    __state_data__['androidVersion'] = ""
    __state_data__['registeredUser'] = __registeredUser__
    __state_data__['registeredDeviceID'] = ""
    __state_data__['lastAuthTS'] = ""
    
    digionline__write_stateData(__state_data__, NAME, DATA_DIR)
  
  common_vars.__logger__.debug('Enter function')


def digionline__init(NAME, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  
  digionline_functions.digionline__init_stateData(NAME, DATA_DIR)

  __rsd__ = digionline_functions.digionline__read_stateData(NAME, DATA_DIR)

  if __rsd__['state_data']['deviceID'] == "":
    if digionline_functions.digionline__check_DefaultUserSettings(NAME) != 0:
        common_vars.__logger__.debug('[digionline.ro] => Incomplete configuration => Please configure all fields for digionline.ro account.')
        xbmcgui.Dialog().ok('[digionline.ro] => Incomplete configuration', "Please configure all fields for digionline.ro account.")
        xbmc.executebuiltin("XBMC.Container.Update(path,replace)")
    else:
      __rsd__['state_data']['deviceID'] = digionline_functions.digionline__generateDeviceID(NAME)
      common_vars.__logger__.debug('deviceID = ' + __rsd__['state_data']['deviceID'])
      
      __deviceManufacturer__ = re.sub("\\W", "_", common_vars.__config_digionline_DeviceManufacturer__)
      __deviceManufacturer__ = re.sub("[^\\x00-\\x7F]", "_", __deviceManufacturer__)
      common_vars.__logger__.debug('deviceManufacturer = ' + __deviceManufacturer__)
      __rsd__['state_data']['deviceManufacturer'] = __deviceManufacturer__

      __deviceModel__ = re.sub("\\W", "_", common_vars.__config_digionline_DeviceModel__)
      __deviceModel__ = re.sub("[^\\x00-\\x7F]", "_", __deviceModel__)
      common_vars.__logger__.debug('deviceModel = ' + __deviceModel__)
      __rsd__['state_data']['deviceModel'] = __deviceModel__
      
      __androidVersion__ = re.sub("\\W", "_", common_vars.__config_digionline_AndroidVersion__)
      __androidVersion__ = re.sub("[^\\x00-\\x7F]", "_", __androidVersion__)
      __androidVersion__ = 'REL_' + __androidVersion__
      common_vars.__logger__.debug('__androidVersion__ = ' + __androidVersion__)
      __rsd__['state_data']['androidVersion'] = __androidVersion__

      digionline_functions.digionline__write_stateData(__rsd__['state_data'], NAME, DATA_DIR)

  common_vars.__logger__.debug('Exit function')


def digionline__generateDeviceID(NAME):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  __section_1__ = common_vars.__config_digionline_DeviceManufacturer__ + "_" + common_vars.__config_digionline_DeviceModel__ + "_" + str(int(time.time()))
  __section_1__ = re.sub("\\W", "_", __section_1__)
  __section_1__ = re.sub("[^\\x00-\\x7F]", "_", __section_1__)
  common_vars.__logger__.debug('__section_1__ = ' + __section_1__)
  
  __UUID__ = ""
  for i in range(8):
    __UUID__ = __UUID__ + str(uuid.uuid4())
 
  __section_2__ = __UUID__.replace("-", "")
  common_vars.__logger__.debug('__section_2__ = ' + __section_2__)

  __delta__ = (128 - len(__section_1__) - 1)
  __ret__ = __section_1__ + "_" + __section_2__[:__delta__]
  
  common_vars.__logger__.debug('Generated deviceID = ' + __ret__)
  common_vars.__logger__.debug('Exit function')
  return __ret__


def digionline__isUserRegistered(NAME, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  
  __rsd__ = digionline_functions.digionline__read_stateData(NAME, DATA_DIR)
  _config_pass_hash_ = hashlib.md5(common_vars.__config_digionline_Password__.encode('utf-8')).hexdigest()
  
  if __rsd__['state_data']['registeredUser']['userName'] != common_vars.__config_digionline_Username__ or __rsd__['state_data']['registeredUser']['passwordHash'] != _config_pass_hash_:
    # Not registered
    common_vars.__logger__.debug('Account is not registered.')
    common_vars.__logger__.debug('Exit function')
    return False
  else:
    common_vars.__logger__.debug('Account is registered.')
    common_vars.__logger__.debug('Exit function')
    return True


def digionline__registerUser(NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  __URL__ = 'https://digiapis.rcs-rds.ro/digionline/api/v13/user.php'

  # Setup headers for the request
  MyHeaders = {
    'User-Agent': common_vars.__digionline_API_userAgent__
  }
  
  # Setup parameters for the request
  _config_pass_hash_ = hashlib.md5(common_vars.__config_digionline_Password__.encode('utf-8')).hexdigest()
  
  MyParams = {
    'action': 'registerUser',
    'user': common_vars.__config_digionline_Username__,
    'pass': _config_pass_hash_
  }  

  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: ' + __URL__)
  common_vars.__logger__.debug('Method: GET')
  common_vars.__logger__.debug('Parameters: ' + str(MyParams))

  # Send the GET request
  _request_ = SESSION.get(__URL__, headers=MyHeaders, params=MyParams)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

  _response_ = json.loads(_request_.content.decode())
  
  if _response_['result']['code'] == '200':
    common_vars.__logger__.debug('Received message: ' + str(_response_['data']['message']))
    __rsd__ = digionline_functions.digionline__read_stateData(NAME, DATA_DIR)
    __rsd__['state_data']['registeredUser']['userName'] = common_vars.__config_digionline_Username__
    __rsd__['state_data']['registeredUser']['passwordHash'] = _config_pass_hash_
    __rsd__['state_data']['registeredUser']['receivedHash'] = _response_['data']['h']
    __rsd__['state_data']['registeredUser']['registeredTS'] = time.time()
    common_vars.__logger__.debug('State data: ' + str(__rsd__['state_data']))
    digionline_functions.digionline__write_stateData(__rsd__['state_data'], NAME, DATA_DIR)

  else:
    common_vars.__logger__.debug('Received message: ' + str(_response_['result']['message']))
    xbmcgui.Dialog().ok('[digionline.ro] => Error code ' + str(_response_['result']['code']), str(_response_['result']['message']))
    common_vars.__logger__.debug('Exit function')
    return

  common_vars.__logger__.debug('Exit function')


def digionline__isDeviceRegistered(NAME, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  
  __rsd__ = digionline_functions.digionline__read_stateData(NAME, DATA_DIR)
  
  if __rsd__['state_data']['registeredDeviceID'] != __rsd__['state_data']['deviceID']:
    # Device not registered
    common_vars.__logger__.debug('Device is not registered.')
    common_vars.__logger__.debug('Exit function')
    return False
  else:
    common_vars.__logger__.debug('Device is registered.')
    common_vars.__logger__.debug('Exit function')
    return True

def digionline__registerDevice(NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  __URL__ = 'https://digiapis.rcs-rds.ro/digionline/api/v13/devices.php'

  # Setup headers for the request
  MyHeaders = {
    'User-Agent': common_vars.__digionline_API_userAgent__
  }
  
  __rsd__ = digionline_functions.digionline__read_stateData(NAME, DATA_DIR)
  
  # Setup parameters for the request  
  __c__ = hashlib.md5((__rsd__['state_data']['registeredUser']['userName'] + __rsd__['state_data']['registeredUser']['passwordHash'] + __rsd__['state_data']['deviceID'] + __rsd__['state_data']['deviceManufacturer'] + __rsd__['state_data']['deviceModel'] + __rsd__['state_data']['androidVersion'] + __rsd__['state_data']['registeredUser']['receivedHash']).encode('utf-8')).hexdigest()
  
  MyParams = {
    "action": "registerDevice",
    "user": __rsd__['state_data']['registeredUser']['userName'],
    "pass": __rsd__['state_data']['registeredUser']['passwordHash'],
    "i": __rsd__['state_data']['deviceID'],
    "dma": __rsd__['state_data']['deviceManufacturer'],
    "dmo": __rsd__['state_data']['deviceModel'],
    "o": __rsd__['state_data']['androidVersion'],
    "c": __c__
  }  

  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: ' + __URL__)
  common_vars.__logger__.debug('Method: GET')
  common_vars.__logger__.debug('Parameters: ' + str(MyParams))

  # Send the GET request
  _request_ = SESSION.get(__URL__, headers=MyHeaders, params=MyParams)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

  _response_ = json.loads(_request_.content.decode())
  
  if _response_['result']['code'] == 200:
    common_vars.__logger__.debug('Received message: ' + str(_response_['data']['message']))
    __rsd__['state_data']['registeredDeviceID'] = __rsd__['state_data']['deviceID']
    common_vars.__logger__.debug('State data: ' + str(__rsd__['state_data']))

    digionline_functions.digionline__write_stateData(__rsd__['state_data'], NAME, DATA_DIR)

  else:
    common_vars.__logger__.debug('Received message: ' + str(_response_['result']['message']))
    xbmcgui.Dialog().ok('[digionline.ro] => Error code ' + str(_response_['result']['code']), str(_response_['result']['message']))

  common_vars.__logger__.debug('Exit function')

def digionline__doAuth(NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  # Initialize device data
  digionline_functions.digionline__init(NAME, DATA_DIR)

  if not digionline_functions.digionline__isUserRegistered(NAME, DATA_DIR):
    common_vars.__logger__.debug('Registering user')
    digionline_functions.digionline__registerUser(NAME, SESSION, DATA_DIR)
    
  if digionline_functions.digionline__isUserRegistered(NAME, DATA_DIR) and not digionline__isDeviceRegistered(NAME, DATA_DIR):
    common_vars.__logger__.debug('Registering device')
    digionline_functions.digionline__registerDevice(NAME, SESSION, DATA_DIR)

  else:
    __rsd__ = digionline_functions.digionline__read_stateData(NAME, DATA_DIR)
    common_vars.__logger__.debug('\'' + __rsd__['state_data']['registeredUser']['userName'] + '\' already registered at: ' + time.strftime("%Y%m%d_%H%M%S", time.gmtime(__rsd__['state_data']['registeredUser']['registeredTS'])))

  common_vars.__logger__.debug('Exit function')


def digionline__getStreamDetails(STREAM_ID, NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  __URL__ = 'https://digiapis.rcs-rds.ro/digionline/api/v13/streams_l_3.php'

  # Setup headers for the request
  MyHeaders = {
    'User-Agent': common_vars.__digionline_API_userAgent__
  }
  
  __rsd__ = digionline_functions.digionline__read_stateData(NAME, DATA_DIR)
  
  # Setup parameters for the request  
  MyParams = {
    "action": "getStream",
    "id_stream": STREAM_ID,
    "platform": "Android",
    "version_app": "1.0",
    "i": __rsd__['state_data']['registeredDeviceID'],
    "sn": "ro.rcsrds.digionline",
    "s": "app",
    "quality": "all"
  }  

  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: ' + __URL__)
  common_vars.__logger__.debug('Method: GET')
  common_vars.__logger__.debug('Parameters: ' + str(MyParams))

  # Send the GET request
  _request_ = SESSION.get(__URL__, headers=MyHeaders, params=MyParams)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

  _response_ = json.loads(_request_.content.decode())
  
  common_vars.__logger__.debug('Exit function')
  return _response_


def digionline__getCategoriesChannels(NAME, SESSION):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  
  __URL__ = 'https://digiapis.rcs-rds.ro/digionline/api/v13/categorieschannels.php'

  # Setup headers for the request
  MyHeaders = {
    'User-Agent': common_vars.__digionline_API_userAgent__
  }

  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: ' + __URL__)
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get(__URL__, headers=MyHeaders)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

  __ret__ = _request_.json()
  
  common_vars.__logger__.debug('Exit function')
  return __ret__
  

def digionline__updateCachedCategoriesChannels(NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  _catchan_ = digionline__getCategoriesChannels(NAME, SESSION)
  common_vars.__logger__.debug('Received data = ' + str(_catchan_))

  if not os.path.exists(DATA_DIR + '/' + common_vars.__digionline_cache_dir__ ):
    os.makedirs(DATA_DIR + '/' + common_vars.__digionline_cache_dir__)

  _cache_data_file_ = os.path.join(DATA_DIR, common_vars.__digionline_cache_dir__, common_vars.__digionline_categorieschannelsCachedDataFilename__)
  common_vars.__logger__.debug('Cached data file: ' + _cache_data_file_)

  _data_file_ = open(_cache_data_file_, 'w')
  json.dump(_catchan_, _data_file_)
  _data_file_.close()

  common_vars.__logger__.debug('Exit function')


def digionline__getCachedCategories(NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  _cached_data_file_ = os.path.join(DATA_DIR, common_vars.__digionline_cache_dir__, common_vars.__digionline_categorieschannelsCachedDataFilename__)
  common_vars.__logger__.debug('Cached data file: ' + _cached_data_file_)

  if os.path.exists(_cached_data_file_) and os.path.getsize(_cached_data_file_) != 0:
    # The data file with cached categories exists and is not empty.
    
    # Get the value (seconds since epoch) of the last modification time for the file containing cached data.
    _last_update_ = os.path.getmtime(_cached_data_file_)
    common_vars.__logger__.debug('Cached data file last update: ' + time.strftime("%Y%m%d_%H%M%S", time.gmtime(_last_update_)))
    
    if _last_update_ > time.time() - common_vars.__CachedDataRetentionInterval__:
      # Cached data is not yet expired.
      common_vars.__logger__.debug('Read cached categories from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _catchan_ = json.load(_data_file_)
      _data_file_.close()
      
      __ret__ = _catchan_['data']['categories_list']

    else:
      # Cached data is expired.
      
      # Call the function to update the cached data
      common_vars.__logger__.debug('Cached data requires update.')
      digionline__updateCachedCategoriesChannels(NAME, SESSION, DATA_DIR)

      common_vars.__logger__.debug('Read cached categories from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _catchan_ = json.load(_data_file_)
      _data_file_.close()
      
      __ret__ = _catchan_['data']['categories_list']

  else:
    # The data file with cached categories does not exist or it is empty.

    # Call the function to update the cached data
    common_vars.__logger__.debug('Cached data file does not exist.')
    digionline__updateCachedCategoriesChannels(NAME, SESSION, DATA_DIR)

    common_vars.__logger__.debug('Read cached categories from data file: ' + _cached_data_file_)
    _data_file_ = open(_cached_data_file_, 'r')
    _catchan_ = json.load(_data_file_)
    _data_file_.close()
    
    __ret__ = _catchan_['data']['categories_list']

  common_vars.__logger__.debug('Exit function')

  return __ret__


def digionline__listCategories(NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  # Set plugin category.
  xbmcplugin.setPluginCategory(int(common_vars.__handle__), 'DigiOnline.ro')

  # Set plugin content.
  xbmcplugin.setContent(int(common_vars.__handle__), 'videos')

  # Get video categories
  categories = digionline_functions.digionline__getCachedCategories(NAME, SESSION, DATA_DIR)
  common_vars.__logger__.debug('Received categories = ' + str(categories))

  for category in categories:
    common_vars.__logger__.debug('Category:  id = \'' + str(category['id_category']) + '\', Name = \'' + str(category['category_name']) + '\', Title = \'' + str(category['category_desc']) + '\', Channel list = \'' + str(category['channels_list']) + '\'')

    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label=category['category_desc'])

    # Set additional info for the list item.
    # For available properties see https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
    # 'mediatype' is needed for a skin to display info for this ListItem correctly.
    list_item.setInfo('video', {'title': category['category_desc'],
                                'genre': category['category_desc'],
                                'mediatype': 'video'})

    # Create a URL for a plugin recursive call.
    # Example: plugin://plugin.video.example/?action=listing&category=filme
    url = common_functions.get_url(action='list_channels', account='digionline.ro', category_id=category['id_category'], category_name=category['category_name'], channel_list=json.dumps(category['channels_list']))
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


def digionline__getCachedChannels(NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  _cached_data_file_ = os.path.join(DATA_DIR, common_vars.__digionline_cache_dir__, common_vars.__digionline_categorieschannelsCachedDataFilename__)
  common_vars.__logger__.debug('Cached data file: ' + _cached_data_file_)

  if os.path.exists(_cached_data_file_) and os.path.getsize(_cached_data_file_) != 0:
    # The data file with cached categories and channels exists and is not empty.
    
    # Get the value (seconds since epoch) of the last modification time for the file containing cached data.
    _last_update_ = os.path.getmtime(_cached_data_file_)
    common_vars.__logger__.debug('Cached data file last update: ' + time.strftime("%Y%m%d_%H%M%S", time.gmtime(_last_update_)))
    
    if _last_update_ > time.time() - common_vars.__CachedDataRetentionInterval__:
      # Cached data is not yet expired.
      common_vars.__logger__.debug('Read cached channels from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _catchan_ = json.load(_data_file_)
      _data_file_.close()
      
      __ret__ = _catchan_['data']['channels_list']

    else:
      # Cached data is expired.
      
      # Call the function to update the cached data
      common_vars.__logger__.debug('Cached data requires update.')
      digionline__updateCachedCategoriesChannels(NAME, SESSION, DATA_DIR)

      common_vars.__logger__.debug('Read cached channels from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _catchan_ = json.load(_data_file_)
      _data_file_.close()
      
      __ret__ = _catchan_['data']['channels_list']

  else:
    # The data file with cached categories does not exist or it is empty.

    # Call the function to update the cached data
    common_vars.__logger__.debug('Cached data file does not exist.')
    digionline__updateCachedCategoriesChannels(NAME, SESSION, DATA_DIR)

    common_vars.__logger__.debug('Read cached channels from data file: ' + _cached_data_file_)
    _data_file_ = open(_cached_data_file_, 'r')
    _catchan_ = json.load(_data_file_)
    _data_file_.close()
    
    __ret__ = _catchan_['data']['channels_list']

  common_vars.__logger__.debug('Exit function')

  return __ret__


def digionline__listChannels(CATEGORY_NAME, CHANNEL_LIST, NAME, SESSION, DATA_DIR):

  common_vars.__logger__.debug('Enter function')
  common_vars.__logger__.debug('Called with parameters:  Category name = ' + str(CATEGORY_NAME))
  common_vars.__logger__.debug('Called with parameters:  Channel list = ' + str(CHANNEL_LIST))

  # Set plugin category.
  xbmcplugin.setPluginCategory(int(common_vars.__handle__), CATEGORY_NAME)

  # Set plugin content.
  xbmcplugin.setContent(int(common_vars.__handle__), 'videos')

  # Get the list of all cached channels.
  _cached_channels_ = digionline_functions.digionline__getCachedChannels(NAME, SESSION, DATA_DIR)
  common_vars.__logger__.debug('Received cached channels = ' + str(_cached_channels_))
  
  _channel_list_ = json.loads(CHANNEL_LIST)
  for _chan_ in _channel_list_:
    for channel in _cached_channels_:
      common_vars.__logger__.debug('_chan_ = ' + str(_chan_) + '  id_channel = ' + str(channel['id_channel']))
      if _chan_ == channel['id_channel']:
        common_vars.__logger__.debug('Channel ID => ' + str(channel['id_channel']))
        common_vars.__logger__.debug('Channel name: ' + str(channel['channel_name']))
        common_vars.__logger__.debug('Channel title: ' + str(channel['channel_desc']))
        common_vars.__logger__.debug('Channel logo: ' + str(channel['media_channel']['channel_logo_url']))


        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=channel['channel_desc'])

        # Set additional info for the list item.
        # For available properties see https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for skin to display info for this ListItem correctly.

        list_item.setInfo('video', {'title': channel['channel_desc'],
                                    'genre': CATEGORY_NAME,
                                    'mediatype': 'video'})


        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        list_item.setArt({'thumb': channel['media_channel']['channel_logo_url']})

        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')

        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&channel_endpoint=/filme/tnt&channel_metadata=...
        url = common_functions.get_url(action='play', account='digionline.ro', channel_id=channel['id_channel'])
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


def digionline__playVideo(CHANNEL_ID, NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  common_vars.__logger__.debug('Called with parameters: CHANNEL_ID = ' + str(CHANNEL_ID))
  
  # Authenticate if needed.
  digionline_functions.digionline__doAuth(NAME, SESSION, DATA_DIR)

  _stream_details_ = digionline_functions. digionline__getStreamDetails(CHANNEL_ID, NAME, SESSION, DATA_DIR)
  common_vars.__logger__.debug('Reveived data: ' + str(_stream_details_))
    
  if _stream_details_['error'] != "":
    common_vars.__logger__.debug('[digionline.ro] => ' + _stream_details_['error'])
    xbmcgui.Dialog().ok('[digionline.ro]', _stream_details_['error'])

    common_vars.__logger__.debug('Exit function')
    return

  common_vars.__logger__.debug('Playing a \'' + _stream_details_['stream']['f'] + '\' stream')

  if _stream_details_['stream']['f'] == "hls":
    # Set the headers to be used with imputstream.adaptive
    _headers_ = ''
    _headers_ = _headers_ + '&User-Agent=' + common_vars.__digionline_userAgent__

    common_vars.__logger__.debug('Created: _headers_ = ' + _headers_)

    # Create a playable item with a path to play.
    # See:  https://github.com/peak3d/inputstream.adaptive/issues/131#issuecomment-375059796
    is_helper = inputstreamhelper.Helper('hls')
    if is_helper.check_inputstream():
      play_item = xbmcgui.ListItem(path=_stream_details_['stream']['abr'] + '|' + _headers_)
      play_item.setProperty('inputstream', 'inputstream.adaptive')
      play_item.setProperty('inputstream.adaptive.stream_headers', _headers_)
      play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
      play_item.setMimeType('application/vnd.apple.mpegurl')
      play_item.setContentLookup(False)

      # Pass the item to the Kodi player.
      xbmcplugin.setResolvedUrl(int(common_vars.__handle__), True, listitem=play_item)


  if _stream_details_['stream']['f'] == "dash":
    # Set the headers to be used with imputstream.adaptive
    _headers_ = ''
    _headers_ = _headers_ + '&User-Agent=' + common_vars.__digionline_userAgent__
    common_vars.__logger__.debug('Created: _headers_ = ' + _headers_)

    # Get the host needed to be set in the headers for the DRM license request
    _lic_headers_host_ = re.findall('//(.+?)/', _stream_details_['stream']['abr'], re.IGNORECASE)[0]
    common_vars.__logger__.debug('Found: _lic_headers_host_ = ' + _lic_headers_host_)

    # Set the headers to be used when requesting license key
    _lic_headers_ = ''
    _lic_headers_ = _lic_headers_ + '&User-Agent=' + common_vars.__digionline_userAgent__
#    _lic_headers_ = _lic_headers_ + '&User-Agent=user-agent'
    _lic_headers_ = _lic_headers_ + '&Connection=keep-alive'
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
      play_item = xbmcgui.ListItem(path=_stream_details_['stream']['abr'])
      play_item.setProperty('inputstream', 'inputstream.adaptive')
      play_item.setProperty('inputstream.adaptive.stream_headers', _headers_)
      play_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
      play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
      play_item.setProperty('inputstream.adaptive.license_key', _stream_details_['stream']['proxy'] + '|' + _lic_headers_ + '|R{SSM}|')
      play_item.setMimeType('application/dash+xml')

      # Pass the item to the Kodi player.
      xbmcplugin.setResolvedUrl(int(common_vars.__handle__), True, listitem=play_item)

  common_vars.__logger__.debug('Exit function')



def digionline__getEPG(DATE, NAME, SESSION):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  __URL__ = 'https://digiapis.rcs-rds.ro/digionline/api/v13/epg.php'

  # Setup headers for the request
  MyHeaders = {
    'User-Agent': common_vars.__digionline_API_userAgent__
  }

  MyParams = {
    "date": DATE,
    "duration": "1"
  }  

  common_vars.__logger__.debug('Headers: ' + str(MyHeaders))
  common_vars.__logger__.debug('URL: ' + __URL__)
  common_vars.__logger__.debug('Method: GET')

  # Send the GET request
  _request_ = SESSION.get(__URL__, headers=MyHeaders, params=MyParams)

  common_vars.__logger__.debug('Received status code: ' + str(_request_.status_code))
  common_vars.__logger__.debug('Received headers: ' + str(_request_.headers))
  common_vars.__logger__.debug('Received data: ' + _request_.content.decode())

  __ret__ = _request_.json()
  
  common_vars.__logger__.debug('Exit function')
  return __ret__
  

def digionline__updateCachedEPG(NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  _today_ = datetime.date(datetime.today())
  common_vars.__logger__.debug('_today_: ' + str(_today_))
  _epg_today_ = digionline__getEPG(_today_, NAME, SESSION)
  
  _today_plus_1_ = datetime.date(datetime.today()) + timedelta(days=1)
  common_vars.__logger__.debug('_today_plus_1_: ' + str(_today_plus_1_))
  _epg_today_plus_1_ = digionline__getEPG(_today_plus_1_, NAME, SESSION)
  
  _today_plus_2_ = datetime.date(datetime.today()) + timedelta(days=2)
  common_vars.__logger__.debug('_today_plus_2_: ' + str(_today_plus_2_))
  _epg_today_plus_2_ = digionline__getEPG(_today_plus_2_, NAME, SESSION)
  
  _epg_data_ = []
    
  for _ch_ in _epg_today_['data']['channels']:
    _ch_epg_data_ = {}
    _ch_epg_data_['id_channel'] = _ch_['id_channel']
    _ch_epg_data_['channel_name'] = _ch_['channel_name']
    _ch_epg_data_['channel_desc'] = _ch_['channel_desc']
    
    __ch_id__ = _ch_['id_channel']
    __epg__ = _ch_['epg']
  
    for _ch_1_ in _epg_today_plus_1_['data']['channels']:
      if _ch_['id_channel'] == _ch_1_['id_channel']:
        __epg__ = __epg__ + _ch_1_['epg']

    for _ch_2_ in _epg_today_plus_2_['data']['channels']:
      if _ch_['id_channel'] == _ch_2_['id_channel']:
        __epg__ = __epg__ + _ch_2_['epg']

    _ch_epg_data_['channel_epg'] = __epg__
    _epg_data_.append(_ch_epg_data_)
    

  if not os.path.exists(DATA_DIR + '/' + common_vars.__digionline_cache_dir__ ):
    os.makedirs(DATA_DIR + '/' + common_vars.__digionline_cache_dir__)

  _cache_data_file_ = os.path.join(DATA_DIR, common_vars.__digionline_cache_dir__, common_vars.__digionline_epgCachedDataFilename__)
  common_vars.__logger__.debug('Cached data file: ' + _cache_data_file_)

  _data_file_ = open(_cache_data_file_, 'w')
  json.dump(_epg_data_, _data_file_)
  _data_file_.close()

  common_vars.__logger__.debug('Exit function')


def digionline__getCachedEPG(NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  _cached_data_file_ = os.path.join(DATA_DIR, common_vars.__digionline_cache_dir__, common_vars.__digionline_epgCachedDataFilename__)
  common_vars.__logger__.debug('Cached data file: ' + _cached_data_file_)

  if os.path.exists(_cached_data_file_) and os.path.getsize(_cached_data_file_) != 0:
    # The data file with cached EPG data exists and is not empty.
    
    # Get the value (seconds since epoch) of the last modification time for the file containing cached data.
    _last_update_ = os.path.getmtime(_cached_data_file_)
    common_vars.__logger__.debug('Cached data file last update: ' + time.strftime("%Y%m%d_%H%M%S", time.gmtime(_last_update_)))
    
    if _last_update_ > time.time() - common_vars.__CachedDataRetentionInterval__:
      # Cached data is not yet expired.
      common_vars.__logger__.debug('Read cached EPG from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _epg_data_ = json.load(_data_file_)
      _data_file_.close()
      
      __ret__ = _epg_data_

    else:
      # Cached data is expired.
      
      # Call the function to update the cached data
      common_vars.__logger__.debug('Cached data requires update.')
      digionline__updateCachedEPG(NAME, SESSION, DATA_DIR)

      common_vars.__logger__.debug('Read cached EPG from data file: ' + _cached_data_file_)
      _data_file_ = open(_cached_data_file_, 'r')
      _epg_data_ = json.load(_data_file_)
      _data_file_.close()
      
      __ret__ = _epg_data_

  else:
    # The data file with cached EPG does not exist or it is empty.

    # Call the function to update the cached data
    common_vars.__logger__.debug('Cached data file does not exist.')
    digionline__updateCachedEPG(NAME, SESSION, DATA_DIR)

    common_vars.__logger__.debug('Read cached EPG from data file: ' + _cached_data_file_)
    _data_file_ = open(_cached_data_file_, 'r')
    _epg_data_ = json.load(_data_file_)
    _data_file_.close()
      
    __ret__ = _epg_data_

  common_vars.__logger__.debug('Exit function')

  return __ret__



def digionline__updateM3Ufile(M3U_FILE, START_NUMBER, NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')
  
  common_vars.__logger__.debug('M3U_FILE = ' + M3U_FILE)
  common_vars.__logger__.debug('START_NUMBER = ' + str(START_NUMBER))
  
  _CHNO_ = START_NUMBER

  _data_file_ = open(M3U_FILE, 'a', encoding='utf-8')

  # Get the list of categories
  _categories_ = digionline__getCachedCategories(NAME, SESSION, DATA_DIR)
  common_vars.__logger__.debug('Received categories = ' + str(_categories_))
  
  # Get the list of channels
  _channels_ = digionline_functions.digionline__getCachedChannels(NAME, SESSION, DATA_DIR)
  common_vars.__logger__.debug('Received channels = ' + str(_channels_))
    
  for category in _categories_:
    common_vars.__logger__.debug('Category name = ' + category['category_desc'])
      
    for cat_chan in category['channels_list']:
      for channel in _channels_:
        if cat_chan == channel['id_channel']:
          common_vars.__logger__.debug('Channel ID => ' + str(channel['id_channel']))
          common_vars.__logger__.debug('Channel name: ' + str(channel['channel_name']))
          common_vars.__logger__.debug('Channel title: ' + str(channel['channel_desc']))
          common_vars.__logger__.debug('Channel logo: ' + str(channel['media_channel']['channel_logo_url']))
        
          _line_ = "#EXTINF:0 tvg-id=\"digionline__" + str(channel['id_channel']) + "\" tvg-name=\"" + channel['channel_desc'] + "\" tvg-logo=\"" + channel['media_channel']['channel_logo_url'] + "\" tvg-chno=\"" + str(_CHNO_) + "\" group-title=\"" + category['category_desc'] + "\"," + channel['channel_desc']

          _url_ = common_functions.get_url(action='play', account='digionline.ro', channel_id=channel['id_channel'])
          _play_url_ = "plugin://" + common_vars.__AddonID__ + "/" + _url_

          _data_file_.write(_line_ + "\n")
          _data_file_.write(_play_url_ + "\n")
        
          _CHNO_ = _CHNO_ + 1

  _data_file_.close()
  
  common_vars.__logger__.debug('Exit function')

  return _CHNO_


def digionline__updateEPGfile(XML_FILE, NAME, SESSION, DATA_DIR):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  common_vars.__logger__.debug('XML_FILE = ' + XML_FILE)


  _epg_data_ = digionline__getCachedEPG(NAME, SESSION, DATA_DIR)
#  common_vars.__logger__.debug('_epg_data_ = ' + str(_epg_data_))

  _data_file_ = open(XML_FILE, 'a', encoding='utf-8')

  for channel in _epg_data_:
    common_vars.__logger__.debug('Channel ID => ' + str(channel['id_channel']))
    common_vars.__logger__.debug('Channel name: ' + str(channel['channel_name']))
    common_vars.__logger__.debug('Channel title: ' + str(channel['channel_desc']))

    _line_ = "  <channel id=\"digionline__" + str(channel['id_channel']) + "\">"
    _data_file_.write(_line_ + "\n")
    _line_ = "    <display-name>" + str(channel['channel_desc']) + "</display-name>"
    _data_file_.write(_line_ + "\n")
    _line_ = "  </channel>"
    _data_file_.write(_line_ + "\n")

    for _program_data_ in channel['channel_epg']:
      
      _start_date_time_object_ = datetime.utcfromtimestamp(int(_program_data_['start_ts']))
      _stop_date_time_object_ = datetime.utcfromtimestamp(int(_program_data_['end_ts']))
      _line_ = "  <programme start=\"" + str(_start_date_time_object_.strftime("%Y%m%d%H%M%S")) + "\" stop=\"" + str(_stop_date_time_object_.strftime("%Y%m%d%H%M%S")) + "\" channel=\"digionline__" + str(channel['id_channel']) + "\">"
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





















