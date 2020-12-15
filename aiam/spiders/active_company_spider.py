import scrapy
import json
from os import name, remove
# from pyvirtualdisplay import Display
from aiam.Models import deleteJobsForCompany, getActiveCompany, CompanyDB
from aiam.spiders.general_spider import Spider_General
from aiam.env import *
import time


class Active_Company_Spider(Spider_General):
    name = "active"

    # NO PIPELINES
    custom_settings = {
        'ITEM_PIPELINES': {
            'aiam.pipelines.SetupDBTablesPipeline': 400,
            # add jobs if necessary
            'aiam.pipelines.ScrapySpiderPipeline': 600
        }
    }

    def __init__(self, company):
        q = getActiveCompany( company )
        if q is not None:
            self.member = q.serialize()
        else:
            self.member = {}
        
        # remove results obtained during profile creation by the company
        try:
            remove( './results/{}-jobs.txt'.format( company ) ) 
        except:
            print("Already deleted!\n")

        super().__init__()

    def start_requests(self):
        if "company" not in self.member:
            ### TODO-Log error
            yield self.member
        else:
            deleteJobsForCompany( self.member[ 'company' ] )

        ##target_chrome_driver = '/var/www/job_collector/virtualenv/src/aiam_fall_2020/aiam/ChromeDrivers/linux_chromedriver'
        target_chrome_driver = './ChromeDrivers/linux_chromedriver'
        if name == 'nt':
            target_chrome_driver = './ChromeDrivers/chromedriver.exe'
        member = self.member

        with open(MICHIGAN_LOCATIONS_FILE, 'r') as f:
            self.valid_locations = json.load(f)

        with open(STATES_FILE, 'r') as f:
            self.valid_states = json.load(f)

        # a few of these don't come with the web form, manually add those in
        self.member["driver"] = self.create_chrome_instance(target_chrome_driver)
        if "nextPageX" not in member:
            self.member["nextPageX"] = ''
        if "useDriver" not in member:
            self.member["useDriver"] = True
        if "defaultLocation" not in member:
            self.member["defaultLocation"] = 'Local'
        yield scrapy.Request(url=self.member['careersURL'], callback=self.parse)

    def parse(self, response):
        profile = self.member
        data = {}

        driver = profile["driver"]
        company = profile["company"]
        print("\n\n\n======\n{}\n======\n\n\n".format( company ) )
        useDriver = profile["useDriver"]
        locationX = profile["locationX"]
        defaultLocation = profile["defaultLocation"]
        jobX = profile["jobX"]
        nextPageX = profile["nextPageX"]
        careersURL = profile["careersURL"]

        jobNum = 0
        # scrape with selenium
        if useDriver == True:
            old_jobs = []
            driver.get(careersURL)
            driver.implicitly_wait(5)  # seconds

            working = True
            while working:
                new_jobs = []
                jobsAdded = 0
                # TODO: Change this to optional?? Would require SQL migration
                time.sleep(1)
                jobs = driver.find_elements_by_xpath(jobX)

                locations = None
                if len(locationX) > 0:
                    locations = driver.find_elements_by_xpath(locationX)
                l = self.balance_lists(jobs, locationlist=locations, defaultlocation=defaultLocation)

                for job, location, link in l:
                    result = self.cleanup(job.text)
                    new_jobs.append(result)
                    # calls the validate function
                    result_location = location
                    try:
                        result_location = self.validate_location(self.cleanup(location.text))
                        if result_location is None:
                            continue

                    except:
                        result_location = location

                    data[jobNum] = {"job": result, "location": result_location, "jobURL": careersURL, "company": company}
                    jobNum += 1
                    jobsAdded += 1

                # Scrape additional pages if provided
                if (len(nextPageX)) > 0:
                    next_page = driver.find_elements_by_xpath(nextPageX)
                    if sorted(new_jobs) == sorted(old_jobs): 
                        data = self.removeDuplicates(data, jobsAdded)
                        break
                    else:
                        old_jobs = new_jobs
                        driver.execute_script("arguments[0].click();", next_page[0])
                        driver.implicitly_wait(5)
                else:
                    working = False

            yield data


        # scrape without selenium
        else:
            jobs = response.xpath(jobX + "/text()")
            # location provided
            if len(locationX) > 0:
                locations = response.xpath(locationX + "/text()")
            l = self.balance_lists(jobs, locationlist=locations, defaultlocation=defaultLocation)
            for job, location, link in l:
                result = self.cleanup(job.get())
                # calling validate locations
                result_location = location
                try:
                    result_location = self.validate_location(self.cleanup(location.get()))
                    if result_location is None:
                        continue
                except:
                    result_location = location
                data[jobNum] = {"job": result, "location": result_location, "jobURL": careersURL, "company": company}
                jobNum += 1
            yield data

        driver.quit()
