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
