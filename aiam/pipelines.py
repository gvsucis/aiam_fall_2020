# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy import literal
from sqlalchemy.orm import sessionmaker
from aiam.Models import JobDB, db_connect, create_tables, drop_job_table


class AiamPipeline:
	def process_item(self, item, spider):
		print("XXX{}".format(item));
		return item

class DropJobTablePipeline:
    def __init__(self):
        engine = db_connect()
        drop_job_table(engine)

class SetupDBTablesPipeline(object):
    def __init__(self):
        engine = db_connect()
        #delete_table(engine)
        self.Session = sessionmaker(bind=engine)
        if not (engine.dialect.has_table(engine, "job_table")
                or engine.dialect.has_table(engine, "company_table")
                or engine.dialect.has_table(engine, "temporary_company_table")
        ):
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
        print("\n\n\nIS IN PIPELINE!\n\n\n\n" )

        """
        This method is called for every item pipeline component.
        """
        #allJobs = []
        for key, item in items.items():
            session = self.Session()
            q = session.query(JobDB).filter(
                (JobDB.job == item["job"]) & (JobDB.location == item["location"]) & (JobDB.company == item["company"])).first()
            if q is None:
                print("\n\nq is none\n\n")
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
                    print("Error in db add job\n")
            else:
                print(q.serialize())
            session.close()
            
        #session = self.Session()
        return items
