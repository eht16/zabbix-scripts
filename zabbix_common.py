# coding: utf-8
#
#  zabbix_common.py
#
#  Copyright 2011 Enrico Tröger <enrico(dot)troeger(at)uvena(dot)de>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""
Common logic to the various Zabbix Python scripts.

For details about this script and its configuration, see README.rst.
"""


from ConfigParser import ConfigParser
from os.path import expanduser
from socket import getfqdn



# either edit these values or provide a config file which will overwrite the values below
ZABBIX_FRONTEND_URL = u'https://example.com/zabbix'
ZABBIX_USERNAME = 'zabbix_user'
ZABBIX_PASSWORD = 'zabbix_password'

GRAPH_WIDTH = 600
GRAPH_HEIGHT = 200
GRAPH_PERIOD = 60 * 60 * 24 * 7 # 7 days
# you can get the graph ids from the URL when watching a graph in the frontend
GRAPH_IDS = [1, 2, 3, 4]

SMTP_FROM = u'zabbix@%s' % getfqdn()
SMTP_TO = [u'recipient@example.com']
SMTP_SUBJECT = u'Zabbix Report'
SMTP_SERVER = u'localhost'

SMSTRADE_API_URL = 'https://gateway.smstrade.de'
SMSTRADE_KEY = 'abcd1234'
SMSTRADE_ROUTE = 'basic'
# if from is set to something non-empty, the route is changed to 'gold'
SMSTRADE_FROM = ''
# this enables the debug mode on the smstrade API, i.e. SMS are not delivered and not accounted
SMSTRADE_DEBUG = True



########################################################################
class Configuration(object):

    #----------------------------------------------------------------------
    def __init__(self, additional_config_filepath=None):
        self.graph_height = GRAPH_HEIGHT
        self.graph_ids = GRAPH_IDS
        self.graph_period = GRAPH_PERIOD
        self.graph_width = GRAPH_WIDTH
        self.smstrade_api_url = SMSTRADE_API_URL
        self.smstrade_debug = SMSTRADE_DEBUG
        self.smstrade_from = SMSTRADE_FROM
        self.smstrade_key = SMSTRADE_KEY
        self.smstrade_route = SMSTRADE_ROUTE
        self.smtp_from = SMTP_FROM
        self.smtp_server = SMTP_SERVER
        self.smtp_subject = SMTP_SUBJECT
        self.smtp_to = SMTP_TO
        self.zabbix_frontend_url = ZABBIX_FRONTEND_URL
        self.zabbix_password = ZABBIX_PASSWORD
        self.zabbix_username = ZABBIX_USERNAME

        self._parser = None
        self._vars = dict(fqdn=getfqdn())
        self._additional_config_filepath = additional_config_filepath

    #----------------------------------------------------------------------
    def read(self):
        config_file_paths = self._get_config_file_paths()
        self._parser = ConfigParser()
        self._parser.read(config_file_paths)

        self._get_string('zabbix', 'zabbix_frontend_url')
        self._get_string('zabbix', 'zabbix_password')
        self._get_string('zabbix', 'zabbix_username')
        self._get_bool('zabbix_smstrade', 'smstrade_debug')
        self._get_int('zabbix_graph', 'graph_height')
        self._get_int('zabbix_graph', 'graph_period')
        self._get_int('zabbix_graph', 'graph_width')
        self._get_list('zabbix_graph', 'graph_ids')
        self._get_list('zabbix_graph', 'smtp_to')
        self._get_string('zabbix_graph', 'smtp_from')
        self._get_string('zabbix_graph', 'smtp_server')
        self._get_string('zabbix_graph', 'smtp_subject')
        self._get_string('zabbix_smstrade', 'smstrade_api_url')
        self._get_string('zabbix_smstrade', 'smstrade_from')
        self._get_string('zabbix_smstrade', 'smstrade_key')
        self._get_string('zabbix_smstrade', 'smstrade_route')

    #----------------------------------------------------------------------
    def _get_config_file_paths(self):
        config_file_paths = list()
        # various config file paths
        config_file_paths.append(u'/etc/zabbix_script.conf')
        config_file_paths.append(u'/etc/zabbix/zabbix_script.conf')
        config_file_paths.append(expanduser(u'~/.zabbix_script.conf'))
        
        if self._additional_config_filepath:
            config_file_paths.append(self._additional_config_filepath)
            
        return config_file_paths
        
    #----------------------------------------------------------------------
    def _get_string(self, section, key):
        if self._parser.has_option(section, key):
            value = self._parser.get(section, key, vars=self._vars)
            setattr(self, key, value)

    #----------------------------------------------------------------------
    def _get_int(self, section, key):
        if self._parser.has_option(section, key):
            value = self._parser.getint(section, key)
            setattr(self, key, value)

    #----------------------------------------------------------------------
    def _get_list(self, section, key):
        if self._parser.has_option(section, key):
            value = self._parser.get(section, key)
            value = eval(value)
            setattr(self, key, value)

    #----------------------------------------------------------------------
    def _get_bool(self, section, key):
        if self._parser.has_option(section, key):
            value = self._parser.getboolean(section, key)
            setattr(self, key, value)
