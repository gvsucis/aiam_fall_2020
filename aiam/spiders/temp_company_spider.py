import scrapy
import json
from os import name
# from pyvirtualdisplay import Display
from aiam.Models import getTempCompany, TemporaryCompanyDB
from aiam.spiders.general_spider import Spider_General
from aiam.env import *


class Temp_Company_Spider(Spider_General):
    name = "temp"

    # NO PIPELINES
    custom_settings = {
        'ITEM_PIPELINES': {

        }
    }

    def __init__(self, company):
        q = getTempCompany(company)
        if q is not None:
            self.member = q.serialize()
        else:
            self.member = {}

        with open("/var/www/html/output", "w") as f:
            f.write(company + "\n")

        super().__init__()

    def start_requests(self):
        if "company" not in self.member:
            ### TODO-Log error
            yield self.member

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
        print("=" * 16 + '\n' + self.member["careersURL"] + "\n" + "=" * 16)
        if "nextPageX" not in member:
            self.member["nextPageX"] = ''
        if "useDriver" not in member:
            self.member["useDriver"] = True
        if "defaultLocation" not in member:
            self.member["defaultLocation"] = 'Local'
        yield scrapy.Request(url=self.member['careersURL'], callback=self.parse)

    def parse(self, response):
        with open("/var/www/html/output", "a") as f:
            f.write("Inside of parse!\n")
        profile = self.member
        data = {}

        self.write_profile(profile)
        driver = profile["driver"]
        company = profile["company"]
        useDriver = profile["useDriver"]
        locationX = profile["locationX"]
        defaultLocation = profile["defaultLocation"]
        jobX = profile["jobX"]
        nextPageX = profile["nextPageX"]
        careersURL = profile["careersURL"]

        f = open('results/' + company + "-jobs.txt", "w")
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
                    except:
                        result_location = location

                    data[jobNum] = {"job": result, "location": result_location, "jobURL": "", "company": company}
                    jobNum += 1
                    f.write(result + ' - ' + result_location + '\n')

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
            f = open('results/' + company + "-jobs.txt", "w")
            # location provided
            if len(locationX) > 0:
                locations = response.xpath(locationX + "/text()")
            l = self.balance_lists(jobs, locationlist=locations, defaultlocation=defaultLocation)
            for job, location, link in l:
                result = self.cleanup(job.get())
                # calling validate locations
                result_location = location
                try:
                    result_location = self.validate_location(self.cleanup(location.text))
                except:
                    result_location = location
                data[jobNum] = {"job": result, "location": result_location, "jobURL": careersURL, "company": company}
                jobNum += 1
                f.write(result + '--' + result_location + '\n')
            yield data

        driver.quit()

        f.close()

        with open("/var/www/html/output", "a") as f2:
            f2.write("END OF PARSE :D\n")
