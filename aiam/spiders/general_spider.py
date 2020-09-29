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
            self.company = member
            # populate self variables from the current member subdictionary
            self.__dict__ = members[member]
            # supply scrapy with the data
            yield scrapy.Request( url=self.careersURL, callback=self.parse )


    def parse(self, response):
        for jobs in response.xpath(self.jobsListX):
            yield {
                'job': jobs.xpath(self.jobX).get(),
                'location': jobs.xpath(self.locationX).get(),
                'jobURL': self.baseURL + jobs.xpath(self.jobURLX).attrib[self.jobURLAttr],
            }
