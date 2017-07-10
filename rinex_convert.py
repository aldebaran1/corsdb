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
#import file_convert
import subprocess

def callsubprocess(file):
    try:
        subprocess.call('python3 file_convert.py -o ' + file, shell=True)
    except:
        raise ValueError 
        
def convertObs2HDF(folder=None, year=str(2017)):
    yr = year[-2:]
    wlstr ='*.'+yr+'o'
    filestr = os.path.join(folder,wlstr)
    flist = glob.glob(filestr)
#    print (flist)
    for file in flist:
        new_fname = file[:-3] + 'h5'
        if not os.path.exists(new_fname):
            print ('Converting file: ', file)
            callsubprocess(file)
            sleep(4)
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