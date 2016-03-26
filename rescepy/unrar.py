# Author: Joseph Wiseman <joswiseman@cock.li>
# URL: https://github.com/dryes/rescepy/
#
# This file is part of rescepy.
#

import os,re,subprocess

class UnRAR(object):
    def __init__(self, filename=None, password=None, binary=None):
        self.filename = filename
        self.password = password
        if binary == None:
            if os.name == 'posix':
                self.binary = ('/usr/bin/unrar')
            elif os.name == 'nt':
                self.binary = ('unrar')
        else:
            self.binary = binary

    def extract(self, opts='-ierr -o+ -y'):
        if self.password is not None:
            opts += ' -p%s' % re.escape(self.password)
        sp = subprocess.Popen('%s x \"%s\" %s --' % (self.binary, self.filename, opts), shell=True, stdin=subprocess.PIPE)
        sp.communicate()

        return True if sp.returncode == 0 else False
