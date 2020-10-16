from flask import Flask, render_template, request
from subprocess import Popen, PIPE
from os import chdir, listdir
from json import load, dump

app = Flask(__name__)

# function to add to JSON 
def write_json( data, filename ): 
	with open(filename,'w') as f: 
		dump(data, f, indent=4) 
      
@app.route('/process', methods = ['POST'])
def process():
	data = request.form
	data = data.to_dict()
	company_name = data.pop( 'company' )
	print(data)
	print(company_name)

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
	return 'success'

@app.route('/run_scrapes', methods = ['POST'])
def run_scrapes():
	print( request.form );
	return 'success'

@app.route('/scrape_profiles')
def scrape_profiles():
	scrape_profile_names = []
	for scrape_profile in listdir('../profiles'):
		try:
				scrape_profile_names.append( scrape_profile.strip('-profile.txt') )
		except:
			continue
	return {'data':scrape_profile_names}

@app.route('/')
def hello_world():
	return render_template('interface.html', scrape_profile_api='http://0.0.0.0:9001/scrape_profiles', profiles=['a','b','c'])

if __name__ == "__main__":
	app.run( '0.0.0.0', 9001 )