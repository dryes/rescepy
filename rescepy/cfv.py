# Author: Joseph Wiseman <joswiseman@gmail>
# URL: https://github.com/dryes/rescepy/
#
# This file is part of rescepy.
#
# rescepy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rescepy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rescepy.  If not, see <http://www.gnu.org/licenses/>.

import os,subprocess

class CFV:
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
        if sp.returncode == 0:
            return True
        else:
            return False
