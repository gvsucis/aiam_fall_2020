import scrapy
import json
from selenium import webdriver

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

    def write_profile(self):
        with open('profiles/' + self.company + '-profile.json', 'w') as profilef:
            profile = {}
            for key in self.__dict__:
                if key == 'driver':
                    continue
                else:
                    profile[ key ] = self.__dict__[key]
            profilef.write( json.dump( profile ) )

    def start_requests(self):
        # parse json file into dictionary
        with open( PARAM_FILE, 'r' ) as f:
            members = json.load( f )[ 'members' ]

        for member in members:
            # populate self variables from the current member subdictionary
            self.__dict__ = members[member]
            self.company = member
            self.driver = webdriver.Chrome(executable_path="chromedriver.exe")
            # supply scrapy with the data
            yield scrapy.Request( url=self.careersURL, callback=self.parse )

    def parse(self, response):
        # formatting like this to work seamlessly with firebase
        data = { self.company: {} }

        self.write_profile()

        #self.driver.get( response.url )
        #self.driver.implicitly_wait(5)

        #jobs = self.driver.find_elements_by_xpath( self.jobX )
        jobs = response.xpath(self.jobX + "/text()")
        f = open('results/' + self.company + "-jobs.txt", "w")
        # location provided
        if len(self.locationX) > 0:
            
            locations = self.driver.find_elements_by_xpath( self.locationX )

            for job, location in zip(jobs,locations):
                f.write( job.text + ' - ' + location.text + '\n' )
        # no locations provided, only jobs
        else:
            
            for job in jobs:              
                f.write( job.get() + ' -- ' + 'Local' + '\n' )

        f.close()
        #self.driver.close()

        #jobs = response.xpath(self.jobX+'/text()')

        #loc = response.xpath(self.jobX)

        #urls = ""
        #if jobURLAttr != "N/A":
        #    urls = response.xpath(self.jobURLX).attrib[self.jobURLAttr],

        '''
        for job, location,  in ( response.xpath(self.jobsListX), res:
        # each job to yield fits this dict pattern
        new_job_title = xpath(self.jobX).get()
        '''
        '''
        for job in jobs:
            print(job)
            new_job_info = {
                'location': 'Ann Arbor', #jobs.xpath(self.locationX).get(),
                'jobURL': self.jobURLX #self.baseURL + jobs.xpath(self.jobURLX).attrib[self.jobURLAttr]
            }

            # add the job to the current list of company jobs
            data[ self.company ][job.get()] = new_job_info
        '''
        yield data
