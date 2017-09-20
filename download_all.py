#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 12:10:06 2017

@author: Sebastijan Mrak <smrak@gmail.com>
"""

from six.moves.urllib.parse import urlparse
import ftplib
import numpy as np
import subprocess
from datetime import datetime
import yaml

def getStateList():
    url =  urlparse('ftp://geodesy.noaa.gov/cors/rinex/2017/233/')# 'ftp://geodesy.noaa.gov'
    lib = ftplib.FTP(url[1],'anonymous','guest',timeout=15)
    lib.cwd(url[2])
    d = []
    stations = []
    lib.retrlines('LIST', d.append)
    for line in d:
        stations.append(line[-4:])
    
    return np.array(stations)

def downloadObsRinexList(day=None, folder=None):
    """
    """
    rxlist = getStateList()
    
    if day == 'yesterday':
        d = datetime.now()
        year = d.strftime('%Y')
        day = str(d.timetuple().tm_yday - 1)
    else:
        year = datetime.now().strftime('%Y')
    
    
    if rxlist.shape[0] == 0:
        print ('No receivers in the list. Please correct the prefix for state')
        exit()
    save_dir = folder

    for line in rxlist:
        try:
            subprocess.call('python3 /home/smrak/Documents/cors/cors_download.py ' + 
                            year + ' ' + day  + ' ' + line + ' ' + save_dir  + ' ' + '-t obs', shell=True)
        except Exception as e:
            print(e)
    print (rxlist.shape[0])
    print (save_dir)                
    
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('day',type=str)
    p.add_argument('-f', "--dest_folder",help='IPP lat lon data with time stanps in h5file', 
                   default='/home/smrak/sharedrive/cors/', type=str)
    P = p.parse_args()
    
    downloadObsRinexList(day=P.day, folder=P.dest_folder)