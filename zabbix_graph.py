#!/usr/bin/env python
# coding: utf-8
#
#  zabbix_graph.py
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
This script reads one or more graphs from the Zabbix frontend and
sends them as attachments via mail.

For details about this script and its configuration, see README.rst.
"""


from cookielib import CookieJar
from datetime import datetime, timedelta
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate
from urllib import urlencode
from urllib2 import build_opener, HTTPCookieProcessor
from zabbix_common import Configuration
import smtplib



#----------------------------------------------------------------------
def login(config):
    url = u'%s/index.php' % config.zabbix_frontend_url
    data = urlencode(dict(
        form='1',
        form_refresh='1',
        name=config.zabbix_username,
        password=config.zabbix_password,
        enter='Enter'))
    cookie_jar = CookieJar()
    cookie_processor = HTTPCookieProcessor(cookie_jar)
    opener = build_opener(cookie_processor)

    # since we only call the index page to login, we are not interested in the output
    # TODO error handling
    opener.open(url, data)

    return cookie_jar


#----------------------------------------------------------------------
def logout(config, cookie_jar):
    url = u'%s/index.php' % config.zabbix_frontend_url
    data = urlencode(dict(reconnect='1'))

    cookie_processor = HTTPCookieProcessor(cookie_jar)
    opener = build_opener(cookie_processor)

    opener.open(url, data)


#----------------------------------------------------------------------
def get_graph(config, cookie_jar, graph_id, start_time):
    url = u'%s/chart2.php' % config.zabbix_frontend_url
    data = urlencode(dict(
            stime=start_time,
            graphid=graph_id,
            width=config.graph_width,
            height=config.graph_height,
            period=config.graph_period))

    cookie_processor = HTTPCookieProcessor(cookie_jar)
    opener = build_opener(cookie_processor)

    request = opener.open(url, data)
    graph_image = request.read()
    return graph_image


#----------------------------------------------------------------------
def send_mail(config, images):
    msg = MIMEMultipart()
    msg['From'] = config.smtp_from
    msg['To'] = u', '.join(config.smtp_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = config.smtp_subject

    msg.attach(MIMEText(u'Zabbix Report'))

    i = 0
    for image in images:
        part = MIMEBase('image', 'png')
        part.set_payload(image)
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s.png"' % i)
        msg.attach(part)
        i += 1

    smtp = smtplib.SMTP(config.smtp_server)
    smtp.sendmail(config.smtp_from, config.smtp_to, msg.as_string())
    smtp.close()


#----------------------------------------------------------------------
def main():
    config = Configuration()
    config.read()

    start_time = datetime.now() - timedelta(seconds=config.graph_period)
    start_time = start_time.strftime(u'%Y%m%d%H%M%S')

    cookie_jar = login(config)

    images = list()
    for graph_id in config.graph_ids:
        image = get_graph(config, cookie_jar, graph_id, start_time)
        images.append(image)

    logout(config, cookie_jar)

    send_mail(config, images)


if __name__ == '__main__':
    main()
