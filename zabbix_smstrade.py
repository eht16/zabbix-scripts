#!/usr/bin/env python
# coding: utf-8
#
#  zabbix_smstrade.py
#
#  Copyright 2011 Enrico Tröger <enrico(dot)troeger(at)uvena(dot)de>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
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
This script sends Zabbix alerts as SMS via the HTTP API of smstrade.de.

It is very similar to http://www.zabbix.com/wiki/howto/config/alerts/smsapi
but written in Python. Similarly, the subject is ignored, instead the message
is used as SMS text. Additionally, this script will cut the passed message text
after 160 characters to ensure only one (non-concatenated) SMS is sent.

To get it working, simply edit the parameters below.
Alternatively, you can specify the full path to a config file as the first and only
command line argument to overwrite the default values below. This way you do not
need to edit this script. An example config file can be found in the GIT repository
where you got this script from.
"""

from ConfigParser import ConfigParser
from os.path import basename
from syslog import closelog, openlog, syslog, LOG_INFO, LOG_ERR, LOG_USER
from urllib import urlencode
from urllib2 import urlopen
import sys


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
    def __init__(self):
        self.smstrade_api_url = SMSTRADE_API_URL
        self.smstrade_key = SMSTRADE_KEY
        self.smstrade_route = SMSTRADE_ROUTE
        self.smstrade_from = SMSTRADE_FROM
        self.smstrade_debug = SMSTRADE_DEBUG

        self._parser = None
        self._vars = None

    #----------------------------------------------------------------------
    def read(self):
        self._parser = ConfigParser()
        config_filename = u'/tmp/zabbix_script.conf'
        self._parser.read(config_filename)

        self._get_string('zabbix_smstrade', 'smstrade_api_url')
        self._get_string('zabbix_smstrade', 'smstrade_key')
        self._get_string('zabbix_smstrade', 'smstrade_route')
        self._get_string('zabbix_smstrade', 'smstrade_from')
        self._get_bool('zabbix_smstrade', 'smstrade_debug')

    #----------------------------------------------------------------------
    def _get_string(self, section, key):
        if self._parser.has_option(section, key):
            value = self._parser.get(section, key, vars=self._vars)
            setattr(self, key, value)

    #----------------------------------------------------------------------
    def _get_bool(self, section, key):
        if self._parser.has_option(section, key):
            value = self._parser.getboolean(section, key)
            setattr(self, key, value)


#----------------------------------------------------------------------
def send_sms(config):
    def _get_response_line(lines, index):
        try:
            return lines[index].strip()
        except IndexError:
            return -1
        
    url = config.smstrade_api_url
    recipient = sys.argv[1]
    message = sys.argv[3]
    key = config.smstrade_key
    route = config.smstrade_route
    
    if len(message) > 160:
        message = message[:160]
        
    data = dict(
        key=key,
        to=recipient,
        message=message,
        route=route,
        cost='1',
        count='1')

    if config.smstrade_from:
        data['route'] = 'gold'
        data['from'] = config.smstrade_from
    # debug mode
    if config.smstrade_debug:
        data['debug'] = 1

    response = urlopen(url, urlencode(data))
    result = response.read()
    lines = result.splitlines()
    response_code = int(_get_response_line(lines, 0))
    cost = float(_get_response_line(lines, 2))
    count = int(_get_response_line(lines, 3))
    syslog_priority = LOG_INFO if response_code == 100 else LOG_ERR
    syslog(syslog_priority, u'SMS sent to %s with response code %s (cost: %s, count: %s)' % \
            (recipient, response_code, cost, count))
        

#----------------------------------------------------------------------
def validate_arguments():
    if len(sys.argv) < 4:
        print >> sys.stderr, u'Usage: %s recipientmobilenumber "subject" "message"' % sys.argv[0]
        exit(1)

    # here we do not support +XXyyyy style numbers but that's ok for me :)
    if not sys.argv[1].isdigit():
        print >> sys.stderr, u'Invalid recipient phone number'
        
    if not sys.argv[3]:
        print >> sys.stderr, u'Invalid / empty message'
        

#----------------------------------------------------------------------
def main():
    openlog(basename(sys.argv[0]), 0, LOG_USER)
    try:
        validate_arguments()

        config = Configuration()
        config.read()

        send_sms(config)
    except Exception, e:
        syslog(LOG_ERR, u'An error occurred: %s' % unicode(e))
    finally:
        closelog()
    

if __name__ == '__main__':
    main()
