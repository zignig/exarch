#!/usr/bin/python -i

# -*- coding: utf-8 -*-

# some basic tools for bootserver manipulation

import os 

import config
from model import * 

import readline,rlcompleter
readline.parse_and_bind('tab:complete')

# load configs
pxe_menu = yaml.load(open(config.menu))
distros = yaml.load(open('config/image_urls.txt'))

def get_media():
    if 'media' in dir(config):
        path = config.media
    else:
        path = 'static/images'
    for i in distros.keys():        
        if distros[i] != None:
            print '\n'+i
            # check if folder exists
            try:
                os.stat(path+os.sep+i)
            except:
                print 'no folder '+i
                os.mkdir(path+os.sep+i)
            # check if processro folder is there
            for j in distros[i]:
                print '\t '+j
                directory = path+os.sep+i+os.sep+j
                try:
                    os.stat(directory)
                except:
                    os.mkdir(directory)
                data = distros[i][j]
                kernel = directory+os.sep+data['boot']
                file_system =  directory+os.sep+data['fs']
                try:
                    os.stat(kernel)
                except:
                    print 'get file ' + str(data['kernel'])
                try:
                    os.stat(file_system)
                except:
                    print 'get file ' + str(data['initrd'])    

def add_user(username,password):
    u = User.query.filter(User.name == username).first()
    if u != None:
        print "User already exists"
    else:
        new_user = User(username,password)
        db_session.add(new_user)
        db_session.commit()
        
if __name__ == "__main__":
    get_media()