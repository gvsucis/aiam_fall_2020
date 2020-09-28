import scrapy


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
        f = open('/home/westoand/capstone/aiam/aiam/spiders/member_params.txt', 'r')
        while True:
            line = f.readline()
            if not line:
                break
            self.company = line
            line = f.readline()
            if not line:
                break
            self.baseURL = line.strip()
            line = f.readline()
            if not line:
                break
            self.careersURL = line
            line = f.readline()
            if not line:
                break
            self.jobsListX = line
            line = f.readline()
            if not line:
                break
            self.jobX = line
            line = f.readline()
            if not line:
                break
            self.locationX = line
            line = f.readline()
            if not line:
                break
            self.jobURLX = line
            line = f.readline()
            if not line:
                break
            self.jobURLAttr = line
            yield scrapy.Request(url=self.careersURL, callback=self.parse)
            f.readline() #flush \n delimiter between scrape entries


    def parse(self, response):
        for jobs in response.xpath(self.jobsListX):
            yield {
                'job': jobs.xpath(self.jobX).get(),
                'location': jobs.xpath(self.locationX).get(),
                'jobURL': self.baseURL + jobs.xpath(self.jobURLX).attrib[self.jobURLAttr],
            }
