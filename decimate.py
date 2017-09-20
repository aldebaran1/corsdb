#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Sebastijan Mrak <smrak@gmail.com>
"""
import glob
import os
import subprocess
from time import sleep

#folder = '/home/smrak/sharedrive/cors/al/184/'
def decimate(folder, sufix=None, fs=1, dec=15):
    if sufix is None:
        wlstr = '*.17o'
    else:
        wlstr = sufix
        
    filestr = os.path.join(folder,wlstr)
    flist = glob.glob(filestr)
    for file in flist:
        head, tail = os.path.split(file)
        rx = tail[0:8]
        newfile = head + '/' + rx + '_' + str(dec) + '.17o'
        if not os.path.isfile(newfile):
            print('Decimating: ', file)
            subprocess.call('./teqc -O.int ' + str(fs) + ' -O.dec ' + str(dec) + ' ' + file + ' > ' + file[:-4] + '_' + str(dec) + '.17o', shell=True)
            sleep(1)

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('folder',type=str)
    p.add_argument('-a','--fs', help='original time resolution', default=1, type=int)
    p.add_argument('-b','--dec', help='decimated time resolution', default=15, type=int)
    p.add_argument('-s','--sufix', help='sufix of observation files to be decimated', default='*.17o', type=str)
    P = p.parse_args()
    
    decimate(P.folder, fs=P.fs, dec=P.dec, sufix=P.sufix)