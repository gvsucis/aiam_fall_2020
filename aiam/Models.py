from sqlalchemy import create_engine, Column, literal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ( String)
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


class JobDB(DeclarativeBase):
    __tablename__ = "job_table"
    #job location and company uniquely ID a job
    job = Column('job', String(200), primary_key=True)
    location = Column('location', String(200), primary_key=True)
    jobURL = Column('jobURL', String(200))
    company = Column('company', String(200), primary_key=True)


class CompanyDB(DeclarativeBase):
    __tablename__ = "company_table"

    company = Column('company', String(200), primary_key=True)
    companyURL = Column('companyURL', String(200))
    jobsURL = Column('jobsURL', String(200))



class AddCompany():
    def __init__(self, spider):
        engine = db_connect()
        self.Session = sessionmaker(bind=engine)
        session = self.Session()
        create_tables(engine)
        q = session.query(CompanyDB).filter(CompanyDB.company == spider["company"])
        # add the company record if it doesn't already exist
        if (not session.query(literal(True)).filter(q.exists()).scalar()):
            coDB = CompanyDB()
            coDB.company = spider["company"]
            coDB.companyURL = spider["baseURL"]
            coDB.jobsURL = spider["careersURL"]
            try:
                session.add(coDB)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()
