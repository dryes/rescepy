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

import argparse,os,re,shutil,socket,sys,urllib.request
from rescepy.cfv import CFV
from rescepy.srr import SRR
from rescepy.srs import SRS
from rescepy.unrar import UnRAR


def init_argparse():
	parser = argparse.ArgumentParser(description='automated srr/srs reconstruction.', usage=os.path.basename(sys.argv[0]) + ' [--opts] input1 [input2] ...')

	parser.add_argument('input', nargs='*', help='dirname', default='')

	parser.add_argument('--force', '-f', action='store_true', help='proceed if rars/samples already exist', default=False)

	parser.add_argument('--sample-only', '-s', action='store_true', help='process samples only - no rars', default=False)

	parser.add_argument('--srr-dir', default=None)

	parser.add_argument('--srr-bin', default=None)
	parser.add_argument('--srs-bin', default=None)
	parser.add_argument('--cfv-bin', default=None)
	parser.add_argument('--unrar-bin', default=None)

	args = parser.parse_args()

	return vars(args)

def dircheck(input):
	if re.search(r'[._-](dir|id3|nfo|sample|(vob)?sub(title)?s?|track).?(fix|pack)[._-]', input, re.IGNORECASE) is not None:
		print('%r detected as fix, skipping.' % (input))
		return False
	elif re.search(r'[._-](divx|xvid|[hx]264|wmv(hd)?)[._-]', input, re.IGNORECASE) is None:
		print('%r not video release, skipping.' % (input))
		return False

	return True

def prepare(input):
	ds = []
	for d in os.listdir():
		if d != os.path.basename(input) and os.path.isdir(d):
			try:
				os.chdir(d)
				for f in os.listdir():
					if os.path.isfile(os.path.join(os.pardir, os.path.basename(f))):
						os.unlink(os.path.join(os.pardir, os.path.basename(f)))
					shutil.move(f, os.pardir)
				ds.append(d)
				os.chdir(os.pardir)
			except:
				if len(str(sys.exc_info()[1])) > 0:
					print(sys.exc_info()[1])
				return False	

	for d in ds:
		try:
			os.rmdir(d)
		except:
			if len(str(sys.exc_info()[1])) > 0:
				print(sys.exc_info()[1])
			return False

	if os.path.basename(os.getcwd()) != input:
		try:
			os.chdir(input)
		except:
			if len(str(sys.exc_info()[1])) > 0:
				print(sys.exc_info()[1])
			return False

def getsrr(srrfile, dirname, srrdir):
	if not os.path.isfile(srrfile):
		if srrdb(dirname, srrdir) == False:
			return False

	if srrdir != os.getcwd():
		try:
			shutil.copy(srrfile, os.getcwd())
		except:
			if len(str(sys.exc_info()[1])) > 0:
				print(sys.exc_info()[1])
			return False

def getsubslist():
	subslist = []
	for f in os.listdir(os.getcwd()):
		if re.search(r'[._-](vob)?sub(title)?s?[._-]?.*\.(r(ar|\d+)|sfv|srt|idx|sub)$', f, re.IGNORECASE) is not None:
			subslist.append(f)

	return sorted(subslist)

def getrarlist(subslist):
	rarlist = []
	for f in os.listdir(os.getcwd()):
		if f not in subslist and re.search(r'\.(rar|[a-z]\d{2}|\d{3})$', f, re.IGNORECASE) is not None:
			rarlist.append(f)

	return sorted(rarlist)

def movesubs(subslist):
	if len(subslist) > 0:
		if not os.path.isdir(os.path.join(os.getcwd(), 'Subs')):
			os.mkdir(os.path.join(os.getcwd(), 'Subs'))
	for f in subslist:
		try:
			shutil.move(f, os.path.join(os.getcwd(), 'Subs', os.path.basename(f)))
		except:
			if len(str(sys.exc_info()[1])) > 0:
				print(sys.exc_info()[1])
			return False

def rarexist(srrlist, rarlist):
	rar = None
	if os.path.isfile(os.path.join(os.getcwd(), srrlist[2][0])):
		rar = srrlist[2][0]
	elif len(rarlist) > 0:
		rar = rarlist[0]

	return rar

def rarsexist(rar, srr, rarlist, srrlist, args):
	print('%r found, rars exist.' % (rar))
	if srr.extract() == False:
		return False

	if args['force'] == False and sfvverify(args) != False:
		return True

	rarlist = getrarlist(getsubslist())
	if sorted(srrlist)[0] == sorted(rarlist)[0] and args['force'] == False:
		return True

	for f in set(srrlist[2] + rarlist):
		if os.path.isfile(f):
			if re.search(r'\.((part0?0?1\.)?rar|001)$', f, re.IGNORECASE) is not None:
				unrar = UnRAR(filename=f, binary=args['unrar_bin'])
				if unrar.unrar() == False:
					return False

			try:
				os.unlink(os.path.join(os.getcwd(), f))
			except:
				if len(str(sys.exc_info()[1])) > 0:
					print(sys.exc_info()[1])
				return False

	return None

