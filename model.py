# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime , Enum

import string,random,datetime,yaml
import hashlib,uuid

import config
engine = create_engine(config.sqlurl, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def rand_string(length=16):
    a = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return a 

def default_fill():
    # fill in some default data on database creation
    print 'fill in default data'
    f = open('/opt/bootserver/config/servers.yaml')
    servers = yaml.load(f)
    f.close()
    for i in servers:
        t = Machine(i,servers[i]['os'],servers[i]['description'])
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
    #if User.query.count() == 0:
    #    u = User('','')
        
class Session(Base):
    " session storage for machine installs"
    __tablename__ = 'session'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    active = Column(Integer,default=0)
    key = Column(String(16),unique=True)
    macaddress = Column(String(50))#,unique=True)
    status = Column(Enum('init','boot','install','configure','finish',name='status'))
    name = Column(String(50))
    processor = Column(String(20))
    platform = Column(String(20))

    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.active = 1
        self.key = rand_string()
        self.status = 'init'
    
    def close(self):
        if self.active == 1:
            self.active = 0
            self.end_time = datetime.datetime.now()
            db_session.add(self)
            db_session.commit()
        
    @staticmethod
    def valid_key(val):
        k = Session.query.filter(Session.key == val,Session.active == 1).first()
        if k != None:
            return True
        else:
            return False
            
    @staticmethod
    def valid_mac(mac):
        # check some basic mac address features
        if len(string.split(mac,':')) != 6:
            return False
        k = Session.query.filter(Session.macaddress == mac,Session.active == 1).one()
        if k != None:
            return True
        else:
            return False
            
    @staticmethod
    def get_session(val):
        k = Session.query.filter(Session.key == val).first()
        return k
            
class Images(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    name = Column(String(50),unique=True)
    active = Column(Integer,default=0)
    
class Machine(Base):
    __tablename__ = 'machines'
    id = Column(Integer, primary_key=True)
    name = Column(String(50),unique=True)
    description = Column(String(50),unique=True)
    platform = Column(String(50))
    
    def __init__(self,name,platform,description):
        self.name = name
        self.platform = platform
        self.description = description
    
    def __repr__(self):
        txt = ' '+self.name+' : '+self.description
        return txt
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    active = Column(Integer,default=1)
    password = Column(String(40))
    salt = Column(String(32))
    
    def __init__(self, name=None, password=None):
        self.name = name
        self.salt = uuid.uuid4().hex
        self.password = hashlib.sha1(self.salt.encode() + password.encode()).hexdigest()
    
    def check_password(self,password):
        if password != '':
            new_hash = hashlib.sha1(self.salt.encode() + password.encode()).hexdigest()
            if new_hash == self.password:
                return True
            else:
                return False
        else:
            return False
        return False
        
    def is_anonymous(self):
        return False
            
    def is_authenticated(self):
        return True
        
    def get_id(self):
        return self.id
        
    def is_active(self):
        if self.active == 1:
            return True
        else:
            return False 
            
    def __repr__(self):
        return '<User %r>' % (self.name)
        
if __name__ == "__main__":
    print('create database tables')
    init_db()
