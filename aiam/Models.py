from sqlalchemy import create_engine, Column, literal, Boolean, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (String)
from sqlalchemy.orm import sessionmaker
from scrapy.utils.project import get_project_settings
from json import load, dumps, dump
from os import chdir, listdir

DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_tables(engine):
    DeclarativeBase.metadata.create_all(engine)


def delete_table(engine):
    DeclarativeBase.metadata.drop_all(engine)


def drop_job_table(engine):
    table = DeclarativeBase.metadata.tables.get('job_table')
    DeclarativeBase.metadata.drop_all(engine, [table], checkfirst=True)


class JobDB(DeclarativeBase):
    __tablename__ = "job_table"
    # job location and company uniquely ID a job
    job = Column('job', String(200), primary_key=True)
    location = Column('location', String(200), primary_key=True)
    jobURL = Column('jobURL', String(400))
    company = Column('company', String(200), primary_key=True)

    def serialize(self):
        return {
            'company': self.company,
            'jobURL': self.jobURL,
            'location': self.location,
            'job': self.job
        }



class CompanyDB(DeclarativeBase):
    __tablename__ = "company_table"

    company = Column('company', String(200), primary_key=True)
    companyURL = Column('companyURL', String(200))
    careersURL = Column('careersURL', String(400))
    jobX = Column('jobX', String(400))
    locationX = Column('locationX', String(400))
    nextPageX = Column('nextPageX', String(400))
    useDriver = Column('useDriver', Boolean)
    defaultLocation = Column('defaultLocation', String(400), default="N/A")
    
    def serialize(self):
        return {
            'company': self.company,
            'companyURL': self.companyURL,
            'careersURL': self.careersURL,
            'jobX': self.jobX,
            'locationX': self.locationX,
            'nextPageX': self.nextPageX,
            'useDriver': self.useDriver,
            'defaultLocation': self.defaultLocation
        }

class TemporaryCompanyDB(DeclarativeBase):
    __tablename__ = "temporary_company_table"

    company = Column('company', String(200), primary_key=True)
    companyURL = Column('companyURL', String(200))
    careersURL = Column('careersURL', String(400))
    jobX = Column('jobX', String(400))
    locationX = Column('locationX', String(400))
    nextPageX = Column('nextPageX', String(400))
    useDriver = Column('useDriver', Boolean)
    defaultLocation = Column('defaultLocation', String(400), default="N/A")

    def serialize(self):
        return {
            'company': self.company,
            'companyURL': self.companyURL,
            'careersURL': self.careersURL,
            'jobX': self.jobX,
            'locationX': self.locationX,
            'nextPageX': self.nextPageX,
            'useDriver': self.useDriver,
            'defaultLocation': self.defaultLocation
        }


def addCompany(spider):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    create_tables(engine)
    q = session.query(CompanyDB).filter(CompanyDB.company == spider["company"]).first()
    # add the company record if it doesn't already exist
    coDB = CompanyDB()
    coDB.company = spider["company"]
    coDB.companyURL = spider["companyURL"]
    coDB.careersURL = spider["careersURL"]
    coDB.jobX = spider["jobX"]
    coDB.locationX = spider["locationX"]
    coDB.nextPageX = spider["nextPageX"]
    coDB.useDriver = spider["useDriver"]

    exitcode = 1

    if "defaultLocation" in spider:
        coDB.defaultLocation = spider["defaultLocation"]
    if coDB != q:
        try:
            if q is not None:
                session.delete(q)
            session.add(coDB)
            session.commit()
        except:
            session.rollback()
            print(type(q))
            exitcode = 0
        finally:
            session.close()
    
    return exitcode

def getTempCompanies():
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    create_tables(engine)
    q = session.query(TemporaryCompanyDB).all()
    
    ret = {}
    # serialize all results
    # will look like: { company1: {profile}, company2: {profile}, company3: {profile}... }
    for company in q:
        new_profile = company.serialize()
        company_id = new_profile[ 'company' ]
        ret[ company_id ] = new_profile
    # json encode the dict of dicts for javascript to read
    ret = dumps( ret )
    
    # must print ret for bash script to parse output back into php
    print(ret)
    # nothing using this right now, but returning just to return something in case needed in future
    return ret


def addTempCompany(filename):
    # NOTE: path needs to be included in the provided filename!
    data = {}
    try:
        with open(filename, 'r') as f:
            data = load(f)
    except:
        with open('logs/db_errors', 'a') as f:
            f.write('{} Does not exist!\n'.format(filename))
            return

    engine = db_connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    create_tables(engine)
    q = session.query(TemporaryCompanyDB).filter(TemporaryCompanyDB.company == data["company"]).first()
    # add the company record if it doesn't already exist
    coDB = TemporaryCompanyDB()
    coDB.company = data["company"]
    coDB.companyURL = data["baseURL"]
    coDB.careersURL = data["careersURL"]
    coDB.jobX = data["jobX"]
    coDB.locationX = data["locationX"]
    coDB.nextPageX = data["nextPageX"]
    coDB.useDriver = data["useDriver"] is True

    exitcode = 1

    if "defaultLocation" in data:
        coDB.defaultLocation = data["defaultLocation"]
    if coDB != q:
        try:
            try:
                session.delete(q)
            except:
                exitcode = 2 # no previously made temp profile was found for this company! 
            session.add(coDB)
            session.commit()
        except:
            session.rollback()
            exitcode = 0
        finally:
            session.close()
    return exitcode

