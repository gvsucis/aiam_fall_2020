from sqlalchemy import create_engine, Column, literal, Boolean, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (String)
from sqlalchemy.orm import sessionmaker
from scrapy.utils.project import get_project_settings
from json import load, dumps, dump

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
    coDB.companyURL = spider["baseURL"]
    coDB.careersURL = spider["careersURL"]
    coDB.jobX = spider["jobX"]
    coDB.locationX = spider["locationX"]
    coDB.nextPageX = spider["nextPageX"]
    coDB.useDriver = spider["useDriver"]

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
            raise
        finally:
            session.close()

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

    if "defaultLocation" in data:
        coDB.defaultLocation = data["defaultLocation"]
    if coDB != q:
        try:
            if q is not None:
                session.delete(q)
            session.add(coDB)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

def getTempCompany(company):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "temporary_company_table"):
        create_tables(engine)

    session = Session()
    q = session.query(TemporaryCompanyDB).filter(TemporaryCompanyDB.company == company).first()
    session.close()
    return q

def moveToMainDB(company):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    if not engine.dialect.has_table(engine, "company_table"):
        create_tables(engine)

    session = Session()
    q = session.query(CompanyDB).filter(CompanyDB.company == company).first()
    if q is not None:
        session.delete(q)

    newEntry = session.query(TemporaryCompanyDB).filter(TemporaryCompanyDB.company == company).first()
    data = newEntry.serialize()
    session.close()
    addCompany(data)


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
