# Author: Joseph Wiseman <joswiseman@outlook>
# URL: https://github.com/d2yes/rescepy/
#
# This file is part of rescepy.
#

import os,rescene,subprocess

class SRR(object):
    def __init__(self, filename, binary=None, rardir=None):
        self.filename = filename
        if binary == None:
            if os.name == 'posix':
                self.binary = '/usr/bin/srr'
            elif os.name == 'nt':
                self.binary = 'srr.exe'
        else:
            self.binary = binary

        if rardir is not None and os.path.isdir(rardir):
            self.rardir = rardir
        else:
            self.rardir = None

    def extract(self, opts=''):
        sp = subprocess.Popen('%s \'%s\' %s -x -p -y' % (self.binary, self.filename, opts), shell=True, stdin=subprocess.PIPE)
        sp.communicate()

        return True if sp.returncode == 0 else False

    def reconstruct(self, opts=''):
        if self.rardir is not None:
            z = '-z \'%s\'' % (self.rardir)
        else:
            z = ''

        sp = subprocess.Popen('%s \'%s\' %s -c -p -r %s -y' % (self.binary, self.filename, opts, z), shell=True, stdin=subprocess.PIPE)
        sp.communicate()

        return True if sp.returncode == 0 else False

    def verify(self, opts=''):
        print 'Verifying input files ...'
        sp = subprocess.Popen('%s \'%s\' %s -q -r -y' % (self.binary, self.filename, opts), shell=True, stdin=subprocess.PIPE)
        sp.communicate()

        return True if sp.returncode == 0 else False


    def filelist(self):
        srrinfo = rescene.info(self.filename)

        srrlist = []
        if len(srrinfo['stored_files']) > 0:
            srrlist.append(list(srrinfo['stored_files']))
        else:
            srrlist.append(None)

        if len(srrinfo['rar_files']) > 0:
            srrlist.append([])
            for k, v in (srrinfo['rar_files']).items():
                srrlist[1].append(v.file_name)
        else:
            srrlist.append(None)

        if srrlist[1] is not None:
            srrlist.append([])
            for f in srrlist[1]:
                srrlist[2].append(f.split('/')[-1])
        else:
            srrlist.append(None)
        if srrlist[2] is not None:
            srrlist[2] = list(set(srrlist[2]))
        else:
            srrlist.append(None)

        if len(srrinfo['archived_files']) > 0:
            srrlist.append(list(srrinfo['archived_files']))
        else:
            srrlist.append(None)

        return srrlist
