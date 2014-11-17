#!/usr/bin/python2

# Author: Joseph Wiseman <joswiseman@outlook>
# URL: https://github.com/d2yes/rescepy/
#
# This file is part of rescepy.
#

import argparse,json,os,re,shutil,socket,sys,urllib,zlib

from rescepy.cfv import CFV
from rescepy.srr import SRR
from rescepy.srs import SRS
from rescepy.unrar import UnRAR


def init_argparse():
    parser = argparse.ArgumentParser(description='automated srr verification and reconstruction.', usage=os.path.basename(sys.argv[0]) + ' [--opts] input1 [input2] ...')

    parser.add_argument('input', nargs='*', help='file/directory', default='')

    parser.add_argument('--force', '-f', action='store_true', help='proceed if rars/samples already exist', default=False)
    parser.add_argument('--sample-only', '-s', action='store_true', help='process samples only - no rars', default=False)
    parser.add_argument('--download', '-d', action='store_true', help='force download of srr', default=False)
    parser.add_argument('--no-process', '-n', action='store_true', help='do not process files - check srr exists only', default=False)

    parser.add_argument('--srr-dir', default=None)

    parser.add_argument('--srr-bin', default=None)
    parser.add_argument('--srs-bin', default=None)
    parser.add_argument('--cfv-bin', default=None)
    parser.add_argument('--unrar-bin', default=None)
    parser.add_argument('--rar-dir', default=None)

    args = parser.parse_args()

    return vars(args)

def dircheck(inputdir):
    if re.search(r'[._-](dir|id3|nfo|sample|(vob)?sub(title)?s?|track).?(fix|pack)[._-]', inputdir, re.IGNORECASE) is not None:
        print '\'%s\' detected as fix, skipping.' % (inputdir)
        return False

    return None

def prepare(inputdir):
    files = []
    dirs = []
    for r, s, f in os.walk(os.getcwd()):
        if len(dirs) == 0:
            dirs.append(s)
        for sf in f:
             files.append(os.path.join(r, sf))

    for f in files:
        try:
            dest = os.path.join(inputdir, os.path.basename(f))
            if f == dest:
                continue
            if os.path.isfile(dest):
                os.unlink(dest)
            shutil.move(f, inputdir)
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]
            return False 

    for d in dirs[0]:
        try:
            os.rmdir(d)
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]
            return False

    return None

def getsrr(srrfile, dirname, srrdir, download):
    if not os.path.isfile(srrfile) or download == True:
        if srrdbget(dirname, srrdir) == False:
            return False

    if srrdir != os.getcwd():
        try:
            shutil.copy(srrfile, os.getcwd())
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]
            return False

    return True

def getsubsfiles():
    subsfiles = []
    for r, s, f in os.walk(os.getcwd()):
        for subs in f:
            if re.search(r'([._-](vob)?sub(?!bed|marine|par)(title)?s?[._-]?.*\.(r(ar|\d+)|sfv|srt|idx|sub|srr)|\.(srt|idx|sub))$', subs, re.IGNORECASE) is not None:
                subsfiles.append(subs)

    return sorted(subsfiles)

def getrarfiles(subsfiles):
    rarfiles = []
    for r, s, f in os.walk(os.getcwd()):
        for rar in f:
            if rar not in subsfiles and re.search(r'\.(rar|[a-z]\d{2}|\d{3})$', rar, re.IGNORECASE) is not None:
                rarfiles.append(rar)

    return sorted(rarfiles)

def movesubs(subsfiles, storedfiles):
    if len(subsfiles) == 0:
        return True

    subsdir = None
    for f in storedfiles:
        if re.search(r'^(vob)?sub(title)?s?\/', f, re.IGNORECASE) is not None:
            subsdir = os.path.join(os.getcwd(), f.split('/')[0])
            break

    defaultdir = os.path.join(os.getcwd(), 'Subs')
    if subsdir is not None:
        subsdir = subsdir      
    else:
        subsdir = defaultdir

    if not os.path.isdir(subsdir):
        try:
            os.mkdir(subsdir)
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]
            return False

    if subsdir != defaultdir and os.path.isdir(defaultdir):
        try:
            for f in os.listdir(defaultdir):
                shutil.copy(os.path.join(defaultdir, f), subsdir)
            shutil.rmtree(defaultdir)
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]
            return False

    for f in set(subsfiles):
        try:
            shutil.copy(os.path.join(os.getcwd(), f), subsdir)
            os.unlink(f)
        except:
            None
            #if len(str(sys.exc_info()[1])) > 0:
            #    print sys.exc_info()[1]
            #return False

    return subsdir

