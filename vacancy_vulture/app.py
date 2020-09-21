from flask import Flask, render_template
from subprocess import Popen, PIPE
from json import dumps, loads

app = Flask(__name__)
companies = [ 
		'httpthermoanalytics',
		'httpdornerworks',
		'aerodynamicadvisory'
	]

def get_jobs():
	ret = ''
	# url of data to get
	db = 'https://aiam-f9a6da.firebaseio.com/jobs.json'
	# Get data with curl //NOTE: Maybe should use an actual legit API
	p = Popen( ['/usr/bin/curl', db], stdout=PIPE )
	ret = p.communicate()[0]; p.wait();
	return ret

def format_jobs( data ):
	data = u'{}'.format( data.decode() )
	return loads( data )

@app.route('/')
def hello_world():
    jobs = ''
    try:
    	jobs = format_jobs( get_jobs() )
    except Exception as e:
    	print(e)
    	jobs = 'Jobs could not be loaded!'

    return render_template( 'index.html', jobs=jobs )

if __name__ == "__main__":
    app.run( '0.0.0.0', 8080 )