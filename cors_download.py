#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 13:19:38 2017

@author: Sebastijan Mrak <smrak@gmail.com>
"""

from six.moves.urllib.parse import urlparse
import ftplib
from os.path import expanduser
from time import sleep

def getRinexObs(year,day,site,odir,ftype,clobber=False):
    """
    year,month,day: integer
    hour, minute:  start,stop integer len == 2
    """
    
    #parsed = urlparse(host)
    url =  urlparse('ftp://geodesy.noaa.gov/cors/rinex/')# 'ftp://geodesy.noaa.gov'
    #fpath = '/cors/rinex/'
    if len(str(day)) == 2:
        day = '0'+str(day)
    elif len(str(day)) == 1:
        day = '00'+str(day)
    elif len(str(day)) == 3:
        day = str(day)
    else: 
        print ('Error - day has to be a string 0-365')

#%% get available files for this day
    with ftplib.FTP(url[1],'anonymous','guest',timeout=15) as F:
        rpath = url[2] + '/' + str(year) + '/' + day + '/' + str(site) + '/'
        #print (rpath)
        F.cwd(rpath)
        
        fn_year = str(year)[2:]
        filename = site + day + '0.' + fn_year + 'o.gz'
        #download observation file
        if ftype == 'obs':
            ofn = odir + filename
            with open( ofn, 'wb') as h:
                F.retrbinary('RETR {}'.format(filename), h.write)
                sleep(1)
        elif ftype == 'nav':    
            rpath2 = url[2] + '/' + str(year) + '/' + day + '/'
            #download navigation faile
            F.cwd(rpath2)
            navfilename = 'brdc' + day + '0.' + fn_year + 'n.gz'
            ofn = odir + navfilename
            with open(ofn, 'wb') as h:
                F.retrbinary('RETR {}'.format(navfilename), h.write)
                sleep(1)
        else: 
            print ('Wrong file format -t')
            
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('year',type=int)
    p.add_argument('day',type=int)
    p.add_argument('site',type=str)
    p.add_argument('odir',type=str)
    p.add_argument('-t', '--type', help='type of the file you wish to download. Obs or Nav', default='obs')
    P = p.parse_args()
    
    getRinexObs(P.year, P.day, P.site, P.odir, P.type)