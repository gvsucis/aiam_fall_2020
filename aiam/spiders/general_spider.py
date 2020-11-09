import scrapy
import json
import re
from selenium import webdriver
from os import name
from urllib.parse import quote

from aiam.Models import addCompany

PARAM_FILE = 'member_params.json'

class Spider_General(scrapy.Spider):
    name = "general"

    def __init__(self):
        self.members = {}
        super().__init__()


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

        target_chrome_driver = './ChromeDrivers/linux_chromedriver'
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
            self.members[member]["driver"] = webdriver.Chrome(executable_path=target_chrome_driver) # needs instantiation
            if "nextPageX" not in members[member]:
                self.members[member]["nextPageX"] = ''
            if "useDriver" not in members[member]:
                self.members[member]["useDriver"] = "on"
            # supply scrapy with the data
            addCompany(self.members[member])
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
                        if str(result_location) == "":
                            result_location = "Local"
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
        f.close()

