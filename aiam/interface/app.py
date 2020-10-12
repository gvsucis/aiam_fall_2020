from flask import Flask, render_template, request
from subprocess import Popen, PIPE
from os import chdir
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


@app.route('/')
def hello_world():
    return render_template('interface.html')

if __name__ == "__main__":
	app.run()
	#app.run( '0.0.0.0', 8080 )