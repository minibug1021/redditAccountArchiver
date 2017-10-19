import os,sys
from shutil import copyfile


if sys.argv[1] == '-u':
    os.system('update.py')

if sys.argv[1] == '-a':
    os.system('a.py {}'.format(sys.argv[2]))

if sys.argv[1] == '-t':
		if sys.argv[3] == '-n':
			os.mkdir(sys.argv[2])
			copyfile('a.py','{}/a.py'.format(sys.argv[2]))
			copyfile('post_grabber.py','{}/post_grabber.py'.format(sys.argv[2]))
			os.chdir(sys.argv[2])
			os.system('post_grabber.py {}'.format(sys.argv[2]))
		else:
			os.system('post_grabber.py {}'.format(sys.argv[2]))
