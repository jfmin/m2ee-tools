#
# Copyright (c) 2009-2015, Mendix bv
# All Rights Reserved.
#
# http://www.mendix.com/
#

import getpass


class M2EEConfig:

    def __init__(self):
        self.url = raw_input('Give url, i.e.: https://my.app.com\n').strip()
        if self.url.endswith('/'):
            self.url = self.url[:-1]
        if not self.url.startswith('http'):
            self.url = 'https://' + self.url
        print 'using url', self.url

        self.password = getpass.getpass(
            'Give admin password, from the ADMIN_PASSWORD env var'
        ).strip()

        self.url = self.url + '/_mxadmin/'

        print ''
        print 'try the help command to get started'
