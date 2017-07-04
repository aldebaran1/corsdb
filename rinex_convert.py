#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 13:25:38 2017

@author: Sebastijan Mrak <smrak@gmail.com>
"""
import os
import glob
from time import sleep
import pyRinex

def convertObs2HDF(folder=None, year=str(2017)):
    yr = year[-2:]
    wlstr ='*.'+yr+'o'
    filestr = os.path.join(folder,wlstr)
    flist = glob.glob(filestr)
#    print (flist)
    for file in flist:
        print ('Converting file: ', file)
        pyRinex.writeRinexObs2Hdf(file)
        sleep(60*5)
def convertYaml(folder=None):
    pyRinex.writeRinexObsHeaders2yaml(folder)
    
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('folder',type=str)
    p.add_argument('-y', '--year',default='2017',type=str)
    p.add_argument('-t', '--type', help='Type of conversion, yaml of hdf')
#    p.add_argument('-f', "--dest_folder",help='IPP lat lon data with time stanps in h5file', 
#                   default='/home/smrak/sharedrive/cors/', type=str)
#    p.add_argument('-t', '--type', help='Type of file to download. Observation of navigation. Type "nav" or "obs"', default='obs')
    P = p.parse_args()
    
    if P.type == 'hdf':
        convertObs2HDF(folder = P.folder, year=P.year)
    elif P.type == 'yaml':
        convertYaml(folder = P.folder)