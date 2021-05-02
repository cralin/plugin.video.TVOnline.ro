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


######## Variables for the user preferences stored in the addon configuration ########

# Accounts
__config_digionline_Enabled__ = ''
__config_digionline_Username__ = ''
__config_digionline_Password__ = ''
__config_digionline_DeviceManufacturer__ = ''
__config_digionline_DeviceModel__ = ''
__config_digionline_AndroidVersion__ = ''

__config_protvplus_Enabled__ = ''
__config_protvplus_Username__ = ''
__config_protvplus_Password__ = ''

# General settings
__config_ShowTitleInChannelList__ = ''
__config_DebugEnabled__ = ''

# Cached data
__config_categoriesCachedDataRetentionInterval__ = ''
__config_channelsCachedDataRetentionInterval__ = ''
__config_EPGDataCachedDataRetentionInterval__ = ''

## Simple PVR integration
__config_PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime__ = ''
__config_PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime__ = ''


########



# UserAgent exposed by this add-on
__digionline_API_userAgent__ = 'okhttp/4.8.1'
__digionline_userAgent__ = 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
__protvplus_userAgent__ = 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'


# The IDs used by add-on
__AddonID__ = 'plugin.video.TVOnline.ro'
__ServiceID__ = 'service.plugin.video.TVOnline.ro'

# File names for the files where the add-on and the service will write the log entries
__AddonLogFilename__ = __AddonID__ + '.log'
__ServiceLogFilename__ = __ServiceID__ + '.log'

# The cookiejars used by add-on
__digionline_CookiesFilename__ = 'digionline.ro_cookies.txt'
__digionline_CookieJar__ = ''

__protvplus_CookiesFilename__ = 'protvplus.ro_cookies.txt'
__protvplus_CookieJar__ = ''

# File name for storing the state data
__digionline_StateFilename__ = 'digionline.ro_state.txt'


# The sessions used by add-on
__digionline_Session__ = ''
__protvplus_Session__ = ''

__digionline_ServiceSession__ = ''
__protvplus_ServiceSession__ = ''

# The plugin url in plugin:// notation.
__plugin_url__ = ''

# The plugin handle
__handle__ = ''

__logger__ = ''



# Constants
__minute__ = (1 * 60)
__day__ = (24 * 60 * 60)

# Max interval between authentications
__digionline_AuthInterval__ = (1 * __day__)

# Directory holding the cached data. 
__digionline_cache_dir__ = 'cached_data/digionline.ro'
__protvplus_cache_dir__ = 'cached_data/protvplus.ro'


# File names for the raw data
__PVRIPTVSimpleClientIntegration_digionline_raw_m3u_FileName__ = __AddonID__ + 'digionline.m3u.raw'
__PVRIPTVSimpleClientIntegration__digionline_raw_EPG_FileName__ = __AddonID__ + 'digionline.xml.raw'
 
__PVRIPTVSimpleClientIntegration_protvplus_raw_m3u_FileName__ = __AddonID__ + 'protvplus.m3u.raw'
__PVRIPTVSimpleClientIntegration__protvplus_raw_EPG_FileName__ = __AddonID__ + 'protvplus.xml.raw'


# File containing the local copy of the list of categories and channels read from source
__digionline_categorieschannelsCachedDataFilename__ = 'categorieschannels.json'

# File containing the local copy of the epg read from source
__digionline_epgCachedDataFilename__ = 'epg.json'


# Some sane defaults before being overwritten by the user settings
# How much time has to pass before reading again from source the list of categories.
__CachedDataRetentionInterval__ = (1 * __day__)


### Service variables

## PVR IPTV Simple Client integration 
# Directory where data files are stored
__PVRIPTVSimpleClientIntegration_DataDir__ = 'PVRIPTVSimpleClientIntegration'

# File names for the data files
__PVRIPTVSimpleClientIntegration_m3u_FileName__ = __AddonID__ + '.m3u'
__PVRIPTVSimpleClientIntegration_EPG_FileName__ = __AddonID__ + '.xml' 

# Time of day for refreshing the contents in the data files.
__PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime__ = ''
__PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime__ = ''

# Previous/Old time of day for refreshing the contents in the data files.
__PVRIPTVSimpleClientIntegration_m3u_FileOldRefreshTime__ = ''
__PVRIPTVSimpleClientIntegration_EPG_FileOldRefreshTime__ = ''

# Time since the last update of data files. If this time has passed, the data files will be updated.
__PVRIPTVSimpleClientIntegration_m3u_FileMaxAge__ = (1 * __day__) + (1 * __minute__)
__PVRIPTVSimpleClientIntegration_EPG_FileMaxAge__ = (1 * __day__) + (1 * __minute__)


