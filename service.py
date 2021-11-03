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

import os
import xbmcaddon
import xbmc
import xbmcvfs
from urllib.parse import urlencode
import requests
import json
import logging
import logging.handlers
#from datetime import datetime
#from datetime import timedelta
import time
import resources.lib.common.vars as common_vars
import resources.lib.common.functions as common_functions
import resources.lib.digionline.functions as digionline_functions
import resources.lib.protvplus.functions as protvplus_functions
import resources.lib.schedule as schedule
import re

__SystemBuildVersion__ = xbmc.getInfoLabel('System.BuildVersion')
__SystemBuildDate__ = xbmc.getInfoLabel('System.BuildDate')

# Kodi uses the following sys.argv arguments:
# [0] - The base URL for this add-on, e.g. 'plugin://plugin.video.demo1/'.
# [1] - The process handle for this add-on, as a numeric string.
# [2] - The query string passed to this add-on, e.g. '?foo=bar&baz=quux'.

# Get the plugin url in plugin:// notation.
common_vars.__plugin_url__ = sys.argv[0]

# Get the plugin handle as an integer number.
#_handle = int(sys.argv[1])

MyServiceAddon = xbmcaddon.Addon(id=common_vars.__AddonID__)

# The version of the runing Addon
__AddonVersion__ = MyServiceAddon.getAddonInfo('version')

# Initialize the Addon data directory
MyServiceAddon_DataDir = xbmcvfs.translatePath(MyServiceAddon.getAddonInfo('profile'))
if not os.path.exists(MyServiceAddon_DataDir):
    os.makedirs(MyServiceAddon_DataDir)

# Read the user preferences stored in the addon configuration
common_functions.read_AddonSettings(MyServiceAddon, common_vars.__ServiceID__)

# Log file name
service_logfile_name = os.path.join(MyServiceAddon_DataDir, common_vars.__ServiceLogFilename__)

# Configure logging
if common_vars.__config_DebugEnabled__ == 'true':
  logging.basicConfig(level=logging.DEBUG)
else:
  logging.basicConfig(level=logging.INFO)

common_vars.__logger__ = logging.getLogger(common_vars.__ServiceID__)
common_vars.__logger__.propagate = False

# Create a rotating file handler
# TODO: Extend the settings.xml to allow the user to choose the values for maxBytes and backupCount
# TODO: Set the values for maxBytes and backupCount to values defined in the addon settings
handler = logging.handlers.RotatingFileHandler(service_logfile_name, mode='a', maxBytes=104857600, backupCount=2, encoding='utf-8', delay=False)
if common_vars.__config_DebugEnabled__ == 'true':
  handler.setLevel(logging.DEBUG)
else:
  handler.setLevel(logging.INFO)

# Create a logging format to be used
formatter = logging.Formatter('%(asctime)s %(funcName)s %(levelname)s: %(message)s', datefmt='%Y%m%d_%H%M%S')
handler.setFormatter(formatter)

# add the file handler to the common_vars.__logger__
common_vars.__logger__.addHandler(handler)


# Initialize the __AddonCookieJar__ variable
digionline_functions.init_AddonCookieJar(common_vars.__ServiceID__, MyServiceAddon_DataDir)
protvplus_functions.init_AddonCookieJar(common_vars.__ServiceID__, MyServiceAddon_DataDir)

# Start a new requests session and initialize the cookiejar
common_vars.__digionline_ServiceSession__ = requests.Session()
common_vars.__protvplus_ServiceSession__ = requests.Session()

# Put all session cookeis in the cookiejar
common_vars.__digionline_ServiceSession__.cookies = common_vars.__digionline_CookieJar__
common_vars.__protvplus_ServiceSession__.cookies = common_vars.__digionline_CookieJar__




