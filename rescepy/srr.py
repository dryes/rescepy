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

class SRR:
    def __init__(self, filename, binary=None):
        self.filename = filename
        if binary == None:
            if os.name == 'posix':
                self.binary = '/usr/bin/srr'
            elif os.name == 'nt':
                self.binary = 'srr'
        else:
            self.binary = binary

    def extract(self, opts=''):
        sp = subprocess.Popen('%s %r %s -x -p -y' % (self.binary, self.filename, opts), shell=True, stdin=subprocess.PIPE)
        sp.communicate()
        if sp.returncode == 0:
            return True
        else:
            return False

    def reconstruct(self, opts=''):
        sp = subprocess.Popen('%s %r %s -c -p -r -y' % (self.binary, self.filename, opts), shell=True, stdin=subprocess.PIPE)
        sp.communicate()
        if sp.returncode == 0:
            return True
        else:
            return False

    def list(self):
        #TODO: this is filth; use proper means of determining content
        sg = subprocess.getoutput('%s %r -l' % (self.binary, self.filename)).split(':')

        ##stored files.
        sft = (sg[2].split('\n'))
        del sft[0]
        sft[-1] = sft[-1][:-1]
        sf = []
        for f in sft:
            sf.append(f.split(' ')[-1])
        if sf[-1] == 'file':
            del sf[-1]
        if sf[-1] == '':
            del sf[-1]

        ##rar files.
        rf = None
        try:
            sg[3]
        except IndexError:
            sg.append(None)
        if sg[3] is not None:
            rft = (sg[3].split('\n\t'))
            del rft[0]
            rft[-1] = rft[-1][:-1]
            rf = []
            for f in rft:
                rf.append(f.split(' ')[0])

        ##rar files - no dirs.
        rfnd = None
        if rf is not None:
            rfnd = []
            for f in rf:
                rfnd.append(f.split('/')[-1])

        ##archived files.
        af = None
        try:
            sg[4]
        except IndexError:
            sg.append(None)
        if sg[4] is not None:
            aft = (sg[4].split('\t'))
            del aft[0]
            af = []
            for f in aft:
                af.append(f.replace('\n', '').replace('\\', '/').split(' ')[0])

        return (sf, rf, rfnd, af)
