# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
#from itemadapter import ItemAdapter
#from sqlalchemy import literal
#from sqlalchemy.orm import sessionmaker
#from aiam.Models import JobDB, db_connect, create_tables, delete_table

'''
class AiamPipeline:
	def process_item(self, item, spider):
		print("XXX{}".format(item));
		return item


class SetupDBTablesPipeline(object):
    def __init__(self):
        engine = db_connect()
        # delete_table(engine)
        self.Session = sessionmaker(bind=engine)
        if not (engine.dialect.has_table(engine, "job_table") or engine.dialect.has_table(engine, "company_table")):
            create_tables(engine)


class ScrapySpiderPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        self.Session = sessionmaker(bind=engine)
        #create the job table if it doesn't exist
        if not engine.dialect.has_table(engine, "job_table"):
            create_tables(engine)

    def process_item(self, items, spider):
        """
        This method is called for every item pipeline component.
        """
        #allJobs = []
        for key, item in items.items():
            session = self.Session()
            q = session.query(JobDB).filter(
                JobDB.job == item["job"] and JobDB.location == item["location"] and JobDB.company == item["company"])
            if (not session.query(literal(True)).filter(q.exists()).scalar()):
                jobdb = JobDB()
                jobdb.job = item["job"]
                jobdb.location = item["location"]
                jobdb.jobURL = item["jobURL"]
                jobdb.company = item['company']
                #allJobs.append(jobdb)
                #session.close()
                try:
                    ##session.bulk_save_objects(allJobs)
                    session.add(jobdb)
                    session.commit()
                except:
                    session.rollback()
                    raise
                finally:
                    session.close()

        #session = self.Session()



        return items
'''