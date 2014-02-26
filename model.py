# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime , Enum

import string,random,datetime,yaml

engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def rand_string(length=16):
    a = ''.join(random.choice(string.hexdigits) for i in range(length))
    return a 

def default_fill():
    # fill in some default data on database creation
    print 'fill in default data'
    f = open('servers.yaml')
    servers = yaml.load(f)
    f.close()
    for i in servers:
        t = Machine(i,servers[i])
        db_session.add(t)
    db_session.commit()
    return
    
def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.metadata.create_all(bind=engine)
    if Machine.query.count() == 0:
        default_fill()
    
class Session(Base):
    " session storage for machine installs"
    __tablename__ = 'session'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    key = Column(String(16),unique=True)
    status = Column(Enum('init','boot','install','configure','finish'))
    
    def __init__(self):
        self.time = datetime.datetime.now()
        self.key = rand_string()
        self.status = 'init'
        
class Machine(Base):
    __tablename__ = 'machines'
    id = Column(Integer, primary_key=True)
    name = Column(String(50),unique=True)
    description = Column(String(50),unique=True)
    
    def __init__(self,name,description):
        self.name = name
        self.description = description
    
    def __repr__(self):
        txt = ' '+self.name+' : '+self.description
        return txt
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(120))
    
    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)