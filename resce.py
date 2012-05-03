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
from rescepy.unrar import UNRAR


def init_argparse():
	parser = argparse.ArgumentParser(description='automated ReScene reconstruction.', usage=os.path.basename(sys.argv[0]) + ' [--opts] input')

	parser.add_argument('input', nargs='?', help='dirname', default='')

	parser.add_argument('--force', '-f', action='store_true', help='proceed if rars/samples already exist', default=False)

	parser.add_argument('--sample-only', '-s', action='store_true', help='process samples only - no rars', default=False)

	parser.add_argument('--srr-dir', default=None)

	parser.add_argument('--srr-bin', default=None)
	parser.add_argument('--srs-bin', default=None)
	parser.add_argument('--cfv-bin', default=None)
	parser.add_argument('--unrar-bin', default=None)

	args = parser.parse_args()

	return vars(args)

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

	return True

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

	return True

def main():
	args = init_argparse()

	input = os.path.normpath(args['input'])
	if not os.path.isdir(input):
		return False
	try:
		os.chdir(input)
	except:
		if len(str(sys.exc_info()[1])) > 0:
			print(sys.exc_info()[1])
			return False

	if args['sample_only'] == False:
		if prepare(input) == False:
			return False

	if args['srr_dir'] == None:
		srrdir = os.getcwd()
	else:
		srrdir = args['srr_dir']
	if not os.path.isdir(srrdir):
		try:
			os.makedirs(srrdir)
		except:
			if len(str(sys.exc_info()[1])) > 0:
				print(sys.exc_info()[1])
				return False
	dirname = os.path.dirname(input + os.sep)
	srrfile = os.path.join(srrdir, dirname + '.srr')

	if not os.path.isfile(srrfile):
		if not srrdb(dirname, srrdir):
			return False

		if srrdir != os.getcwd():
			try:
				shutil.copy(srrfile, os.getcwd())
			except:
				if len(str(sys.exc_info()[1])) > 0:
					print(sys.exc_info()[1])
					return False

	srrfile = os.path.join(os.getcwd(), dirname + '.srr')

	srr = SRR(filename=srrfile, binary=args['srr_bin'])
	if srr == False:
		return False
	srrlist = srr.list()

	rarlist = []
	for f in os.listdir(os.getcwd()):
		if re.search(r'\.(rar|[a-z]\d{2}|\d{3})$', f, re.IGNORECASE) is not None:
			rarlist.append(f)

	rar = None
	if os.path.isfile(os.path.join(os.getcwd(), srrlist[1][0].split('/')[-1])):
		rar = srrlist[1][0].split('/')[-1]
	elif len(rarlist) > 0:
		rar = rarlist[0]

	if args['sample_only'] == False and rar is not None:
		print('%r found, rars exist.' % (rar))
		if srr.extract() == False:
			return False

		cfv = CFV(binary=args['cfv_bin'])
		if cfv.verify() == True and args['force'] == False:
			return True

		if sorted(srrlist)[0] == sorted(rarlist)[0] and args['force'] == False:
			return True

		for f in set(srrlist[2] + rarlist):
			if re.search(r'\.((part0?0?1\.)?rar|001)$', f, re.IGNORECASE) is not None:
				unrar = UNRAR(filename=f.split('/')[-1], binary=args['unrar_bin'])
				if unrar.unrar() == False:
					return False

		for f in set(srrlist[2] + rarlist):
			try:
				os.unlink(os.path.join(os.getcwd(), f.split('/')[-1]))
			except:
				if len(str(sys.exc_info()[1])) > 0:
					print(sys.exc_info()[1])
					return False
	
	if args['sample_only'] == False:
		nf = 0
		for f in srrlist[3]:
			if not os.path.isfile(os.path.join(os.getcwd(), f)):
				print('Input file: %r not found.' % (f))
				nf = (nf+1)
	
	if args['sample_only'] == False and nf > 0:
		return False

	if args['sample_only'] == False:
		if srr.reconstruct() == False:
			return False

	if os.path.isdir(os.path.join(os.getcwd(), 'Subs')):
		for f in os.listdir():
			if re.search(r'[._-](vob)?sub(title)?s?[._-].*\.(r(ar|\d+)|srt|idx|sub)$', f, re.IGNORECASE) is not None:
				try:
					shutil.move(f, os.path.join(os.getcwd(), 'Subs', os.path.basename(f)))
				except:
					if len(str(sys.exc_info()[1])) > 0:
						print(sys.exc_info()[1])
						return False

	for f in os.listdir():
		if f not in srrlist[1] and f != os.path.basename(srrfile) and os.path.isfile(f):
			try:
				os.unlink(f)
			except:
				if len(str(sys.exc_info()[1])) > 0:
					print(sys.exc_info()[1])
					return False

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

	if srrdir != os.getcwd():
		try:
			os.unlink(srrfile)
		except:
			if len(str(sys.exc_info()[1])) > 0:
				print(sys.exc_info()[1])
				return False

	if args['sample_only'] == False:
		cfv = CFV(binary=args['cfv_bin'])
		if cfv.verify() == False:
			return False

if __name__ == '__main__':
	if main() != False:
		sys.exit(0)
	else:
		sys.exit(1)