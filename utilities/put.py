import os, sys
import traceback

from optparse import OptionParser
Parser = OptionParser(usage="%prog [options] output\nType \"%prog -h\" for help", version="%prog 1.0")
Parser.add_option('-s', '--source',  dest='source',  type  ='string',     default='',    help='Source')
Parser.add_option('-d', '--dest',    dest='dest',    type  ='string',     default='',    help='Destination')
Parser.add_option('-n', '--name',    dest='name',    type  ='string',     default='',    help='Name')
Parser.add_option('-r', '--rsync',   dest='rsync',   action='store_true', default=False, help='Use rsync')
Parser.add_option('-V', '--verbose', dest='verbose', action='store_true', default=False, help='Verbose mode')
Parser.add_option('-D', '--debug',   dest='debug',   action='store_true', default=False, help='Debug mode')
(Options, args) = Parser.parse_args()
if Options.debug: Options.verbose = True

os.umask(0000)

def errorExit( i_msg = None):
	if i_msg:	
		print('Error: ' + i_msg)
	if sys.exc_info()[1]:
		traceback.print_exc(file=sys.stdout);
	sys.exit(1)

def makeDir( i_folder):
	if( len( i_folder) == 0 ): return
	if os.path.isdir( i_folder ): return
	print('Creating folder:\n' + i_folder )
	if Options.debug: return
	try:
		os.makedirs( i_folder)
	except:
		errorExit('Can`t create folder "%s"' % i_folder )


if Options.source == '': errorExit('Source is not specified')
if not os.path.exists( Options.source ): errorExit('Source does not exist:\n' + Options.source )

if Options.dest == '': errorExit('Destination is not specified')
if not os.path.isdir( Options.dest ): errorExit('Destination folder does not exist:\n' + Options.dest )

if Options.name == '': errorExit('Name is not specified')
Result = os.path.join( Options.dest, Options.name)

if Options.verbose:
	print('Source:      ' + Options.source)
	print('Destination: ' + Options.dest)
	print('Name:        ' + Options.name)
	print('Result:      ' + Result)


files = []
if os.path.isdir( Options.source):
	makeDir( Result)
	allfiles = os.listdir( Options.source)
	for afile in allfiles:
		if afile[0] == '.': continue
		afile = os.path.join( Options.source, afile)
		if os.path.isfile( afile): files.append( afile)
		elif os.path.isdir( afile): files.append( afile)
else:
	files = [Options.source]

files.sort()

Copy_File = 'cp -p "%s" "%s"'
Copy_Dir  = 'cp -rp "%s" "%s"'
if sys.platform.find('win') == 0:
	Copy_File = 'COPY "%s" "%s"'
	Copy_Dir  = 'XCOPY "%s" "%s" /YSIR'
if Options.rsync:
	Copy_File = 'rsync -avP "%s" "%s"'
	Copy_Dir  = 'rsync -avP "%s" "%s"'

i = 0
for afile in files:
	if Options.verbose:
		print( os.path.basename( afile))

	dest = Result
	if not Options.rsync and os.path.isdir( Options.source):
		dest = os.path.join( Result, os.path.basename( afile))

	Copy = Copy_File
	if os.path.isdir( afile):
		Copy = Copy_Dir

	cmd = Copy % ( afile, dest)

	print( cmd)
	sys.stdout.flush()

	if not Options.debug:
		status = os.system( cmd)
		if status != 0:
			sys.exit( status)

	if not Options.rsync:
		print('PROGRESS: %d%%' % int( 100.0 * (i + 1.0) / len( files)))

	sys.stdout.flush()

	i += 1

