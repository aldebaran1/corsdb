#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 12:10:06 2017

@author: Sebastijan Mrak <smrak@gmail.com>
"""

from six.moves.urllib.parse import urlparse
import os
import ftplib
import numpy as np
import subprocess
from datetime import datetime
import yaml

def getStateList(year, day):
    url =  urlparse('ftp://geodesy.noaa.gov/cors/rinex/'+year+'/'+day+'/')# 'ftp://geodesy.noaa.gov'
    lib = ftplib.FTP(url[1],'anonymous','guest',timeout=15)
    lib.cwd(url[2])
    d = []
    stations = []
    lib.retrlines('LIST', d.append)
    for line in d:
        stations.append(line[-4:])
    
    return np.array(stations)

def checkDir(folder):
    
    if not os.path.exists(folder):
        subprocess.call('mkdir {}'.format(folder[:-1]), shell=True)
    else:
        pass

def downloadObsRinexList(year=None, day=None, folder=None):
    """
    """
    if (year is not None) and (day is not None):
        rxlist = getStateList(str(year), str(day))
    else:
        print ('Enter the year and day arguments')
        exit()
    if day == 'yesterday':
        d = datetime.now()
        year = d.strftime('%Y')
        day = str(d.timetuple().tm_yday - 1)
    else:
        year = datetime.now().strftime('%Y')

    if rxlist.shape[0] == 0:
        print ('No receivers in the list. Please correct the prefix for state')
        exit()
    save_dir = folder + str(day) + '/'
    
    checkDir(save_dir)

    for line in rxlist:
        try:
            subprocess.call('python3 /home/smrak/Documents/cors/cors_download.py ' + 
                            year + ' ' + day  + ' ' + line + ' ' + save_dir  + ' ' + '-t obs', shell=True)
        except Exception as e:
            print(e)
    print (rxlist.shape[0])
    print ('Saving the data to the directory: ', save_dir)
    
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('year',type=str)
    p.add_argument('day',type=str)
    p.add_argument('-f', "--dest_folder",help='IPP lat lon data with time stanps in h5file', 
                   default='/home/smrak/sharedrive/cors/all/', type=str)
    P = p.parse_args()
    
    downloadObsRinexList(day=P.day, year=P.year, folder=P.dest_folder)