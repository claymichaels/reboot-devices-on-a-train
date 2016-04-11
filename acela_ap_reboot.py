__author__ = 'Clay'

import paramiko
from cStringIO import StringIO
from time import sleep
from sys import argv
import logging
from logging.handlers import RotatingFileHandler
from sys import path
path.append('/home/automation/scripts/clayScripts/resources')
from claylib import check_if_online, helpdesk_key


# Set up logging
LOG_FILE = '/home/automation/scripts/clayScripts/logs/acela_ap_reboot.log'
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
#logger = logging.getLogger(__name__)
logging.getLogger("paramiko").setLevel(logging.ERROR)
handler = RotatingFileHandler(LOG_FILE,maxBytes=1000000)
logger.addHandler(handler)


# APs are in groups by <trainset#><AP#0-9>
# TS01 10-19, TS09 90-99, TS10 100-109


# This order seems to work best
ap_table = ['9', '7', '8', '6', '0', '1', '2', '3', '4', '5']
ap_ip_first_three = '10.125.18.'

if argv[-1] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']:
    trainset = argv[-1]
    logger.debug('Received argv[-1] of "%s"' % argv[-1])
else:
    logger.error('Invalid trainset "%s". Exiting!' % argv[-1])
    exit()


for ap in ap_table:
    ap_ip = ap_ip_first_three + trainset + ap
    if check_if_online(ap_ip):
        logger.debug('TS%s AP %s: Online' % (trainset, ap_ip))
        try:
            ap_connection = paramiko.SSHClient()
            key = paramiko.DSSKey.from_private_key(StringIO(helpdesk_key))
            ap_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ap_connection.connect(ap_ip, username='<SNIPPED USER>', password='<SNIPPED PW>', pkey=key, timeout=30)
            channel = ap_connection.invoke_shell()
            stdin = channel.makefile('wb')
            stdout = channel.makefile('rb')
            logger.debug('TS%s AP %s: Connected' % (trainset, ap_ip))
            sleep(1)
            channel.send("sys\r")
            sleep(1)
            channel.send("re\r")
            sleep(1)
            channel.send("yes\r")
            logger.info('TS%s AP %s: Rebooted' % (trainset, ap_ip))
        except paramiko, e:
            logger.error('TS%s AP %s: %s' % (trainset, ap_ip, e))
    else:
        logger.info('TS%s AP %s: Already offline. Possible issue?' % (trainset, ap_ip))
