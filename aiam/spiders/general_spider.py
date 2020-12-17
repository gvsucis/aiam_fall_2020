import scrapy
import json
import re
from selenium import webdriver
from os import name
from urllib.parse import quote

from aiam.Models import addCompany
from aiam.env import *


class Spider_General(scrapy.Spider):
    name = "general"

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
        self.members = {}
        self.valid_locations = {}
        self.valid_states = {}
        super().__init__()

    def create_chrome_instance(self, executable_path):
        # selenium on a vps needs a display port to run google chrome
        # display = Display( visible=0, size=(800,600) )
        # display.start()
        # set up webdriver options, then return chrome instance
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-extensions')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        return webdriver.Chrome(executable_path=executable_path, chrome_options=options)

    def cleanup(self, text):
        text = text.strip().strip("\n \t").replace("  ", "").replace("\n", " ")
        return text

    def get_max_char(self, s):
        all_freq = {}
        valid_list = ['-', ' ']
        for i in s:
            if i in valid_list:
                if i in all_freq:
                    all_freq[i] += 1
                else:
                    all_freq[i] = 1
        res = max(all_freq, key=all_freq.get)
        return res

    def validate_location(self, location):
        #print("Start of validate location...")
        s = location
        s = s.replace("\n", " ")
        s = s.replace(",", " ")
        s = s.replace("-", " ")
        s = re.sub(r'[0-9]+', '', s)
        delimeter = self.get_max_char(s)
        array = s.split(delimeter)


        #if 'MICHIGAN' in location.upper():
            #print("HIT")
            #print(array)
            #print(s)
        safe_loc = False
        for word in array:
            word.strip()
            if word.upper() in self.valid_states:
                #print("SUPPOSED TO PRINT HERE: {}".format(word.upper()))
                if word.upper() != "MI" and "MICHIGAN" not in word.upper():
                    #   print("Removing: " + location)
                    return None
                else:
                    safe_loc = True

            if not safe_loc and word.upper() in self.valid_locations:
                safe_loc = True

        if not safe_loc:
            print("NOT SAFE: " + location + "\n")
            return None

        return location

    def urlencode(self, url):
        ret = quote(url).replace("%3A", ":")
        return ret

    def write_profile(self, scrapeProfile):
        with open('profiles/' + scrapeProfile["company"] + '-profile.json', 'w') as profilef:
            profile = {}
            for key in scrapeProfile:
                if key == 'driver':
                    continue
                else:
                    profile[key] = scrapeProfile[key]
            json.dump(profile, profilef)

    def balance_lists(self, joblist, defaultlocation="local", defaultlink="", locationlist=None, linklist=None):
        n = len(joblist)
        if locationlist == None or len(locationlist) < n:
            locationlist = [defaultlocation for i in range(n)]
        if linklist == None or len(linklist) < n:
            linklist = [defaultlink for i in range(n)]
        return zip(joblist, locationlist, linklist)


    def start_requests(self):

        target_chrome_driver = '/var/www/job_collector/virtualenv/src/aiam_fall_2020/aiam/ChromeDrivers/linux_chromedriver'
        ##target_chrome_driver = './ChromeDrivers/linux_chromedriver'
        if name == 'nt':
            target_chrome_driver = './ChromeDrivers/chromedriver.exe'

        # print("HIT")

        # parse json file into dictionary
        with open(PARAM_FILE, 'r') as f:
            members = json.load(f)['members']

        with open(MICHIGAN_LOCATIONS_FILE, 'r') as f:
            self.valid_locations = json.load(f)

        with open(STATES_FILE, 'r') as f:
            self.valid_states = json.load(f)

        for member in members:
            # populate self variables from the current member subdictionary
            self.members[member] = members[member]
            # a few of these don't come with the web form, manually add those in
            self.members[member]["company"] = member
            self.members[member]["driver"] = self.create_chrome_instance(target_chrome_driver)
            print("=" * 16 + '\n' + self.members[member]["careersURL"] + "\n" + "=" * 16)
            if "nextPageX" not in members[member]:
                self.members[member]["nextPageX"] = ''
            if "useDriver" not in members[member]:
                self.members[member]["useDriver"] = True
            if "defaultLocation" not in members[member]:
                self.members[member]["defaultLocation"] = 'Local'
            # supply scrapy with the data
            addCompany(self.members[member])
            yield scrapy.Request(url=self.members[member]["careersURL"], callback=self.parse, meta={"company": member})

    def parse(self, response):

        profile = self.get_profile(response)
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
                if len(locationX) <= 0:
                    locations = driver.find_elements_by_xpath(locationX)

                l = self.balance_lists(jobs, locationlist=locations, defaultlocation=defaultLocation)

                for job, location, link in l:
                    result = self.cleanup(job.text)
                    '''
                    print("THIS IS THE RESULT")
                    print(result)
                    print("This is ENNNNDDDDD of result")
                    '''
                    # calls the validate function
                    result_location = location
                    try:
                        result_location = self.validate_location(self.cleanup(location.text))
                        if result_location is None:
                            continue
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
                f.write(result + ' -- ' + result_location + '\n')
            yield data

        driver.quit()

        f.close()

    def get_profile(self, response):
        return self.members[response.meta["company"]]

    def removeDuplicates(self, data, jobsAdded):
        for i in range(jobsAdded):
            data.popitem()
        return data
