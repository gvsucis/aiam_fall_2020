import scrapy
import json
from os import name
# from pyvirtualdisplay import Display
from aiam.Models import get_all_companies
from aiam.spiders.general_spider import Spider_General
from aiam.env import *


class Cron_Spider(Spider_General):
    name = "cron"

    # NO PIPELINES
    custom_settings = {
        'ITEM_PIPELINES': {
            # data cleaning TBD
            'aiam.pipelines.AiamPipeline': 300,
            'aiam.pipelines.DropJobTablePipeline': 350,
            # create tables if necessary
            'aiam.pipelines.SetupDBTablesPipeline': 400,
            # add jobs if necessary
            'aiam.pipelines.ScrapySpiderPipeline': 600,
            # FIXME update tables
        }
    }

    def __init__(self):
        super().__init__()

    def start_requests(self):
        self.members = get_all_companies()
        
        ##target_chrome_driver = '/var/www/job_collector/virtualenv/src/aiam_fall_2020/aiam/ChromeDrivers/linux_chromedriver'
        target_chrome_driver = './ChromeDrivers/linux_chromedriver'
        if name == 'nt':
            target_chrome_driver = './ChromeDrivers/chromedriver.exe'

        with open(MICHIGAN_LOCATIONS_FILE, 'r') as f:
            self.valid_locations = json.load(f)

        with open(STATES_FILE, 'r') as f:
            self.valid_states = json.load(f)

            # a few of these don't come with the web form, manually add those in
        for member in self.members:
            self.members[member]["driver"] = self.create_chrome_instance(target_chrome_driver)
            yield scrapy.Request(url=self.members[member]['careersURL'], callback=self.parse, meta={"company": member})

    def parse(self, response):
        with open("/var/www/html/output", "a") as f:
            f.write("Inside of parse!\n")
        profile = self.members[response.meta["company"]]
        data = {}

        driver = profile["driver"]
        company = profile["company"]
        useDriver = profile["useDriver"]
        locationX = profile["locationX"]
        defaultLocation = profile["defaultLocation"]
        jobX = profile["jobX"]
        nextPageX = profile["nextPageX"]
        careersURL = profile["careersURL"]

        # print(company + "-jobs.txt")
        jobNum = 0
        # scrape with selenium
        if useDriver == True:

            # print("\n\n\nHIT!\n\n\n")

            driver.get(careersURL)
            driver.implicitly_wait(5)  # seconds

            working = True
            while working:
                jobs = driver.find_elements_by_xpath(jobX)

                locations = None
                if len(locationX) > 0:
                    locations = driver.find_elements_by_xpath(locationX)
                l = self.balance_lists(jobs, locationlist=locations, defaultlocation=defaultLocation)

                for job, location, link in l:
                    result = self.cleanup(job.text)

                    print("THIS IS THE RESULT")
                    print(result)
                    print("This is ENNNNDDDDD of result")
                    # calls the validate function
                    result_location = location
                    try:
                        result_location = self.validate_location(self.cleanup(location.text))
                        if result_location is None:
                            continue
                    except:
                        result_location = location

                    data[jobNum] = {"job": result, "location": result_location, "jobURL": careersURL,
                                    "company": company}
                    jobNum += 1

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

            with open("/var/www/html/output", "a") as f3:
                f3.write("Yielding data...\n")
            yield data


        # scrape without selenium
        else:
            jobs = response.xpath(jobX + "/text()")
            # location provided
            locations = None
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

        with open("/var/www/html/output", "a") as f2:
            f2.write("END OF PARSE :D\n")
