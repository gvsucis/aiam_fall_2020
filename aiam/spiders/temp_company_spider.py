import scrapy
import json
from os import name, remove
# from pyvirtualdisplay import Display
from aiam.Models import getTempCompany, TemporaryCompanyDB
from aiam.spiders.general_spider import Spider_General
from aiam.env import *
import time

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

    def get_profile(self, response):
        return self.member