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
import os
import logging
import http.cookiejar
import re
import time
import json
import resources.lib.common.vars as common_vars


def read_AddonSettings(__MyAddon__, NAME):
  common_vars.__logger__ = logging.getLogger(NAME)
  common_vars.__logger__.debug('Enter function')

  # Read the user preferences stored in the addon configuration

  # Accounts
  common_vars.__config_digionline_Enabled__ = __MyAddon__.getSetting('digionline_Enabled')
  common_vars.__logger__.debug('[ Addon settings ] digionline_Enabled = ' + str(common_vars.__config_digionline_Enabled__))

  common_vars.__config_digionline_Username__ = __MyAddon__.getSetting('digionline_Username')
  common_vars.__config_digionline_Password__ = __MyAddon__.getSetting('digionline_Password')

  common_vars.__config_digionline_DeviceManufacturer__ = __MyAddon__.getSetting('digionline_DeviceManufacturer')
  common_vars.__logger__.debug('[ Addon settings ] digionline_DeviceManufacturer = ' + str(common_vars.__config_digionline_DeviceManufacturer__))

  common_vars.__config_digionline_DeviceModel__ = __MyAddon__.getSetting('digionline_DeviceModel')
  common_vars.__logger__.debug('[ Addon settings ] digionline_DeviceModel = ' + str(common_vars.__config_digionline_DeviceModel__))

  common_vars.__config_digionline_AndroidVersion__ = __MyAddon__.getSetting('digionline_AndroidVersion')
  common_vars.__logger__.debug('[ Addon settings ] digionline_AndroidVersion = ' + str(common_vars.__config_digionline_AndroidVersion__))

  common_vars.__config_protvplus_Enabled__ = __MyAddon__.getSetting('protvplus_Enabled')
  common_vars.__logger__.debug('[ Addon settings ] protvplus_Enabled = ' + str(common_vars.__config_protvplus_Enabled__))
  common_vars.__config_protvplus_Username__ = __MyAddon__.getSetting('protvplus_Username')
  common_vars.__config_protvplus_Password__ = __MyAddon__.getSetting('protvplus_Password')

  # General settings
  common_vars.__config_ShowTitleInChannelList__ = __MyAddon__.getSetting('ShowTitleInChannelList')
  common_vars.__logger__.debug('[ Addon settings ] ShowTitleInChannelList = ' + str(common_vars.__config_ShowTitleInChannelList__))
  common_vars.__config_DebugEnabled__ = __MyAddon__.getSetting('DebugEnabled')
  common_vars.__logger__.debug('[ Addon settings ] DebugEnabled = ' + str(common_vars.__config_DebugEnabled__))

  ## Simple PVR integration
  common_vars.__config_PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime__ = __MyAddon__.getSetting('PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime')
  common_vars.__logger__.debug('[ Addon settings ] PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime = ' + str(common_vars.__config_PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime__))
  common_vars.__config_PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime__ = __MyAddon__.getSetting('PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime')
  common_vars.__logger__.debug('[ Addon settings ] PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime = ' + str(common_vars.__config_PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime__))


def get_url(**kwargs):
  ####
  #
  # Create a URL for calling the plugin recursively from the given set of keyword arguments.
  #
  ####

  common_vars.__logger__.debug('Enter function')
  common_vars.__logger__.debug('Called with parameters: ' + str(kwargs))

  _call_url_ = '{0}?{1}'.format(common_vars.__plugin_url__, urlencode(kwargs))

  common_vars.__logger__.debug('_call_url_: ' + str(_call_url_))
  common_vars.__logger__.debug('Exit function')

  return _call_url_


def has_accounts_enabled():
  common_vars.__logger__.debug('Enter function')
  
  _answer_ = 'false'
  
  if common_vars.__config_digionline_Enabled__ == 'true':
    common_vars.__logger__.debug('[ Addon settings ] digionline_Enabled = ' + str(common_vars.__config_digionline_Enabled__))
    _answer_ = 'true'
    
  if common_vars.__config_protvplus_Enabled__ == 'true':
    common_vars.__logger__.debug('[ Addon settings ] protvplus_Enabled = ' + str(common_vars.__config_protvplus_Enabled__))
    _answer_ = 'true'

  return _answer_
  
