# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import mysql.connector

class TutorialPipeline:

    def __init__(self):
        self.create_connections()
        self.create_table()


    def create_connections(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="Nwpld1234",
            database="aiam_test"
        )
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute(""" DROP TABLE IF EXISTS quotes_tb """)
        self.curr.execute(""" CREATE TABLE quotes_tb (
            title text,
            author text,
            tags text
        )
        """)

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        self.curr.execute(""" insert into quotes_tb values (%s, %s, %s) """,(
            item['title'][0],
            item['author'][0],
            item['tags'][0]
        ))
        self.conn.commit()