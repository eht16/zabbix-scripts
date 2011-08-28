#!/usr/bin/env python
# coding: utf-8
#
#  zabbix_smstrade.py
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
This script sends Zabbix alerts as SMS via the HTTP API of smstrade.de.

For details about this script and its configuration, see README.rst.
"""


from os.path import basename
from syslog import closelog, openlog, syslog, LOG_INFO, LOG_ERR, LOG_USER
from urllib import urlencode
from urllib2 import urlopen
from zabbix_common import Configuration
import sys



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
    syslog(syslog_priority, 
        u'SMS sent to %s with response code %s (cost: %s, count: %s, debug: %s)' % \
        (recipient, response_code, cost, count, config.smstrade_debug))
        

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