def rarexist(srrlist, rarfiles):
    rar = None
    if os.path.isfile(os.path.join(os.getcwd(), srrlist[2][0])):
        rar = srrlist[2][0]
    elif len(rarfiles) > 0:
        rar = rarfiles[0]

    return rar

def rarsexist(rarlist, subsfiles, isvideobool, inputdir, args):
    if args['force'] == False and sfvverify(args, opts='-r') != False:
        return True

    rarfiles = getrarfiles(subsfiles)
    ##do not proceed if only extra rars (eg subs) are missing.
    if sorted(rarlist) == sorted(rarfiles) and args['force'] == False:
        return True

    if isvideobool == True:
        if prepare(inputdir) == False:
            return False

    for f in set(rarlist + rarfiles):
        if not os.path.isfile(f):
            continue

        if re.search(r'\.(rar|001)$', f, re.IGNORECASE) is not None:
            if re.search(r'\.part[0-9]{1,}\.rar$', f, re.IGNORECASE) is not None:
                if re.search(r'\.part0*1\.rar$', f, re.IGNORECASE) is None:
                    continue
            unrar = UnRAR(filename=f, binary=args['unrar_bin'])
            if unrar.extract() == False:
               return False

    for f in set(rarlist + rarfiles):
        if os.path.isfile(f):
            try:
                os.unlink(os.path.join(os.getcwd(), f))
            except:
                if len(str(sys.exc_info()[1])) > 0:
                    print sys.exc_info()[1]
                return False

    return None

def deleteothers(keeplist, srrfile):
    do = []
    for o in os.listdir(os.getcwd()):
        if o not in keeplist:
            do.append(o)

    if len(do) == 0:
        return True

    for o in do:
        try:
            if os.path.isfile(o) and o != os.path.basename(srrfile):
                os.unlink(o)
            elif os.path.isdir(o) and not os.listdir(o):
                os.rmdir(o)
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]
            return False

    return None

def crc(infile):
    p = 0
    for l in open(infile, 'rb'):
        p = zlib.crc32(l, p)

    return '%X' % (p & 0xFFFFFFFF)

def recreatesample(srr, srrlist, args):
    for f in srrlist[0]:
        if re.search(r'\.srs$', f, re.IGNORECASE) is None:
            continue

        srsfile = f
        if not os.path.isfile(srsfile) and os.path.isfile(os.path.basename(f)):
            srsfile = os.path.basename(f)

        if not os.path.isfile(srsfile):
            return False

        srs = SRS(filename=srsfile, binary=args['srs_bin'])
        srsinfo = srs.info()
        if srsinfo == False:
            continue

        defaultdir = os.path.join(os.getcwd(), 'Sample')
        if '/' in srsfile:
            sampledir = os.path.join(os.getcwd(), srsfile.split('/')[0])
        else:
            sampledir = defaultdir

        if not os.path.isdir(sampledir):
            try:
                os.mkdir(sampledir)
            except:
                if len(str(sys.exc_info()[1])) > 0:
                    print sys.exc_info()[1]
                return False

        if sampledir != defaultdir and os.path.isdir(defaultdir):
            try:
                for s in os.listdir(defaultdir):
                    shutil.copy(os.path.join(defaultdir, s), sampledir)
                shutil.rmtree(defaultdir)
            except:
                if len(str(sys.exc_info()[1])) > 0:
                    print sys.exc_info()[1]
                return False

        if os.path.isfile(os.path.join(os.getcwd(), srsinfo[0])):
            try:
                shutil.move(os.path.join(os.getcwd(), srsinfo[0]), sampledir)
            except:
                if len(str(sys.exc_info()[1])) > 0:
                    print sys.exc_info()[1]
                return False

        sample = None
        if os.path.isfile(os.path.join(sampledir, srsinfo[0])):
            sample = os.path.join(sampledir, srsinfo[0])

        if sample is not None:
            print '\'%s\' found, sample exists.' % (os.path.dirname(sample).split(os.sep)[-1] + os.sep + sample.split(os.sep)[-1])

            if crc(sample) == srsinfo[2] and args['force'] == False:
                try:
                    os.unlink(srsfile)
                except:
                    if len(str(sys.exc_info()[1])) > 0:
                        print sys.exc_info()[1]
                    return False

                continue

            try:
                os.unlink(sample)
            except:
                if len(str(sys.exc_info()[1])) > 0:
                    print sys.exc_info()[1]
                return False

        srsinput = None
        if os.path.isfile(srrlist[1][0]):
            srsinput = srrlist[1][0]
        elif os.path.isfile(srrlist[1][0].split('/')[-1]):
            srsinput = srrlist[1][0].split('/')[-1]

        if srsinput is not None:
            if srs.recreate(infile=srsinput, outdir=sampledir + os.sep) == False:
                return False

        try:
            os.unlink(srsfile)
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]
            return False

    return None

