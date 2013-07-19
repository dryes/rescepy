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

##TODO: proper stored files parsing

import os,subprocess

class SRS:
    def __init__(self, filename, binary=None):
        self.filename = filename
        if binary == None:
            if os.name == 'posix':
                self.binary = '/usr/bin/srs'
            elif os.name == 'nt':
                self.binary = 'srs'
        else:
            self.binary = binary

    def recreate(self, input, output='Sample' + os.sep):
        sp = subprocess.Popen('%s %r %r -o %r -y' % (self.binary, self.filename, input, output), shell=True, stdin=subprocess.PIPE)
        sp.communicate()
        if sp.returncode == 0:
            return True
        else:
            return False

    def list(self):
        #TODO: this is filth; use proper means of determining content
        sg = subprocess.getoutput('%s %r -l' % (self.binary, self.filename)).split(':')

        ##sample name.
        sn = sg[3][:-12].strip()
        ##sample size.
        ss = sg[4][:-11].strip()
        ##sample crc.
        sc = sg[5].strip().split('\n')[0]

        return (sn, ss, sc)