def getTempCompany(company):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "temporary_company_table"):
        create_tables(engine)

    session = Session()
    q = session.query(TemporaryCompanyDB).filter(TemporaryCompanyDB.company == company).first()
    session.close()
    return q

def deleteTempCompany(company):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "temporary_company_table"):
        create_tables(engine)

    session = Session()
    q = session.query(TemporaryCompanyDB).filter(TemporaryCompanyDB.company == company).first()
    
    try:
        session.delete(q)
        session.commit()
        print("Success!\n")
    except:
        print("ERR\n")
    session.close()


def getActiveCompany( company ):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "company_table"):
        create_tables(engine)

    session = Session()
    q = session.query( CompanyDB ).filter( CompanyDB.company == company ).first()
    session.close()
    return q

def deleteActiveCompany( company ):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "company_table"):
        create_tables(engine)

    session = Session()
    q = session.query( CompanyDB ).filter( CompanyDB.company == company ).first()
    ret = "Something went wrong"
    try:
        session.delete(q)
        session.commit()

        ret = "Deletion success"
    except:
        ret = "Error while deleting"
    session.close()
    deleteJobsForCompany( company )
    print( ret )

def getJobsForActiveCompany( company ):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "job_table"):
        create_tables(engine)
    
    session = Session()
    jobs = session.query( JobDB ).filter( JobDB.company == company ).all()
    ret = {}; job_id = 0;
    if jobs is not None:
        for job in jobs:
            ret[ str(job_id) ] = job.serialize()
            job_id += 1
    # json encode the dict of dicts for javascript to read
    ret = dumps( ret )
    # must print ret for bash script to parse output back into php
    print(ret)
    session.close()
    return ret

def getAllJobResults():
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "job_table"):
        create_tables(engine)
    
    jobList = {}; job_id = 0;
    session = Session()
    jobs = session.query( JobDB).all()
    if jobs is not None:
        for job in jobs:
            if job.company not in jobList:
                jobList[job.company] = [job.serialize()]
            else:
                jobList[job.company].append(job.serialize())
    jobList = dumps( jobList )
    print(jobList)
    session.close()
    return jobList

# Note this probably should've been called deleteJobsForActiveCompany
def deleteJobsForCompany( company ):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "job_table"):
        create_tables(engine)

    session = Session()
    try:
        q = session.query( JobDB ).filter( JobDB.company == company ).delete()
        session.commit()
        print("Success!\n")
    except:
        session.rollback()
        print("Error deleting jobs for {}".format( company ) )
    session.close()

def moveToMainDB(company):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "company_table"):
        create_tables(engine)

    session = Session()
    q = session.query(CompanyDB).filter(CompanyDB.company == company).first()
    if q is not None:
        session.delete(q)
        session.commit()

    newEntry = session.query(TemporaryCompanyDB).filter(TemporaryCompanyDB.company == company).first()
    data = newEntry.serialize()

    #session.delete( newEntry )
    session.close()

    # check return code for errors
    if addCompany(data) > 0:
        deleteTempCompany( company )


# this one is used specifically for javascript the whole php/bash pipeline needs this
def getActiveCompanies():
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "company_table"):
        create_tables(engine)

    session = Session()
    ret = {}
    companies = session.query(CompanyDB)
    for company in companies:
        ret[company.company] = company.serialize()

    # json encode the dict of dicts for javascript to read
    ret = dumps( ret )

    # must print ret for bash script to parse output back into php
    print(ret)
    
    return ret

# grab the job results for a single company
# takes in company name string
def getCompanyResult( company ):
    result_filename_signature = '-jobs.txt'
    results_directory = 'results/'
    ret = {}

    try:
        with open( results_directory + company + result_filename_signature ) as f:
            ret[ company ] = []
            # output will look like: { companyA: [ 'job1 - location1', 'job2 - location2', ... ]
            for line in f:
                ret[ company ].append( line )
    except:
        print( "Error\n" )
    # json encode the read thru jobs result
    ret = dumps( ret )
    # must print result to stdout, as this function is primarily used by the php-bash pipeline
    # bash can only read this thru printing to stdout
    print( ret )
    # currently this return is not being used by anything else, only adding this here for
    # potential future usage. Remember this function is primarily used by bash so printing == end goal
    return ret

# for inner python workings, only used by other python code
def get_all_companies():
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "company_table"):
        create_tables(engine)

    session = Session()
    members = {}
    companies = session.query(CompanyDB)
    for company in companies:
        members[company.company] = company.serialize()

    return members