def schedule_jobs():
  common_vars.__logger__.debug('Enter function')
  
  # Read the user preferences stored in the addon configuration
  common_functions.read_AddonSettings(MyServiceAddon, common_vars.__ServiceID__)
  
  if common_vars.__PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime__ != common_vars.__PVRIPTVSimpleClientIntegration_m3u_FileOldRefreshTime__ or common_vars.__PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime__ != common_vars.__PVRIPTVSimpleClientIntegration_EPG_FileOldRefreshTime__:
    common_vars.__logger__.debug('__PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime__ = ' + common_vars.__PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime__)
    common_vars.__logger__.debug('__PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime__ = ' + common_vars.__PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime__)

    schedule.clear('m3u')
    schedule.every().day.at(common_vars.__PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime__).do(PVRIPTVSimpleClientIntegration_update_m3u_file).tag('m3u')
    
    schedule.clear('EPG')
    schedule.every().day.at(common_vars.__PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime__).do(PVRIPTVSimpleClientIntegration_update_EPG_file).tag('EPG')

    # Record the new values
    common_vars.__PVRIPTVSimpleClientIntegration_m3u_FileOldRefreshTime__ = common_vars.__PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime__
    common_vars.__PVRIPTVSimpleClientIntegration_EPG_FileOldRefreshTime__ = common_vars.__PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime__

  else:
    common_vars.__logger__.debug('No re-scheduling required !')
    
  # (re)Initialize the files for PVR IPTV Simple Client
  PVRIPTVSimpleClientIntegration_init_m3u_file()
  PVRIPTVSimpleClientIntegration_init_EPG_file()

  common_vars.__logger__.debug('Exit function')


def PVRIPTVSimpleClientIntegration_check_data_file(DATAFILE):
  ####
  #
  # Check the status of data file.
  #
  # Parameters:
  #      DATAFILE: File (full path) to be checked
  #
  # Return:
  #      0 - update of DATAFILE is not required
  #      1 - update of DATAFILE is required
  #
  ####
  common_vars.__logger__.debug('Enter function')
  _return_code_ = 0
  common_vars.__logger__.debug('Data file ==> ' + DATAFILE)

  if os.path.exists(DATAFILE):
    # The DATAFILE exists.
    common_vars.__logger__.debug('\'' + DATAFILE + '\' exists.')

    if os.path.getsize(DATAFILE) != 0:
      # The DATAFILE is not empty.
      common_vars.__logger__.debug('\'' + DATAFILE + '\' is not empty.')
    else:
      # The DATAFILE is empty.
      common_vars.__logger__.debug('\'' + DATAFILE + '\' is empty.')
      _return_code_ = 1

    # Get the value (seconds since epoch) of the last modification time.
    _last_update_ = os.path.getmtime(DATAFILE)

    if _last_update_ > time.time() - (1 * common_vars.__day__):
      # File was updated less than 24 hours ago, nothing to do
      common_vars.__logger__.debug('\'' + DATAFILE + '\' last update: ' + time.strftime("%Y%m%d_%H%M%S", time.localtime(_last_update_)))
    else:
      # File was updated 24 hours (or more) ago
      common_vars.__logger__.debug('\'' + DATAFILE + '\' last update: ' + time.strftime("%Y%m%d_%H%M%S", time.localtime(_last_update_)))
      _return_code_ = 1

  else:
    # The DATAFILE does not exist.
    common_vars.__logger__.debug('\'' + DATAFILE + '\' does not exist.')
    _return_code_ = 1

  common_vars.__logger__.debug('Exit function')
  return _return_code_


def PVRIPTVSimpleClientIntegration_init_m3u_file():
  common_vars.__logger__.debug('Enter function')
  
  # Read the user preferences stored in the addon configuration
  common_functions.read_AddonSettings(MyServiceAddon, common_vars.__ServiceID__)
  
  if not os.path.exists(MyServiceAddon_DataDir + '/' + common_vars.__PVRIPTVSimpleClientIntegration_DataDir__ ):
    os.makedirs(MyServiceAddon_DataDir + '/' + common_vars.__PVRIPTVSimpleClientIntegration_DataDir__)

  _m3u_file_ = os.path.join(MyServiceAddon_DataDir, common_vars.__PVRIPTVSimpleClientIntegration_DataDir__, common_vars.__PVRIPTVSimpleClientIntegration_m3u_FileName__)
  common_vars.__logger__.debug('m3u file: ' + _m3u_file_)

  _update_required_ = PVRIPTVSimpleClientIntegration_check_data_file(_m3u_file_)
  common_vars.__logger__.debug('_update_required_ ==> ' + str(_update_required_))
  
  if _update_required_ == 1:
    PVRIPTVSimpleClientIntegration_update_m3u_file()

  common_vars.__logger__.debug('Exit function')


