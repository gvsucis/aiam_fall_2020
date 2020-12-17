import scrapy
import json
from os import name
# from pyvirtualdisplay import Display
from aiam.Models import get_all_companies
from aiam.spiders.general_spider import Spider_General
from aiam.env import *
import time


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

    def shouldWriteFiles(self):
        return False
