from sqlalchemy import create_engine, Column, literal, Boolean, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (String)
from sqlalchemy.orm import sessionmaker
from scrapy.utils.project import get_project_settings

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
    coDB.useDriver = spider["useDriver"] == "on"

    if "defaultLocation" in spider:
        coDB.defaultLocation = spider["defaultLocation"]
    if coDB != q:
        try:
            if q != None:
                session.delete(q)
            session.add(coDB)
            session.commit()
        except:
            session.rollback()
            print(type(q))
            raise
        finally:
            session.close()
