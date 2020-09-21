from bs4 import BeautifulSoup as bs
from find_job_titles import Finder
from selenium import webdriver
import requests
from selenium.webdriver.common.by import By
import re
from subprocess import Popen, PIPE
from json import dumps

def post_jobs( company, jobs ):
    db = 'https://aiam-f9a6da.firebaseio.com/jobs/{}.json'.format(company)
    data = {}
    for i in range(len(jobs)):
        data[str(i)] = jobs[i]
    data = dumps( data, separators=(',', ':') )

    p = Popen( ['/usr/bin/curl', '-X', 'DELETE', db], stdout=PIPE )

    res = requests.post( db, data=data )
    p = Popen( ['/usr/bin/curl', '-X', 'POST', '-d', data, db], stdout=PIPE )
    p.wait()


def remove_html_tags( txt ):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', txt)


def visible_text( txt ):
    soup = bs( txt, 'lxml' )
    text = soup.get_text()
    return text.split('\n')


def read_robotstxt( url ):
    ret = None

    try:
        res = requests.get( url + '/robots.txt' )
        if res.status_code == 200:
            return visible_text( res.text )
    except:
        print( "Problem with {}".format( url ) )

    return ret

def is_relativepath( route, url ):
    if route[0] == '.':
        return url + route[1:]
    elif route[0] == '/':
        return url + route
    return url


def allhrefs( txt ):
    ret = []

    soup = bs( txt, 'lxml' )
    for a in soup.find_all('a'):
        ret.append( a.get( 'href' ) )

    return ret

def allatags( txt ):
    soup = bs( txt, 'lxml' )
    return soup.find_all('a')


def searchhrefs( hrefs, keyword, url='' ):
    ret = []
    for a in hrefs:
        try:
            if keyword in a:
                if a[0] == '/':
                    if url[-1] == '/':
                        a = url + a[1:]
                    else:
                        a = url + a
                elif a[0] == '.':
                    a = url + a[1:]
                ret += [ a ]
        except:
            continue
    return ret

def find_job_plaintext( txts ):
    finder = Finder()
    found_jobs = []
    #txts = visible_text( plaintext )

    for txt in txts:
        jobs = finder.findall( txt )

        if len( jobs ) > 0:
            found_jobs.append( txt )
    return found_jobs

def find_job_tags( tags ):
    finder = Finder()
    found_jobs = []

    for tag in tags:
        jobs = finder.findall( tag.text )
        if 'intern' in tag.text.lower():
            found_jobs.append( tag )
        elif len( jobs ) > 0:
            found_jobs.append( tag )
    return found_jobs


def search_iframes_for_jobs( d, keyword ):
    found = []; ret = [];

    iframes = d.find_elements_by_tag_name( 'iframe' )


    for iframe in iframes:
        src = iframe.get_attribute( 'src' )
        if 'career' in src or 'job' in src:
            txt = requests.get( src ).text
            found = find_job_tags( allatags( txt ) )

            if len( found ) == 0:
                for tag in [ 'h2', 'h3' ]:
                    found = searchbytags( txt, tag )

            break
    for f in found:
        ret.append( f.encode_contents().decode('utf-8') )
    return ret

def searchbytags( txt, tag ):
    finder = Finder()
    soup = bs( txt, 'lxml' )
    return find_job_tags(soup.find_all( tag ))


def spider_page( url, keywords ):
    pages = allhrefs( requests.get( url ).text )
    ret = []
    [ ret.extend( searchhrefs( pages, keyword, url ) ) for keyword in keywords ]
    return set( ret )


for target in ['https://www.thermoanalytics.com','https://www.dornerworks.com','https://aerodynamicadvisory.com']:
    print( "HARVESTING JOBS FOR {} ".format( target ) )
    keywords = [ 'career', 'job' ]
    possible_job_pages = spider_page( target, keywords )

    print( "INTERESTING PAGES FOUND #{}".format( len( possible_job_pages ) ) )

    driver = webdriver.Firefox()

    postings = []

    for page in possible_job_pages:
        driver.get( page )
        driver.implicitly_wait(1000)

        print( "\tDigging through iframes..." )
        postings = search_iframes_for_jobs( driver, 'career' )

        if len( postings ) == 0:
            print( "\t\t:( Nothing in iframes" )

            for tag in [ 'h2', 'h3' ]:
                print( "\tDigging through all {} html elements...".format( tag ) )

                postings = searchbytags( requests.get( page ).text, tag )
                if len( postings ) > 1:
                    temp = []
                    for job in postings:
                        temp += [ remove_html_tags( str( job ) ) ]
                    postings = temp
                    break
    print( '#{} Possible jobs found'.format( len( postings ) ) )

    driver.close()

    print( 'Updating found jobs to firebase...' )
    post_jobs( 'thermoanalytics', postings )
    print( 'Done updating!' )

print( '\tFinished!' )