def PVRIPTVSimpleClientIntegration_update_m3u_file():
  common_vars.__logger__.debug('Enter function')

  # Read the user preferences stored in the addon configuration
  common_functions.read_AddonSettings(MyServiceAddon, common_vars.__ServiceID__)

  _current_channel_number_ = 1
  
  if not os.path.exists(MyServiceAddon_DataDir + '/' + common_vars.__PVRIPTVSimpleClientIntegration_DataDir__ ):
    os.makedirs(MyServiceAddon_DataDir + '/' + common_vars.__PVRIPTVSimpleClientIntegration_DataDir__)
    
  _m3u_file_ = os.path.join(MyServiceAddon_DataDir, common_vars.__PVRIPTVSimpleClientIntegration_DataDir__, common_vars.__PVRIPTVSimpleClientIntegration_m3u_FileName__)
  common_vars.__logger__.debug('_m3u_file_ = ' + _m3u_file_)
  
  _tmp_m3u_file_ = os.path.join(MyServiceAddon_DataDir, common_vars.__PVRIPTVSimpleClientIntegration_DataDir__, common_vars.__PVRIPTVSimpleClientIntegration_m3u_FileName__ + '.tmp')
  common_vars.__logger__.debug('_tmp_m3u_file_ = ' + _tmp_m3u_file_)
  
  if common_functions.has_accounts_enabled() == 'true':
    common_vars.__logger__.debug('Addon has at least one account enabled')
    
    _data_file_ = open(_tmp_m3u_file_, 'w', encoding='utf-8')
    _data_file_.write("#EXTM3U tvg-shift=0" + "\n")
    _data_file_.close()
  
    # digionline.ro
    if common_vars.__config_digionline_Enabled__ == 'true':
      _current_channel_number_ = digionline_functions.digionline__updateM3Ufile(_tmp_m3u_file_, _current_channel_number_, common_vars.__ServiceID__, common_vars.__digionline_ServiceSession__, MyServiceAddon_DataDir)

    common_vars.__logger__.debug('_current_channel_number_ = ' + str(_current_channel_number_))

    # protvplus.ro
    if common_vars.__config_protvplus_Enabled__ == 'true':
      _current_channel_number_ = protvplus_functions.PVRIPTVSimpleClientIntegration_update_m3u_file(_tmp_m3u_file_, _current_channel_number_, common_vars.__ServiceID__, common_vars.__protvplus_CookieJar__, common_vars.__protvplus_ServiceSession__)

    common_vars.__logger__.debug('_current_channel_number_ = ' + str(_current_channel_number_))
 
    os.replace(_tmp_m3u_file_, _m3u_file_)

  else:
    common_vars.__logger__.debug('Addon has no accounts enabled')

  common_vars.__logger__.debug('Exit function')



def PVRIPTVSimpleClientIntegration_init_EPG_file():
  common_vars.__logger__.debug('Enter function')

  # Read the user preferences stored in the addon configuration
  common_functions.read_AddonSettings(MyServiceAddon, common_vars.__ServiceID__)
  
  if not os.path.exists(MyServiceAddon_DataDir + '/' + common_vars.__PVRIPTVSimpleClientIntegration_DataDir__ ):
    os.makedirs(MyServiceAddon_DataDir + '/' + common_vars.__PVRIPTVSimpleClientIntegration_DataDir__)

  _epg_file_ = os.path.join(MyServiceAddon_DataDir, common_vars.__PVRIPTVSimpleClientIntegration_DataDir__, common_vars.__PVRIPTVSimpleClientIntegration_EPG_FileName__)
  common_vars.__logger__.debug('epg file: ' + _epg_file_)

  _update_required_ = PVRIPTVSimpleClientIntegration_check_data_file(_epg_file_)
  common_vars.__logger__.debug('_update_required_ ==> ' + str(_update_required_))
  
  if _update_required_ == 1:
    PVRIPTVSimpleClientIntegration_update_EPG_file()

  common_vars.__logger__.debug('Exit function')



