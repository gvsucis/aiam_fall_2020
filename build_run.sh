#!/bin/bash
cd /var/www/job_collector/virtualenv/src/aiam_fall_2020/aiam
/var/www/job_collector/virtualenv/bin/python3.8 -m scrapy crawl builder -a filename=$1
