import scrapy
import json
import re
from selenium import webdriver
from os import name
from urllib.parse import quote
# from pyvirtualdisplay import Display
from aiam.Models import addCompany
from aiam.spiders.general_spider import Spider_General
from aiam.env import *
import time


class Builder_General(Spider_General):
    name = "builder"

    # NO PIPELINES
    custom_settings = {
        'ITEM_PIPELINES': {

        }
    }

    def __init__(self, filename):
        self.member = {}

        with open(filename, 'r') as f:
            self.member = json.load(f)

        # with open('/var/www/job_collector/virtualenv/src/aiam_fall_2020/aiam/results/output', 'w') as t:
        #    t.write(filename)
        #    t.write(str(self.member))

        with open("/var/www/html/output", "w") as f:
            f.write(filename + "\n")

        super().__init__()

    def start_requests(self):
        with open("/var/www/html/output", "a") as f:
            f.write("HIT!\n")
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
            old_jobs = []
            # print("\n\n\nHIT!\n\n\n")

            driver.get(careersURL)
            driver.implicitly_wait(5)  # seconds
            working = True
            while working:
                jobsAdded = 0
                new_jobs = []
                # TODO: Change this to optional?? Would require SQL migration
                time.sleep( 1 )
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
                    if result_location != defaultLocation:
                        result_location = self.validate_location(self.cleanup(location.text))
                        if result_location is None:
                            continue

                    data[jobNum] = {"job": result, "location": result_location, "jobURL": "", "company": company}
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

            for entry in data:
                print( type(data[entry]["job"]) )
                print( type(data[entry]["location"]) )
                f.write(data[entry]["job"] + ' - ' + data[entry]["location"] + '\n')

            with open("/var/www/html/output", "a") as f3:
                f3.write("Yielding data...\n")
            
            yield data


        # scrape without selenium
        else:
            jobs = response.xpath(jobX + "/text()")
            f = open('results/' + company + "-jobs.txt", "w")
            # location provided
            locations = []
            if len(locationX) > 0:
                locations = response.xpath(locationX + "/text()")
            l = self.balance_lists(jobs, locationlist=locations, defaultlocation=defaultLocation)
            
            for job, location, link in l:
                result = self.cleanup(job.get())
                # calling validate locations
                result_location = location
                try:
                    result_location = self.validate_location(self.cleanup(location.text))
                    if result_location is None:
                        continue
                except:
                    result_location = location
                data[jobNum] = {"job": result, "location": result_location, "jobURL": careersURL, "company": company}
                jobNum += 1
                f.write(result + '--' + result_location + '\n')

        driver.quit()

        f.close()

        with open("/var/www/html/output", "a") as f2:
            f2.write("END OF PARSE :D\n")
