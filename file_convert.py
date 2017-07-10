#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 17:36:18 2017

@author: Sebastijan Mrak <smrak@gmail.com>
"""

#import yaml
from gsit import pyRinex

#Convert obs file to HDF
def obs2HDF(fname):
    pyRinex.writeRinexObs2Hdf(fname)

#Write yaml files with headers of respective observation files
def writeHeaders(folder):
    pyRinex.writeRinexObsHeaders2yaml(folder)
def writeHeader(fname):
    pyRinex.writeRinexObsHeader2yaml(fname)
    
    
if __name__== '__main__':
    
    from argparse import ArgumentParser
    descr = '''
            '''
    p = ArgumentParser(description=descr)
    ArgumentParser(add_help=False)
    p.add_argument("-ya", "--all",help='Arg is directory to convert files to yaml.',default=None)
    p.add_argument("-y", "--yaml",help='Arg is directory to convert files to yaml.',default=None)
    p.add_argument("-o", "--hdf",help='Arg is obs file to convert it to HDF',default=None)
    
    p = p.parse_args()
    
    if p.all is not None:
        writeHeaders(p.all)
    if p.yaml is not None:
        writeHeader(p.yaml)
    if p.hdf is not None:
        obs2HDF(p.hdf)