def recreatetags(srrlist, srrfile, args):
    listdir = os.listdir(os.getcwd())
    keeplist = []
    srsfiles = []

    for srsfile in sorted(srrlist[0]):
        if re.search(r'\.srs$', srsfile, re.IGNORECASE) is None:
            keeplist.append(srsfile)
            continue

        srsfiles.append(srsfile)

        srs = SRS(filename=srsfile, binary=args['srs_bin'])
        srsinfo = srs.info()
        if srsinfo == False:
            continue
        keeplist.append(srsinfo[0])

        if '/' in srsfile:
            outdir = os.path.join(os.getcwd(), srsfile.split('/')[0])
            if not os.path.isdir(outdir):
                try:
                    os.mkdir(outdir)
                except:
                    if len(str(sys.exc_info()[1])) > 0:
                        print sys.exc_info()[1]
                    return False
        else:
            outdir = os.getcwd()

        infile = None
        if os.path.isfile(os.path.join(outdir, srsinfo[0])):
            infile = os.path.join(outdir, srsinfo[0])
        elif os.path.isfile(os.path.join(os.getcwd(), srsinfo[0])):
            infile = os.path.join(os.getcwd(), srsinfo[0])
        else:
            print 'Input file not found: %s' % (srsinfo[0])

        if infile is None:
            infile = os.path.join(outdir, srsinfo[0])
            fr = r'^' + srsinfo[0].split('/')[-1].split('-')[0] + r'[-_ ].*\.' + srsinfo[0].split('.')[-1] + r'$'
            for srsfile in listdir:
                if srsfile == infile.split(os.sep)[-1] or re.search(fr, srsfile, re.IGNORECASE) is not None:
                    try:
                        shutil.copy(srsfile, infile)
                    except:
                        if len(str(sys.exc_info()[1])) > 0:
                            print sys.exc_info()[1]
                        return False

                    if srs.recreate(infile, outdir=outdir) == True:
                        break
                    else:
                        try:
                            os.unlink(infile)
                        except:
                            if len(str(sys.exc_info()[1])) > 0:
                                print sys.exc_info()[1]
                            return False

        elif srs.recreate(infile, outdir=outdir) == False:
            return False

        if infile == os.path.join(os.getcwd(), srsinfo[0]) and outdir != os.getcwd():
            try:
                os.unlink(infile)
            except:
                if len(str(sys.exc_info()[1])) > 0:
                    print sys.exc_info()[1]
                return False

    if sfvverify(args, opts='-r') == False:
        return False

    if len(keeplist) > 0 and len(srsfiles) > 0 and deleteothers(keeplist, srrfile) == False:
        return False

    return None

def sfvverify(args, opts=''):
    cfv = CFV(binary=args['cfv_bin'])
    if cfv.verify(opts) == False:
        return False

    return True

