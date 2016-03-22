#
# Copyright (c) 2009-2015, Mendix bv
# All Rights Reserved.
#
# http://www.mendix.com/
#

import getpass
import os
from log import logger


class M2EEConfig:

    def __init__(self):
        if os.getenv('MXURL', None):
            self.url = os.getenv('MXURL')
        else:
            self.url = raw_input(
                'Give url, i.e.: https://my.app.com\n'
            ).strip()

        if self.url.endswith('/'):
            self.url = self.url[:-1]
        if not self.url.startswith('http'):
            self.url = 'https://' + self.url
        logger.info('using url %s' % self.url)

        if os.getenv('MXPASSWORD', None):
            self.password = os.getenv('MXPASSWORD')
        else:
            self.password = getpass.getpass(
                'Give admin password, from the ADMIN_PASSWORD env var'
            ).strip()

        self.url = self.url + '/_mxadmin/'

        logger.info('')
        logger.info('try the help command to get started')
