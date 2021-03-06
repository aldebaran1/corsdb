#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 10:47:21 2017

@author: Sebastijan Mrak <smrak@gmail.com>
"""

from six.moves.urllib.parse import urlparse
import ftplib
import numpy as np
import subprocess
from datetime import datetime
import yaml

def getStateList(state):
    url =  urlparse('ftp://geodesy.noaa.gov/cors/rinex/2017/150/')# 'ftp://geodesy.noaa.gov'
    lib = ftplib.FTP(url[1],'anonymous','guest',timeout=15)
    lib.cwd(url[2])
    d = []
    stations = []
    lib.retrlines('LIST', d.append)
    for line in d:
        stations.append(line[-4:])
    rxabv = [l[:2] for l in stations]
    rxlist = np.array(stations)
    rx = state
    idx = np.where(np.array(rxabv) == rx)[0]
    list_out = rxlist[idx]
    
    return list_out

def downloadObsRinexList(state=None, day=None, folder=None, t=None, filepath=None):
    """
    """
    if filepath is not None:
        statelist = []
        rxlist = []
        state = None
        with(open(filepath,'r')) as f:
            l = f.readlines()
            for line in l:
                arr = line.rstrip('\n').split(',')
                statelist.append(arr[0])
                rxlist.append(arr[1:])
            
    else:
        rxlist = getStateList(state)
    
    if day == 'yesterday':
        d = datetime.now()
        year = d.strftime('%Y')
        day = str(d.timetuple().tm_yday - 1)
    else:
        year = datetime.now().strftime('%Y')
    
    
    if isinstance(state, str):
        if (t == 'obs'):
            if rxlist.shape[0] == 0:
                print ('No receivers in the list. Please correct the prefix for state')
                exit()
            save_dir = folder + state + '/' + day + '/'
            
            subprocess.call('mkdir ' + folder + '/' + state, shell=True)
            subprocess.call('mkdir ' + folder + '/' + state + '/' + day, shell=True)
            for line in rxlist:
                subprocess.call('sudo python3 /home/smrak/Documents/cors/cors_download.py ' + 
                                year + ' ' + day  + ' ' + line + ' ' + save_dir  + ' ' + '-t obs', shell=True)
            print (rxlist.shape[0])
            print (save_dir)
            
        elif (t == 'nav'):
            subprocess.call('sudo python3 /home/smrak/Documents/cors/cors_download.py ' + 
                                year + ' ' + day  + ' ' + 'x' + ' ' + folder  + ' ' + '-t nav', shell=True)
    elif isinstance(statelist, list):
        i = 0
        for state in statelist:
            save_dir = folder + state + '/' + day + '/'
            subprocess.call('mkdir ' + folder + '/' + state, shell=True)
            subprocess.call('mkdir ' + folder + '/' + state + '/' + day, shell=True)
            print ('Saving observation files for the state of '+state)
            for line in rxlist[i]:
                subprocess.call('sudo python3 /home/smrak/Documents/cors/cors_download.py ' + 
                                year + ' ' + day  + ' ' + line + ' ' + save_dir  + ' ' + '-t obs', shell=True)
            i+=1
                
    
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('state',type=str)
    p.add_argument('day',type=str)
    p.add_argument('-f', "--dest_folder",help='IPP lat lon data with time stanps in h5file', 
                   default='/home/smrak/sharedrive/cors/', type=str)
    p.add_argument('-t', '--type', help='Type of file to download. Observation of navigation. Type "nav" or "obs"', default='obs')
    p.add_argument('-p', '--path', help='path to the filelist')
    P = p.parse_args()
    
    downloadObsRinexList(state = P.state, day=P.day, folder=P.dest_folder, t=P.type, filepath=P.path)