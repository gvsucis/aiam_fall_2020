from flask import Flask, render_template, request
from subprocess import Popen, PIPE
from os import chdir, listdir
from json import load, dump, loads

MEMBER_PARAMS_FILENAME = 'member_params.json'
PROFILES_PATHNAME = 'profiles/'
SCRAPE_PROFILE_API = 'http://localhost:8000/scrape_profiles'


app = Flask(__name__)

# function to add to JSON 
def write_json( data, filename ): 
	with open(filename,'w') as f: 
		dump(data, f, indent=4) 


def get_profile( filename ):
	profile = {}
	with open( filename ) as p:
		try:
			profile = load( p )
			#profile = loads( profile )
		except:
			return 'err'
	return profile


def clear_memberparams():
	with open( MEMBER_PARAMS_FILENAME ) as f:
		params = load( f )
		params["members"] = {}
		temp = params["members"]
		write_json( params, MEMBER_PARAMS_FILENAME )

def scrape():
	#chdir('../')
	p = Popen( ['scrapy', 'crawl', 'general' ] )
	p.wait()
	#chdir('interface')

      
@app.route('/process', methods = ['POST'])
def process():
	data = request.form
	data = data.to_dict()
	company_name = data.pop( 'company' )
	if 'useDriver' not in data:
		data['useDriver'] = 'off'

	#chdir('../')
	fname = 'member_params.json'
	with open( fname ) as j: 
		params = load( j )
		#temp = params['members']
		params["members"] = {}
		temp = params["members"]
		temp[company_name] = data
		write_json( params, fname )
	p = Popen( ['scrapy', 'crawl', 'general' ] )
	p.wait()
	#chdir('interface')
	return 'success, new profile created'


@app.route('/run_scrapes', methods = ['POST'])
def run_scrapes():
	data = request.form
	data = data.to_dict()

	clear_memberparams()

	params = {"members":{}}
	#print(params)
	for member_profile_file in data:
		profile = get_profile( PROFILES_PATHNAME + member_profile_file )
		#print(type(profile))
		#print("HI")
		if type(profile) == dict:
			company_name = profile.pop('company') 
			params['members'][company_name] = profile
			print(params)
			#load_profiles_into_memberparams( profile )

	with open( MEMBER_PARAMS_FILENAME ) as j: 
		write_json( params, MEMBER_PARAMS_FILENAME )

	scrape()
	return 'success'


@app.route('/scrape_profiles')
def scrape_profiles():
	scrape_profile_names = []
	for scrape_profile in listdir(PROFILES_PATHNAME):
		try:
				scrape_profile_names.append( scrape_profile.strip('-profile.txt') )
		except:
			continue
	return {'data':scrape_profile_names}

@app.route('/')
def hello_world():
	return render_template('interface.html', scrape_profile_api=SCRAPE_PROFILE_API )

if __name__ == "__main__":
	app.run( 'localhost', 8000 )