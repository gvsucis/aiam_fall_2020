import os
import json

for file in os.listdir():
	if 'json' in file:
		x = {}
		try:
			with open( file, 'r' ) as f:
                            x = json.load(f)
                            print(x['useDriver'])
                        #with open( file, 'w' ) as f:
			    #f.write( json.dumps(x) )
		except:
			continue

exit(0)

for x in os.listdir('./'):
	data = ''
	if 'json' in x:
		with open(x,'r') as f:
			data = f.read()
		with open(x,'w') as f:
			json.dump( data, f, indent=4 )
