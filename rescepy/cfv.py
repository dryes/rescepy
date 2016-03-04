# Author: Joseph Wiseman <joswiseman@cock.li>
# URL: https://github.com/d2yes/rescepy/
#
# This file is part of rescepy.
#

import os,subprocess

class CFV(object):
    def __init__(self, binary=None):
        if binary == None:
            if os.name == 'posix':
                self.binary = '/usr/bin/cfv'
            elif os.name == 'nt':
                self.binary = 'cfv'
        else:
            self.binary = binary

    def verify(self, opts=''):
        sp = subprocess.Popen('%s -vsn %s -t sfv' % (self.binary, opts), shell=True, stdin=subprocess.PIPE)
        sp.communicate()

        return True if sp.returncode == 0 else False