def deletesrs():
    for r, s, f in os.walk(os.getcwd()):
       for srs in f:
           if srs.endswith('.srs'):
               try:
                   os.unlink(os.path.join(r, srs))
               except:
                   if len(str(sys.exc_info()[1])) > 0:
                       print sys.exc_info()[1]
                   return False

    return True

def srrdbget(dirname, srrdir):
    srrfile = os.path.join(srrdir, dirname + '.srr')

    sys.stdout.write('Searching on srrdb.com ... ')
    sys.stdout.flush()
    try:
        socket.setdefaulttimeout(30)
        urllib.urlretrieve('http://www.srrdb.com/download/srr/%s' % (dirname), srrfile)
    except:
        if len(str(sys.exc_info()[1])) > 0:
            print sys.exc_info()[1]
        return False

    erm = None
    if not os.path.isfile(srrfile) or os.path.getsize(srrfile) == 0:
        erm = 'not found.'
    elif os.path.isfile(srrfile) and os.path.getsize(srrfile) < 50:
        try:
            erm = open(srrfile, 'r').readlines()[0].lower()
        except:
            erm = 'not found.'

    if erm is not None:
        print '%s' % (erm)
        try:
            os.unlink(srrfile)
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]
        return False

    print 'downloaded successfully.\n'
    return True

def srrdbidentify(crc):
    sys.stdout.write('Searching on srrdb.com ... ')
    sys.stdout.flush()
    try:
        socket.setdefaulttimeout(30)
        response = json.load(urllib.urlopen('http://www.srrdb.com/api/search/archive-crc:%s' % (crc)))
    except:
        if len(str(sys.exc_info()[1])) > 0:
            print sys.exc_info()[1]

    if not response or response['resultsCount'] != 1:
        print 'not found.'
        return False

    print 'found: %s' % (response['results'][0]['release'])
    return response['results'][0]['release']

def recreatesubs(subsdir, srrfile, args):
    srrfile = os.path.join(subsdir, srrfile)
    subssrr = SRR(filename=srrfile, binary=args['srr_bin'], rardir=args['rar_dir'])
    srrlist = subssrr.filelist()

    ##add sfv/crc verification
    if os.path.isfile(os.path.join(subsdir, srrlist[1][0])):
        try:
            os.unlink(srrfile)
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]
        return True

    innersrrfile = None
    for f in srrlist[0]:
        if re.search(r'\.srr$', f, re.IGNORECASE) is not None:
            subssrr.extract(opts='-o %s' % (subsdir))
            innersrrfile = os.path.join(subsdir, f)
            break

    innersrr = None
    if innersrrfile is not None:
        innersrr = SRR(filename=innersrrfile, binary=args['srr_bin'], rardir=args['rar_dir'])

    success = None
    if innersrr is not None and innersrr.verify() == True and innersrr.reconstruct(opts='-o %s' % (subsdir)) == False:
        success = False
    if success == None and subssrr.verify() == True and subssrr.reconstruct(opts='-o %s' % (subsdir)) == False:
        success = False

    srrlist[0].append(srrfile)
    for f in srrlist[0]:
        try:
            os.unlink(os.path.join(subsdir, f))
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]

    return success

def isvideo(dirname):
    if re.search(r'[._-]((dv)?divx|xvid(vd)?|[hx]26[45]|wmv(hd)?|dvd[r59])[._-]', dirname, re.IGNORECASE) is not None:
        return True
    else:
        return False

