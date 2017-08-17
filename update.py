import os
to_update = []

for item in os.listdir():
	if '.db' in item:
		to_update.append(item[:-3])
to_update.append('')
f = open(r'PATH TO ARCHIVER.PY', 'r+')
f.truncate()

for i in range(len(to_update)):
    if to_update[i] not in f.read():
        f.write('archiver.py {}\n'.format(to_update[i]))
    else:
        continue

os.system('update.bat')
