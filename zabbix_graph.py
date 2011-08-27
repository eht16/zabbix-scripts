#!/usr/bin/env python
# coding: utf-8
#
#  zabbix_graph.py
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
This script reads one or more graphs from the Zabbix frontend and
sends them as attachments via mail.

The script is inspired by http://www.zabbix.com/forum/showthread.php?t=15316
but simpler as it just takes a list of graphids to work on instead
of using a special media report in Zabbix to determine the graphids
from the database.

And so, this script only needs a Zabbix frontend user, no direct database
access is necessary.
Also, this script doesn't need to write any temporary files.
It is written in Python as I know the language best and everything necessary
is included in the standard libraries, at least since Python 2.6, maybe even earlier.

To get it working, simply edit the parameters below and maybe set up a cronjob
to execute this script once a day or once a way or whatever you prefer.

The graphs are queried from the Zabbix frontend and then sent as attachments
via mail to the configured address.
"""


from cookielib import CookieJar
from datetime import datetime, timedelta
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate
from socket import getfqdn
from urllib import urlencode
from urllib2 import build_opener, HTTPCookieProcessor
import smtplib


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


#----------------------------------------------------------------------
def login():
    url = u'%s/index.php' % ZABBIX_FRONTEND_URL
    data = urlencode(dict(
        form='1',
        form_refresh='1',
        name=ZABBIX_USERNAME,
        password=ZABBIX_PASSWORD,
        enter='Enter'))
    cookie_jar = CookieJar()
    cookie_processor = HTTPCookieProcessor(cookie_jar)
    opener = build_opener(cookie_processor)

    # since we only call the index page to login, we are not interested in the output
    # TODO error handling
    opener.open(url, data)

    return cookie_jar


#----------------------------------------------------------------------
def logout(cookie_jar):
    url = u'%s/index.php' % ZABBIX_FRONTEND_URL
    data = urlencode(dict(reconnect='1'))

    cookie_processor = HTTPCookieProcessor(cookie_jar)
    opener = build_opener(cookie_processor)

    opener.open(url, data)


#----------------------------------------------------------------------
def get_graph(cookie_jar, graph_id, start_time):
    url = u'%s/chart2.php' % ZABBIX_FRONTEND_URL
    data = urlencode(dict(
            stime=start_time,
            graphid=graph_id,
            width=GRAPH_WIDTH,
            height=GRAPH_HEIGHT,
            period=GRAPH_PERIOD))

    cookie_processor = HTTPCookieProcessor(cookie_jar)
    opener = build_opener(cookie_processor)

    request = opener.open(url, data)
    graph_image = request.read()
    return graph_image


#----------------------------------------------------------------------
def send_mail(images):
    msg = MIMEMultipart()
    msg['From'] = SMTP_FROM
    msg['To'] = u', '.join(SMTP_TO)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = SMTP_SUBJECT

    msg.attach(MIMEText(u'Zabbix Report'))

    i = 0
    for image in images:
        part = MIMEBase('image', 'png')
        part.set_payload(image)
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s.png"' % i)
        msg.attach(part)
        i += 1

    smtp = smtplib.SMTP(SMTP_SERVER)
    smtp.sendmail(SMTP_FROM, SMTP_TO, msg.as_string())
    smtp.close()


#----------------------------------------------------------------------
def main():
    start_time = datetime.now() - timedelta(seconds=GRAPH_PERIOD)
    start_time = start_time.strftime(u'%Y%m%d%H%M%S')

    cookie_jar = login()

    images = list()
    for graph_id in GRAPH_IDS:
        image = get_graph(cookie_jar, graph_id, start_time)
        images.append(image)

    logout(cookie_jar)

    send_mail(images)


if __name__ == '__main__':
    main()
