Various small Zabbix related scripts and utilities
==================================================


This is a collection of various scripts I wrote for my personal use
for Zabbix.


zabbix_graph.py
---------------
This script reads one or more graphs from the Zabbix frontend and
sends them as attachments via mail to one (or more) configured mail addresses.

The script is inspired by http://www.zabbix.com/forum/showthread.php?t=15316
but simpler as it just takes a list of graphids to work on instead
of using a special media report in Zabbix to determine the graphids
from the database.

And so, this script only needs a Zabbix frontend user, no direct database
access is necessary.
Also, this script does not need to write any temporary files.
It is written in Python as I know the language best and everything necessary
is included in the standard libraries, at least since Python 2.6, maybe even earlier.

The graphs are queried from the Zabbix frontend and then sent as attachments
via mail to the configured address.

This scripts is best to be used as a cronjob, maybe once a day or week, as you
prefer. Though there is basically no error handling, errors are printed to stderr
and so they are sent via mail to the administrator by the cron daemon,
assuming it is configured properly.



zabbix_smstrade.py
------------------
A script to send Zabbix alerts as SMS. The German SMS gateway 
http://www.smstrade.de is used as transport.
So, this script is pretty much specific for this provider and its HTTP API.

It is very similar to http://www.zabbix.com/wiki/howto/config/alerts/smsapi
but written in Python. Similarly, the subject is ignored, instead the message
is used as SMS text. Additionally, this script will cut the passed message text
after 160 characters to ensure only one (non-concatenated) SMS is sent.

The script should not produce any output normally. But it does log a status line
when the SMS is delivered to the smstrade.de API, including the response code to
the system's syslog daemon. Additionally, it logs any errors to syslog.
So, it can be used (and is intended to) as an alert script (media type script in Zabbix).


zabbix_common.py
----------------
This is not really a script, just some common code shared by various scripts. Simply ignore.



Common Configuration
--------------------

The scripts are configured by one shared config file.
A sample config file is included. You should copy it to 
one of the following locations (it is read in that order):

 * /etc/zabbix-scripts.conf
 * /etc/zabbix/zabbix-scripts.conf
 * ~/.zabbix-scripts.conf  (~ is replaced by the home directory of the user who executes this script)



License
-------
These scripts are distributed under the terms of the GNU General Public License
as published by the Free Software Foundation; version 2 of the license.
A copy of this license can be found in the file COPYING included with
the source code of this program.



Ideas, questions, patches and bug reports
-----------------------------------------
If you add something, or fix a bug, find a cool feature missing or just want to say hello,
please tell me. I'm always happy about feedback.


--
2011 by Enrico Tröger
