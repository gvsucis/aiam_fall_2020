#!/bin/bash
cd virtualenv/src/aiam_fall_2020/aiam
/var/www/job_collector/virtualenv/bin/python3.8 -m scrapy crawl general
#echo "XXX" > data.txt
