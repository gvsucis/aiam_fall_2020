from flask import Flask, render_template, request, jsonify
from subprocess import Popen, PIPE
from os import chdir, listdir
from json import load, dump, loads

MEMBER_PARAMS_FILENAME = '../member_params.json'
PROFILES_PATH = '../profiles/'

PORT=9001
GET_PROFILE_API = 'http://0.0.0.0:{}/scrape_profile/'.format(PORT)
SCRAPE_API = 'http://0.0.0.0:{}/scrape_profiles'.format(PORT)

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
	chdir('../')
	p = Popen( ['scrapy', 'crawl', 'general' ] )
	p.wait()
	chdir('interface')


def get_profiles():
	return listdir( PROFILES_PATH )


def get_profile_data ( name ):
	with open('{}/{}-profile.json'.format( PROFILES_PATH, name ), 'r' ) as f:
		profile_data = loads( f.read() )
		return profile_data


''' ROUTES '''
      
@app.route('/process', methods = ['POST'])
def process():
	data = request.form
	data = data.to_dict()
	company_name = data.pop( 'company' )
	print(data)
	print(company_name)
	if 'useDriver' not in data:
		data['useDriver'] = 'off'

	chdir('../')
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
	chdir('interface')
	return 'success, new profile created'


@app.route('/run_scrapes', methods = ['POST'])
def run_scrapes():
	data = request.form
	data = data.to_dict()

	clear_memberparams()

	params = {"members":{}}

	for member_profile_file in data:
		profile = get_profile( PROFILES_PATHNAME + member_profile_file )
		if type(profile) == dict:
			company_name = profile.pop('company') 
			params['members'][company_name] = profile
			print(params)
			#load_profiles_into_memberparams( profile )

	with open( MEMBER_PARAMS_FILENAME ) as j: 
		write_json( params, MEMBER_PARAMS_FILENAME )

	scrape()
	return 'success'


@app.route('/scrape_profiles', methods = ['GET', 'DELETE'])
def scrape_profiles():

	if request.method == 'DELETE':
		print( request.data )

	scrape_profile_names = []
	for scrape_profile in listdir('../profiles'):
		try:
				scrape_profile_names.append( scrape_profile.strip('-profile.txt') )
		except:
			continue
	return {'data':scrape_profile_names}


''' Get a single profile's infomation '''
@app.route ( '/scrape_profile/<name>' )
def scrape_profile ( name ):	
	profile = get_profile_data( name )
	print(profile)
	return profile


@app.route('/')
def index():
	return render_template( 'interface.html', get_profile_api=GET_PROFILE_API, scrape_api=SCRAPE_API )

if __name__ == "__main__":
	app.run( '0.0.0.0', PORT )