def main(inputdir, args):
    try:
        os.chdir(inputdir)
    except:
        if len(str(sys.exc_info()[1])) > 0:
            print sys.exc_info()[1]
        return False

    if args['srr_dir'] == None:
        srrdir = os.getcwd()
    else:
        srrdir = os.path.abspath(args['srr_dir'])
        if not os.path.isdir(srrdir):
            try:
                os.makedirs(srrdir)
            except:
                if len(str(sys.exc_info()[1])) > 0:
                    print sys.exc_info()[1]
                return False

    dirname = inputdir.split(os.sep)[-1]
    srrfile = os.path.join(srrdir, dirname + '.srr')

    if getsrr(srrfile, dirname, srrdir, args['download']) == False:
        return False
    if args['no_process'] == True:
        print '\'%s.srr\' exists.' % (dirname)
        return True
    srrfile = os.path.join(os.getcwd(), dirname + '.srr')

    isvideobool = isvideo(dirname)

    if isvideobool == True and args['sample_only'] == False:
        if dircheck(inputdir) == False:
            return True

    srr = SRR(filename=srrfile, binary=args['srr_bin'], rardir=args['rar_dir'])
    srrlist = srr.filelist()

    if srrlist[1] is None:
        #assume audio
        if args['force'] == False:
            if srr.extract() == True and sfvverify(args, opts='-r') == True and deletesrs() == True:
                return True
        if prepare(inputdir) == False or srr.extract() == False or recreatetags(srrlist, srrfile, args) == False:
                deletesrs()
                return False
        return True

    if srr.extract() == False:
        return False

    if isvideobool == True and args['sample_only'] == True:
        if recreatesample(srr, srrlist, args) == False or deleteothers(set(srrlist[0] + srrlist[1] + srrlist[2]), srrfile) == False:
            return False
        else:
            return True

    subsfiles = getsubsfiles()
    subsdir = movesubs(subsfiles, srrlist[0])
    if subsdir == False:
        return False

    for f in subsfiles:
        if re.search(r'\.srr$', f, re.IGNORECASE) is not None:
            if recreatesubs(subsdir, f, args) == False:
                print 'Error recreating subtitle rars in: %s' % (subsdir.split(os.sep)[-1])

    rar = rarexist(srrlist, getrarfiles(subsfiles))
    if rar is not None:
        print '\'%s\' found, rars exist.' % (rar)
        rarsexistbool = rarsexist(srrlist[2], subsfiles, isvideobool, inputdir, args)
        if rarsexistbool == False:
            return False
        elif rarsexistbool == True:
            if recreatesample(srr, srrlist, args) == False or deleteothers(set(srrlist[0] + srrlist[1] + srrlist[2]), srrfile) == False:
                return False

            return True

    if srr.verify() == False:
        return False

    if srr.reconstruct() == False:
        return False

    if isvideobool == True:
        if recreatesample(srr, srrlist, args) == False:
            deleteothers(set(srrlist[0] + srrlist[1] + srrlist[2]), srrfile)
            return False

    if movesubs(getsubsfiles(), srrlist[0]) == False:
        return False

    if deleteothers(set(srrlist[0] + srrlist[1] + srrlist[2]), srrfile) == False:
        return False

    if srrdir != os.getcwd():
        try:
            os.unlink(srrfile)
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]
            return False

    if sfvverify(args, opts='-r') == False:
        return False

if __name__ == '__main__':
    args = init_argparse()
    erc = 0
    erd = []
    cwd = os.getcwd()

    for f in set(args['input']):
        if not os.path.isfile(f) or re.search(r'\.(flac|mp[23]|ogg)$', f, re.IGNORECASE) is not None:
            continue

        print '\nProcessing: %s\n' % (f.split(os.sep)[-1])
        dirname = srrdbidentify(crc(f))
        if dirname is False:
            erc = (erc+1)
            continue

        dirname = os.path.abspath(os.path.join(os.path.dirname(f), dirname))
        try:
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
            shutil.move(f, dirname)
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]

        if dirname not in args['input']:
            args['input'].append(dirname)

    for d in set(args['input']):
        try:
            os.chdir(cwd)
        except:
            if len(str(sys.exc_info()[1])) > 0:
                print sys.exc_info()[1]
            break
        d = os.path.abspath(d)
        if not os.path.isdir(d):
            continue

        print '\nProcessing: %s\n' % (d.split(os.sep)[-1])
        if main(d, args) == False:
            erc = (erc+1)
            erd.append(d)

    if erc > 0:
        print '\nErrors: %s' % (erc)
        for d in erd:
            print '%s' % (d)
        sys.exit(1)
