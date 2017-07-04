#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 17:26:18 2017

@author: Sebastijan Mrak <smrak@gmail.com>
"""

from six.moves.urllib.parse import urlparse
import ftplib
import numpy as np
    
#parsed = urlparse(host)
url =  urlparse('ftp://geodesy.noaa.gov/cors/rinex/2017/150/')# 'ftp://geodesy.noaa.gov'
lib = ftplib.FTP(url[1],'anonymous','guest',timeout=15)
lib.cwd(url[2])
d = []
stations = []
a = lib.retrlines('LIST', d.append)
for line in d:
    stations.append(line[-4:])
rxabv = [l[:2] for l in stations]
rxlist = np.array(stations)
rx = 'tn'
idx = np.where(np.array(rxabv) == rx)[0]
list_out = rxlist[idx]
print (rxlist[idx])