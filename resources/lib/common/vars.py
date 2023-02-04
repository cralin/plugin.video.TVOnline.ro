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
__config_digionline_PhoneDeviceManufacturer__ = ''
__config_digionline_PhoneDeviceModel__ = ''
__config_digionline_PhoneAndroidVersion__ = ''

__config_digionline_TVDeviceModel__ = ''
__config_digionline_TVAndroidVersion__ = ''
__config_digionline_TVPlatform__ = ''

__config_voyo_Enabled__ = ''
__config_voyo_Username__ = ''
__config_voyo_Password__ = ''

__config_primaplay_Enabled__ = ''
__config_primaplay_Username__ = ''
__config_primaplay_Password__ = ''

__config_tvrplus_Enabled__ = ''

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
__voyo_userAgent__ = 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
__primaplay_userAgent__ = 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
__tvrplus_userAgent__ = 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'

# The IDs used by add-on
__AddonID__ = 'plugin.video.TVOnline.ro'
__ServiceID__ = 'service.plugin.video.TVOnline.ro'

# File names for the files where the add-on and the service will write the log entries
__AddonLogFilename__ = __AddonID__ + '.log'
__ServiceLogFilename__ = __ServiceID__ + '.log'

# The cookiejars used by add-on
__digionline_CookiesFilename__ = 'digionline.ro_cookies.txt'
__digionline_CookieJar__ = ''

__voyo_CookiesFilename__ = 'voyo.ro_cookies.txt'
__voyo_CookieJar__ = ''

__primaplay_CookiesFilename__ = 'primaplay.ro_cookies.txt'
__primaplay_CookieJar__ = ''

__tvrplus_CookiesFilename__ = 'tvrplus.ro_cookies.txt'
__tvrplus_CookieJar__ = ''

# Legacy file name for storing the state data
__digionline_LegacyStateFilename__ = 'digionline.ro_state.txt'

# File name for storing the state data when behaving as Android phone
__digionline_PhoneStateFilename__ = 'digionline.ro_PhoneState.txt'

# File name for storing the state data when behaving as Android TV
__digionline_TVStateFilename__ = 'digionline.ro_TVState.txt'


# The sessions used by add-on
__digionline_Session__ = ''
__voyo_Session__ = ''
__primaplay_Session__ = ''
__tvrplus_Session__ = ''

__digionline_ServiceSession__ = ''
__voyo_ServiceSession__ = ''
__primaplay_ServiceSession__ = ''
__tvrplus_ServiceSession__ = ''

# The plugin url in plugin:// notation.
__plugin_url__ = ''

# The plugin handle
__handle__ = ''

__logger__ = ''



#### Constants
__behave_map__ = {}
__behave_map__['0'] = "Phone"
__behave_map__['1'] = "TV"

__minute__ = (1 * 60)
__day__ = (24 * 60 * 60)

# Max interval between authentications
__digionline_AuthInterval__ = (1 * __day__)

# Directory holding the cached data. 
__digionline_cache_dir__ = 'cached_data/digionline.ro'
__voyo_cache_dir__ = 'cached_data/voyo.ro'
__primaplay_cache_dir__ = 'cached_data/primaplay.ro'
__tvrplus_cache_dir__ = 'cached_data/tvrplus.ro'

# File names for the raw data
__PVRIPTVSimpleClientIntegration_digionline_raw_m3u_FileName__ = __AddonID__ + 'digionline.m3u.raw'
__PVRIPTVSimpleClientIntegration__digionline_raw_EPG_FileName__ = __AddonID__ + 'digionline.xml.raw'
 
__PVRIPTVSimpleClientIntegration_voyo_raw_m3u_FileName__ = __AddonID__ + 'voyo.m3u.raw'
__PVRIPTVSimpleClientIntegration__voyo_raw_EPG_FileName__ = __AddonID__ + 'voyo.xml.raw'

__PVRIPTVSimpleClientIntegration_primaplay_raw_m3u_FileName__ = __AddonID__ + 'primaplay.m3u.raw'
__PVRIPTVSimpleClientIntegration__primaplay_raw_EPG_FileName__ = __AddonID__ + 'primaplay.xml.raw'

__PVRIPTVSimpleClientIntegration_tvrplus_raw_m3u_FileName__ = __AddonID__ + 'tvrplus.m3u.raw'
__PVRIPTVSimpleClientIntegration__tvrplus_raw_EPG_FileName__ = __AddonID__ + 'tvrplus.xml.raw'

# File containing the local copy of the list of categories and channels read from source
__digionline_PhoneCategoriesChannelsCachedDataFilename__ = 'Phone_CategoriesChannels.json'
__digionline_TVCategoriesChannelsCachedDataFilename__ = 'TV_CategoriesChannels.json'

# File containing the local copy of the epg read from source
__digionline_PhoneEPGCachedDataFilename__ = 'Phone_EPG.json'
__digionline_TVEPGCachedDataFilename__ = 'TV_EPG.json'

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
__PVRIPTVSimpleClientIntegration_versions_FileName__ = __AddonID__ + '.json'

# Time of day for refreshing the contents in the data files.
__PVRIPTVSimpleClientIntegration_m3u_FileRefreshTime__ = ''
__PVRIPTVSimpleClientIntegration_EPG_FileRefreshTime__ = ''

# Previous/Old time of day for refreshing the contents in the data files.
__PVRIPTVSimpleClientIntegration_m3u_FileOldRefreshTime__ = ''
__PVRIPTVSimpleClientIntegration_EPG_FileOldRefreshTime__ = ''

# Time since the last update of data files. If this time has passed, the data files will be updated.
__PVRIPTVSimpleClientIntegration_m3u_FileMaxAge__ = (1 * __day__) + (1 * __minute__)
__PVRIPTVSimpleClientIntegration_EPG_FileMaxAge__ = (1 * __day__) + (1 * __minute__)


