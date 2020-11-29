import scrapy
import json
import re
from selenium import webdriver
from os import name
from urllib.parse import quote

# from pyvirtualdisplay import Display
from aiam.spiders.general_spider import Spider_General

class Builder_General(Spider_General):
    name = "builder"

    #NO PIPELINES
    custom_settings = {
        'ITEM_PIPELINES' : {

        }
    }


    def __init__(self, filename):
        self.member = {}

        with open(filename, 'r') as f:
            self.member = json.load(f)

        with open('/var/www/job_collector/virtualenv/src/aiam_fall_2020/aiam/results/output', 'w') as t:
            t.write(filename)
            t.write(str(self.member))

        super().__init__()


    def start_requests(self):

        target_chrome_driver = '/var/www/job_collector/virtualenv/src/aiam_fall_2020/aiam/ChromeDrivers/linux_chromedriver'
        if name == 'nt':
            target_chrome_driver = './ChromeDrivers/chromedriver.exe'

        self.member["driver"] = self.create_chrome_instance(target_chrome_driver)
        if "nextPageX" not in self.member:
            self.member["nextPageX"] = ''
        if "useDriver" not in self.member:
            self.member["useDriver"] = True

        yield scrapy.Request(url=self.member['careersURL'], callback=self.parse)

    def parse(self, response):
        profile = self.member
        data = {}

        self.write_profile(profile)
        driver = profile["driver"]
        company = profile["company"]
        useDriver = profile["useDriver"]
        locationX = profile["locationX"]
        jobX = profile["jobX"]
        nextPageX = profile["nextPageX"]
        careersURL = profile["careersURL"]

        print("=" * 16 + '\n' + careersURL + "\n" + "=" * 16)

        with open('/var/www/job_collector/virtualenv/src/aiam_fall_2020/aiam/results/output', 'w') as y:
            y.write("ENTERED PARSE\n")

        f = open('/var/www/job_collector/virtualenv/src/aiam_fall_2020/aiam/results/' + company + "-jobs.txt", "w")
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
                # location provided
                if len(locationX) > 0:
                    locations = driver.find_elements_by_xpath(locationX)
                    for job, location in zip(jobs, locations):
                        result = self.cleanup(job.text)
                        result_location = self.cleanup(location.text)
                        data[jobNum] = {"job": result, "location": result_location, "jobURL": "", "company": company}
                        jobNum += 1
                        f.write(result + ' - ' + result_location + '\n')
                # no locations provided, only jobs
                else:
                    for job in jobs:
                        result = self.cleanup(job.text)
                        data[jobNum] = {"job": result, "location": "Local", "jobURL": "", "company": company}
                        jobNum += 1
                        f.write(result + ' -- ' + 'Local' + '\n')

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
                locations = response.xpath(locationX + "/text()")

                for job, location in zip(jobs, locations):
                    result = self.cleanup(job.get())
                    result_location = self.cleanup(location.get())
                    data[jobNum] = {"job": result, "location": result_location, "jobURL": "", "company": company}
                    jobNum += 1
                    f.write(result + ' - ' + result_location + '\n')
            # no locations provided, only jobs
            else:
                for job in jobs:
                    result = self.cleanup(job.get())
                    data[jobNum] = {"job": result, "location": "Local", "jobURL": "", "company": company}
                    jobNum += 1
                    f.write(result + ' -- ' + 'Local' + '\n')
            yield data

        driver.quit()

        f.close()
