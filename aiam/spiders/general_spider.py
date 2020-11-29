import scrapy
import json
from aiam.Models import AddCompany
import re
from selenium import webdriver
from os import name
from urllib.parse import quote
#from pyvirtualdisplay import Display

PARAM_FILE = 'member_params.json'

class Spider_General(scrapy.Spider):
    name = "general"

    custom_settings = {

        'ITEM_PIPELINES' : {
            # data cleaning TBD
            'aiam.pipelines.AiamPipeline': 300,
            # create tables if necessary
            'aiam.pipelines.SetupDBTablesPipeline': 400,
            #add jobs if necessary
            'aiam.pipelines.ScrapySpiderPipeline': 600,
            # FIXME update tables
        }
    }


    def __init__(self):
        self.members = {}
        super().__init__()

    def create_chrome_instance( self, executable_path ):
        # selenium on a vps needs a display port to run google chrome
        #display = Display( visible=0, size=(800,600) )
        #display.start()
        # set up webdriver options, then return chrome instance
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-extensions')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        return webdriver.Chrome( executable_path=executable_path, chrome_options=options ) 


    def cleanup(self, text):
        text = text.strip().strip("\n \t").replace("  ", "").replace("\n", "")
        return text

    def urlencode ( self, url ):
        ret = quote( url ).replace("%3A",":")
        return ret

    def write_profile(self, scrapeProfile):
        with open('profiles/' + scrapeProfile["company"] + '-profile.json', 'w') as profilef:
            profile = {}
            for key in scrapeProfile:
                if key == 'driver':
                    continue
                else:
                    profile[ key ] = scrapeProfile[ key ]
            json.dump( profile, profilef )


    def start_requests(self):

        target_chrome_driver = '/var/www/job_collector/virtualenv/src/aiam_fall_2020/aiam/ChromeDrivers/linux_chromedriver'
        if name == 'nt':
            target_chrome_driver = './ChromeDrivers/chromedriver.exe'

        #print("HIT")

        # parse json file into dictionary
        with open( PARAM_FILE, 'r' ) as f:
            members = json.load( f )[ 'members' ]

        for member in members:
            # populate self variables from the current member subdictionary
            self.members[member] = members[member]
            # a few of these don't come with the web form, manually add those in
            self.members[member]["company"] = member
            self.members[member]["driver"] = self.create_chrome_instance( target_chrome_driver )
            print("="*16+'\n'+self.members[member]["careersURL"]+"\n"+"="*16)            
            if "nextPageX" not in members[member]:
                self.members[member]["nextPageX"] = ''
            if "useDriver" not in members[member]:
                self.members[member]["useDriver"] = "on"
            # supply scrapy with the data
            AddCompany(self.members[member])
            yield scrapy.Request( url=self.members[member]["careersURL"], callback=self.parse, meta={ "company": member } )


    def parse(self, response):
        profile = self.members[ response.meta["company"] ]
        data = {}

        self.write_profile(profile)
        driver = profile["driver"]
        company = profile["company"]
        useDriver = profile["useDriver"]
        locationX = profile["locationX"]
        jobX = profile["jobX"]
        nextPageX = profile["nextPageX"]
        careersURL = profile["careersURL"]

        print("="*16+'\n'+careersURL+"\n"+"="*16)

        f = open('results/' + company + "-jobs.txt", "w")
        #print(company + "-jobs.txt")
        jobNum = 0
        # scrape with selenium
        if useDriver == 'on':

            #print("\n\n\nHIT!\n\n\n")

            driver.get(careersURL )
            driver.implicitly_wait( 5 ) # seconds

            working = True
            while working:
                jobs = driver.find_elements_by_xpath(jobX)
                # location provided
                if len(locationX) > 0:
                    locations = driver.find_elements_by_xpath(locationX )
                    for job, location in zip(jobs,locations):
                        result = self.cleanup(job.text)
                        result_location = self.cleanup(location.text)
                        data[jobNum] = {"job": result, "location":result_location, "jobURL":"", "company":company}
                        jobNum += 1
                        f.write(result + ' - ' + result_location + '\n' )
                # no locations provided, only jobs
                else:
                    for job in jobs:
                        result = self.cleanup(job.text)
                        data[jobNum] = {"job": result, "location": "Local", "jobURL": "", "company": company}
                        jobNum += 1
                        f.write(result + ' -- ' + 'Local' + '\n' )

                # Scrape additional pages if provided
                if (len(nextPageX)) > 0:
                    next_page = driver.find_elements_by_xpath(nextPageX)
                    if not next_page[0].is_enabled():
                        break
                    else:
                        driver.execute_script("arguments[0].click();", next_page[0])
                        driver.implicitly_wait(5)
                else:
                    working = False
            yield data


        # scrape without selenium
        else:
            jobs = response.xpath(jobX + "/text()")
            f = open('results/' + company + "-jobs.txt", "w")
            # location provided
            if len(locationX) > 0:
                locations = response.xpath(locationX + "/text()" )

                for job, location in zip(jobs,locations):
                    result = self.cleanup(job.get())
                    result_location = self.cleanup(location.get())
                    data[jobNum] = {"job": result, "location": result_location, "jobURL": "", "company": company}
                    jobNum += 1
                    f.write(result + ' - ' + result_location + '\n' )
            # no locations provided, only jobs
            else:
                for job in jobs:
                    result = self.cleanup(job.get())
                    data[jobNum] = {"job": result, "location": "Local", "jobURL": "", "company": company}
                    jobNum += 1
                    f.write(result + ' -- ' + 'Local' + '\n' )
            yield data
        
        driver.quit()

        f.close()

