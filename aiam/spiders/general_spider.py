import scrapy
import json
from aiam.Models import AddCompany
from selenium import webdriver
from os import name

PARAM_FILE = 'member_params.json'

class Spider_General(scrapy.Spider):
    name = "general"

    def __init__(self):
        super().__init__()
        self.company = ''
        self.baseURL = ''
        self.careersURL = ''
        self.jobsListX = ''
        self.jobX = ''
        self.locationX = ''
        self.jobURLX = ''
        self.jobURLAttr = ''
        self.driver = None
        self.useDriver = 'on'


    def write_profile(self):
        with open('profiles/' + self.company + '-profile.json', 'w') as profilef:
            profile = {}
            for key in self.__dict__:
                if key == 'driver':
                    continue
                else:
                    profile[ key ] = self.__dict__[key]
            json.dump( profile, profilef )


    def start_requests(self):

        target_chrome_driver = './ChromeDrivers/linux_chromedriver'
        if name == 'nt':
            target_chrome_driver = './ChromeDrivers/chromedriver.exe'

        print("HIT")

        # parse json file into dictionary
        with open( PARAM_FILE, 'r' ) as f:
            members = json.load( f )[ 'members' ]

        for member in members:
            self.company = member
            #self.baseURL = members[member]['baseURL']
            #self.careersURL = members[member]['careersURL']

            # populate self variables from the current member subdictionary
            self.__dict__ = members[member]
            #self.company = member
            self.driver = webdriver.Chrome(executable_path=target_chrome_driver)
            AddCompany(self)
            # supply scrapy with the data
            yield scrapy.Request( url=self.careersURL, callback=self.parse )


    def parse(self, response):
        data = { self.company: {} }
        self.write_profile()

        f = open('results/' + self.company + "-jobs.txt", "w")

        # scrape with selenium
        if self.useDriver == 'on':

            #print("\n\n\nHIT!\n\n\n")

            self.driver.get( self.careersURL )
            self.driver.implicitly_wait( 5 ) # seconds

            jobs = self.driver.find_elements_by_xpath( self.jobX )
            # location provided
            if len(self.locationX) > 0:
                locations = self.driver.find_elements_by_xpath( self.locationX )
                for job, location in zip(jobs,locations):
                    f.write( job.text + ' - ' + location.text + '\n' )
            # no locations provided, only jobs
            else:
                for job in jobs:
                    f.write( job.text + ' -- ' + 'Local' + '\n' )

        # scrape without selenium
        else:
            jobs = response.xpath(self.jobX + "/text()")
            f = open('results/' + self.company + "-jobs.txt", "w")
            # location provided
            if len(self.locationX) > 0:
                locations = response.xpath( self.locationX + "/text()" )
                for job, location in zip(jobs,locations):
                    f.write( job.get() + ' - ' + location.get() + '\n' )
            # no locations provided, only jobs
            else:
                for job in jobs:
                    f.write( job.get() + ' -- ' + 'Local' + '\n' )

        f.close()

        yield data
