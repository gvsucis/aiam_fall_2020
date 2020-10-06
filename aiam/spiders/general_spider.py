import scrapy
import json

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

    def start_requests(self):
        # parse json file into dictionary
        with open( PARAM_FILE, 'r' ) as f:
            members = json.load( f )[ 'members' ]

        for member in members:
            # populate self variables from the current member subdictionary
            self.__dict__ = members[member]
            self.company = member
            print("ABCHFHHCHE{}".format(self.company))
            # supply scrapy with the data
            yield scrapy.Request( url=self.careersURL, callback=self.parse )

    def parse(self, response):
        # formatting like this to work seamlessly with firebase
        data = { self.company: {} }
        
        jobs = response.xpath( self.jobX )
        print(self.jobX)
        print(jobs)
        locations = response.xpath( self.locationX + '/text()')

        f = open(self.company + "-jobs.txt", "w")

        if len( self.locationX ) > 0:
            for job, location in zip(jobs, locations):
                f.write(job.get() + ' -- ' + location.get() + '\n' )
        else:
            print("\n\n\n\n\nXYZ!")
            for job in jobs:
                print("JOBHERE!:{}".format(job.get()))
                f.write(job.get() + ' -- ' + 'Local' + '\n' )

        f.close()

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