def inputexist(srrlist):
	nf = 0
	for f in srrlist[3]:
		if not os.path.isfile(os.path.join(os.getcwd(), f.split('/')[-1])):
			print('Input file: %r not found.' % (f))
			nf = (nf+1)
	
	if nf > 0:
		return False

def deleteothers(srrlist, srrfile):
	for f in os.listdir():
		if f not in srrlist[1] and f != os.path.basename(srrfile) and os.path.isfile(f):
			try:
				os.unlink(f)
			except:
				if len(str(sys.exc_info()[1])) > 0:
					print(sys.exc_info()[1])
				return False

def recreatesample(srr, srrlist, args):
	if srr.extract() == False:
		return False
	for f in srrlist[0]:
		if re.search(r'\.srs$', f, re.IGNORECASE) is not None:
			srs = SRS(filename=f, binary=args['srs_bin'])
			srslist = srs.list()

			sample = None
			if os.path.isfile(os.path.join(os.getcwd(), srslist[0])):
				sample = srslist[0]
			elif os.path.isfile(os.path.join(os.getcwd(), 'Sample', srslist[0])):
				sample = 'Sample' + os.sep + srslist[0]

			if sample is not None:
				print('%r found, sample exists.' % (sample))
				if args['force'] == False:
					return True

				try:
					os.unlink(sample)
				except:
					if len(str(sys.exc_info()[1])) > 0:
						print(sys.exc_info()[1])
					return False
			
			if srs.recreate(input=srrlist[1][0]) == False:
				return False

			try:
				os.unlink(f)
			except:
				if len(str(sys.exc_info()[1])) > 0:
					print(sys.exc_info()[1])
				return False

def sfvverify(args, opts=''):
	cfv = CFV(binary=args['cfv_bin'])
	if cfv.verify(opts) == False:
		return False

def srrdb(dirname, srrdir):
	srrfile = os.path.join(srrdir, dirname + '.srr')

	try:
		socket.setdefaulttimeout(30)
		urllib.request.urlretrieve('http://www.srrdb.com/download.php?release=%s' % (dirname), srrfile)
	except:
		if len(str(sys.exc_info()[1])) > 0:
			print(sys.exc_info()[1])
		return False

	if os.path.getsize(srrfile) == 0 or not os.path.isfile(srrfile):
		print('%r not found on srrdb.com' % (dirname))
		try:
			os.unlink(srrfile)
		except:
			if len(str(sys.exc_info()[1])) > 0:
				print(sys.exc_info()[1])
		return False

	print('\'%s.srr\' downloaded successfully.' % (dirname))
	return None

def main(args, input):
	input = os.path.normpath(os.path.expanduser(input))
	if not os.path.isdir(input) or input == '.':
		return False
	try:
		os.chdir(input)
	except:
		if len(str(sys.exc_info()[1])) > 0:
			print(sys.exc_info()[1])
		return False

	if args['sample_only'] == False:
		if dircheck(input) == False:
			return True
		if prepare(input) == False:
			return False

	if args['srr_dir'] == None:
		srrdir = os.getcwd()
	else:
		srrdir = os.path.normpath(os.path.expanduser(args['srr_dir']))
	if not os.path.isdir(srrdir):
		try:
			os.makedirs(srrdir)
		except:
			if len(str(sys.exc_info()[1])) > 0:
				print(sys.exc_info()[1])
			return False
	dirname = os.path.dirname(input + os.sep)
	srrfile = os.path.join(srrdir, dirname + '.srr')

	if getsrr(srrfile, dirname, srrdir) == False:
		return False
	srrfile = os.path.join(os.getcwd(), dirname + '.srr')

	srr = SRR(filename=srrfile, binary=args['srr_bin'])
	srrlist = srr.list()

	if args['sample_only'] == True:
		if recreatesample(srr, srrlist, args) == False:
			return False
		else:
			return True

	subslist = getsubslist()
	if movesubs(subslist) == False:
		return False

	rarlist = getrarlist(subslist)
	rar = rarexist(srrlist, rarlist)

	if rar is not None:
		rarsexistbool = rarsexist(rar, srr, rarlist, srrlist, args)
		if rarsexistbool == False:
			return False
		elif rarsexistbool == True:
			prepare(input)
			return True
	
	if inputexist(srrlist) == False:
		return False

	if srr.reconstruct() == False:
		return False

	if deleteothers(srrlist, srrfile) == False:
		return False

	recreatesamplebool = recreatesample(srr, srrlist, args)
	if recreatesamplebool == False:
		return False

	if srrdir != os.getcwd():
		try:
			os.unlink(srrfile)
		except:
			if len(str(sys.exc_info()[1])) > 0:
				print(sys.exc_info()[1])
			return False

	subslist = getsubslist()
	if movesubs(subslist) == False:
		return False

	if sfvverify(args, opts='-r') == False:
		return False

if __name__ == '__main__':
	args = init_argparse()
	err = 0
	cwd = os.getcwd()
	for d in args['input']:
		print('Processing: %s\n' % (d))
		if main(args, d) == False:
			err = (err+1)
		os.chdir(cwd)

	if err > 0:
		print('Errors: %s' % (err))
		sys.exit(1)