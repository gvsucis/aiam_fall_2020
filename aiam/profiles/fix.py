import os
import json

with open( 'Cooling Tech Group-profile.json') as f:
	print( json.loads( json.load(f) )['company'] )

exit(0)

for x in os.listdir('./'):
	data = ''
	if 'json' in x:
		with open(x,'r') as f:
			data = f.read()
		with open(x,'w') as f:
			json.dump( data, f, indent=4 )