def PVRIPTVSimpleClientIntegration_update_EPG_file():
  common_vars.__logger__.debug('Enter function')

  # Read the user preferences stored in the addon configuration
  common_functions.read_AddonSettings(MyServiceAddon, common_vars.__ServiceID__)

  if not os.path.exists(MyServiceAddon_DataDir + '/' + common_vars.__PVRIPTVSimpleClientIntegration_DataDir__ ):
    os.makedirs(MyServiceAddon_DataDir + '/' + common_vars.__PVRIPTVSimpleClientIntegration_DataDir__)
      
  _epg_file_ = os.path.join(MyServiceAddon_DataDir, common_vars.__PVRIPTVSimpleClientIntegration_DataDir__, common_vars.__PVRIPTVSimpleClientIntegration_EPG_FileName__)
  common_vars.__logger__.debug('_epg_file_ = ' + _epg_file_)

  _tmp_epg_file_ = os.path.join(MyServiceAddon_DataDir, common_vars.__PVRIPTVSimpleClientIntegration_DataDir__, common_vars.__PVRIPTVSimpleClientIntegration_EPG_FileName__ + '.tmp')

  common_vars.__logger__.debug('_tmp_epg_file_ = ' + _tmp_epg_file_)

  if common_functions.has_accounts_enabled() == 'true':
    common_vars.__logger__.debug('Addon has at least one account enabled')
      
    _data_file_ = open(_tmp_epg_file_, 'w', encoding='utf-8')
    _data_file_.write("<?xml version=\"1.0\" encoding=\"utf-8\" ?>" + "\n")
    _data_file_.write("<tv>" + "\n")
    _data_file_.close()
  
    if common_vars.__config_digionline_Enabled__ == 'true':
      digionline_functions.digionline__updateEPGfile(_tmp_epg_file_, common_vars.__ServiceID__, common_vars.__digionline_ServiceSession__, MyServiceAddon_DataDir)

    if common_vars.__config_protvplus_Enabled__ == 'true':
      protvplus_functions.PVRIPTVSimpleClientIntegration_update_EPG_file(_tmp_epg_file_, common_vars.__ServiceID__, common_vars.__protvplus_CookieJar__, common_vars.__protvplus_ServiceSession__)

    _data_file_ = open(_tmp_epg_file_, 'a', encoding='utf-8')
    _data_file_.write("</tv>" + "\n")
    _data_file_.close()
    os.replace(_tmp_epg_file_, _epg_file_)

  else:
    common_vars.__logger__.debug('Addon has no accounts enabled')
    
  common_vars.__logger__.debug('Exit function')


if __name__ == '__main__':
  common_vars.__logger__.debug('Enter __main__ ')
  common_vars.__logger__.debug('=== SYSINFO ===  Addon version: ' + str(__AddonVersion__))
  common_vars.__logger__.debug('=== SYSINFO ===  System.BuildVersion: ' + str(__SystemBuildVersion__))
  common_vars.__logger__.debug('=== SYSINFO ===  System.BuildDate: ' + str(__SystemBuildDate__))

  # Read the user preferences stored in the addon configuration
  common_functions.read_AddonSettings(MyServiceAddon, common_vars.__ServiceID__)

  common_vars.__logger__.debug('Waiting 15 seconds for network to stabilize')
  time.sleep(15)
  common_vars.__logger__.debug('Done waiting 15 seconds for network to stabilize')

  schedule_jobs()
  schedule.every().minute.at(":05").do(schedule_jobs)
  
  common_vars.__logger__.debug('Finished scheduling jobs')

  monitor = xbmc.Monitor()  
  while not monitor.abortRequested():
    # Sleep/wait for abort for 300 seconds
    if monitor.waitForAbort(1):
      # Abort was requested while waiting. We should exit
      common_vars.__logger__.debug('Abort was requested while waiting.')
      break
    schedule.run_pending()
  common_vars.__logger__.debug('Exit __main__ ')

