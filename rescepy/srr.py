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

import os,re,subprocess

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

    def listfiles(self):
        #TODO: this is filth; use proper means of determining content
        sg = subprocess.getoutput('%s %r -l' % (self.binary, self.filename)).split(':')

        ##stored files.
        sft = (sg[2].split('\n'))
        del sft[0]
        sft[-1] = sft[-1][:-1]
        sf = []
        for f in sft:
            fm = re.match(r'[\d\,]+ (.*)', f.strip())
            if fm is not None and fm.group(1) is not None:
                sf.append(fm.group(1).strip())
                if '/' in fm.group(1):
                    sf.append(fm.group(1).split('/')[0].strip())
        if sf is not None:
            sf = list(set(sf))

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
                fm = re.match(r'(.*) [A-Z0-9]{8} \d+', f)
                if fm is not None and fm.group(1) is not None:
                    rf.append(fm.group(1).strip())
        

        ##rar files - no dirs.
        rfnd = None
        if rf is not None:
            rfnd = []
            for f in rf:
                rfnd.append(f.split('/')[-1])
                rfnd.append(f.split('/')[0])
        if rfnd is not None:
            rfnd = list(set(rfnd))


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
                fm = re.match(r'(.*) [A-Z0-9]{8} \d+', f)
                if fm is not None and fm.group(1) is not None:
                    af.append(fm.group(1).replace('\\', '/').strip())

        return (sf, rf, rfnd, af)
