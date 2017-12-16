#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 12:34:43 2017

@author: Sebastijan Mrak <smrak@gmail.com>
"""

from gsit import pyGpsUtils, pyGps
import pandas
from pandas import read_hdf
import csv
import numpy as np
import h5py
import yaml
import os,glob
import datetime
from pymap3d.coordconv3d import ecef2geodetic

def plotCorsMap():
    fn = '/home/smrak/Documents/eclipse/corslist.txt'
    #f = open(fn, 'r')
    with open(fn, 'r') as F:
        next(F)
        data = list(csv.reader(F))
    rx = []
    lat = []
    lon = []
    for row in data:
        rx.append(row[0])
        lat.append(float(row[4]))
        lon.append(float(row[5]))
        
    # Read in Totality path
    data = h5py.File('/home/smrak/Documents/eclipse/totality.h5', 'r')
    center_lat = np.array(data['path/center_lat'])
    center_lon = np.array(data['path/center_lon'])
    north_lat = np.array(data['path/north_lat'])
    north_lon = np.array(data['path/north_lon'])
    south_lat = np.array(data['path/south_lat'])
    south_lon = np.array(data['path/south_lon'])
        
    RX = np.vstack( (lat, lon) )
    
    pyGpsUtils.plotGpsMapTrajectory(lat=[], lon=[], rx=RX, #totalityc = [center_lat,center_lon],
                                    totalityu = [north_lat,north_lon], totalityd = [south_lat,south_lon],
                                    labels=None, 
                             timelim=None, latlim=[30, 42], 
                             parallels = [30,35,40], meridians=[-100,-85,-70],
                             lonlim=[-100, -70], center=[40, -80])
    

def saveTrajectories2HDF(day='184', state='tn', el_mask=30, altitude=100, 
                         hdffilename = 'trajectories_tn.h5',loop=True):

    hdffolder = '/home/smrak/sharedrive/cors/'
    navfolder = '/home/smrak/sharedrive/cors/nav/'
    ymlfolder = '/home/smrak/sharedrive/cors/'
    #Find HDF5 filename
    wlstr ='*' + day + '*.h5'
    filestr = os.path.join(hdffolder+state+'/' + day + '/', wlstr)
    flistHDF = glob.glob(filestr)
    #Find NAV filename
    wlstr ='*' + str(day) + '*.17n'
    filestr = os.path.join(navfolder, wlstr)
    flistNAV = glob.glob(filestr)
    #Find YAML filenamE
    wlstr ='*'+ str(day) + '*.yaml'
    filestr = os.path.join(ymlfolder+state+'/'+day+'/', wlstr)
    flistYML = glob.glob(filestr)
    
    h5file = h5py.File(hdffilename, 'w')
    gr = h5file.create_group(day)
    h5state = gr.create_group(state)
    
    if loop:
        for i in range(len(flistHDF)):
            hdffn = flistHDF[i]
            navfn = flistNAV[0]
            ymlfn = flistYML[i]
            
            # YAML import header
            stream = yaml.load(open(ymlfn, 'r'))
            rx_xyz = stream.get('APPROX POSITION XYZ')
            rx_llt = ecef2geodetic(rx_xyz[0], rx_xyz[1], rx_xyz[2])
            #Timelim
            timelim = [datetime.datetime(2017,7,3,15,30,0), datetime.datetime(2017,7,3,19,30,0)]
            
            h5rx = h5state.create_group(hdffn[-11:-7])
            h5rx.create_dataset('rxpos', data=rx_llt)
            
            # HDF Observations
            try:
                data = read_hdf(hdffn)
                obstimes = np.array((data.major_axis))
                obstimes = pandas.to_datetime(obstimes[::10]) - datetime.timedelta(seconds=18)
                idt = np.where( (obstimes>timelim[0]) & (obstimes<timelim[1]))
                obstimes = obstimes[idt]
                #
                h5rx.create_dataset('time', data=pyGps.datetime2posix(obstimes))
                #
                dumb = data['L1', :,1, 'data']
                svlist = dumb.axes[0]
                for sv in svlist:
                    # GPS only svnum <=32
                    az = np.nan*np.zeros(obstimes.shape[0])
                    el = np.nan*np.zeros(obstimes.shape[0])
                    lat = np.nan*np.zeros(obstimes.shape[0])
                    lon = np.nan*np.zeros(obstimes.shape[0])
                    if sv <= 32: 
                        h5sv = h5rx.create_group('sv'+str(sv))
                        aer = pyGps.getIonosphericPiercingPoints(rx_xyz, sv, obstimes, altitude, navfn, cs='aer')
                        llt = pyGps.getIonosphericPiercingPoints(rx_xyz, sv, obstimes, altitude, navfn, cs='wsg84')
                        idel = np.where( aer[1] > el_mask)[0]
                        az[idel] = aer[0][idel]
                        el[idel] = aer[1][idel]
                        lat[idel] = llt[0][idel]
                        lon[idel] = llt[1][idel]
                        h5sv.create_dataset('az', data=az)
                        h5sv.create_dataset('el', data=el)
                        h5sv.create_dataset('lat', data=lat)
                        h5sv.create_dataset('lon', data=lon)
                        print ('Saving data for sat: '+str(sv))
                    else:
                        break
            except:
                raise ValueError 
    h5file.close()
#saveTrajectories2HDF(day='184', state='nc', hdffilename='nclist.h5')
################################################################################


def plotTrajectories(day='184', state='tn', timelim=None):
    
    # Read in Totality path
    data = h5py.File('/home/smrak/Documents/eclipse/totality.h5', 'r')
    center_lat = np.array(data['path/center_lat'])
    center_lon = np.array(data['path/center_lon'])
    north_lat = np.array(data['path/north_lat'])
    north_lon = np.array(data['path/north_lon'])
    south_lat = np.array(data['path/south_lat'])
    south_lon = np.array(data['path/south_lon'])
    if timelim is not None:
        timelim = pyGps.datetime2posix(timelim)
    
    if isinstance(state, str):
        file = state+'list.h5'
        data = h5py.File(file, 'r')
        path = data[day+'/'+state+'/']
        c = 0
        for k in path.keys():
            time = np.array(data[day+'/'+state+'/' + '/'+ k +'/time'])
            svlist = np.array(data[day+'/'+state+'/' + '/' + k])
            rxpos = np.array(data[day+'/'+state+'/' + '/'+ k + '/rxpos'])
            lat = []
            lon = []
            for sv in svlist:
                if (sv != 'time') and (sv != 'rxpos') and (int(sv[2:]) < 33):
                    if timelim is None:
                        lat.append(np.array(data[day+'/'+ state + '/' + k + '/' + sv + '/lat']))
                        lon.append(np.array(data[day+'/'+ state + '/' + k + '/' + sv + '/lon']))
                    elif (timelim is not None) and isinstance(timelim, list):
                        idt = np.where( (time >= timelim[0]) & (time <= timelim[1]))[0]
                        tmp = np.array(data[day+'/'+ state + '/' + k + '/' + sv + '/lat'])
                        lat.append(tmp[idt])
                        tmp = np.array(data[day+'/'+ state + '/' + k + '/' + sv + '/lon'])
                        lon.append(tmp[idt])
            if c == 0:
                ax,m = pyGpsUtils.plotGpsMapTrajectory(lat=lat, lon=lon, rx=np.array([rxpos[0],rxpos[1]]), #totalityc = [center_lat,center_lon],
                                                     totalityu = [north_lat,north_lon], totalityd = [south_lat,south_lon],
                                                     labels=None, ms=30,
                                                     timelim=None, latlim=[30, 42], 
                                                     parallels = [30,35,40], meridians=[-100,-85,-70],
                                                     lonlim=[-100, -70], center=[40, -80])
                c+=1
            else:
                ax,m = pyGpsUtils.plotGpsMapTrajectory(lat=lat, lon=lon, rx=np.array([rxpos[0],rxpos[1]]), #totalityc = [center_lat,center_lon],
                                                     #totalityu = [north_lat,north_lon], totalityd = [south_lat,south_lon],
                                                     labels=None, ms=30,
                                                     timelim=None, latlim=[30, 42], 
                                                     parallels = [30,35,40], meridians=[-100,-85,-70],
                                                     lonlim=[-100, -70], center=[40, -80], 
                                                     ax=ax, m=m)
    
    elif isinstance(state, list):
        c = 0
        for st in state:
            file = st+'list.h5'
            data = h5py.File(file, 'r')
            path = data[day+'/'+st+'/']
            for k in path.keys():
                time = np.array(data[day+'/'+st+'/' + '/'+ k +'/time'])
                svlist = np.array(data[day+'/'+st+'/' + '/' + k])
                rxpos = np.array(data[day+'/'+st+'/' + '/'+ k + '/rxpos'])
                lat = []
                lon = []
                for sv in svlist:
                    if (sv != 'time') and (sv != 'rxpos') and (int(sv[2:]) < 33):
                        if timelim is None:
                            lat.append(np.array(data[day+'/'+ st + '/' + k + '/' + sv + '/lat']))
                            lon.append(np.array(data[day+'/'+ st + '/' + k + '/' + sv + '/lon']))
                        elif (timelim is not None) and isinstance(timelim, list):
                            idt = np.where( (time >= timelim[0]) & (time <= timelim[1]))[0]
                            tmp = np.array(data[day+'/'+ st + '/' + k + '/' + sv + '/lat'])
                            lat.append(tmp[idt])
                            tmp = np.array(data[day+'/'+ st + '/' + k + '/' + sv + '/lon'])
                            lon.append(tmp[idt])
                if c == 0:
                    ax,m = pyGpsUtils.plotGpsMapTrajectory(lat=lat, lon=lon, #rx=np.array([rxpos[0],rxpos[1]]), #totalityc = [center_lat,center_lon],
                                                         totalityu = [north_lat,north_lon], totalityd = [south_lat,south_lon],
                                                         labels=None, ms=10,
                                                         timelim=None, latlim=[30, 42], 
                                                         parallels = [30,35,40], meridians=[-100,-85,-70],
                                                         lonlim=[-100, -70], center=[40, -80])
                    c+=1
                else:
                    ax,m = pyGpsUtils.plotGpsMapTrajectory(lat=lat, lon=lon, #rx=np.array([rxpos[0],rxpos[1]]), #totalityc = [center_lat,center_lon],
                                                         #totalityu = [north_lat,north_lon], totalityd = [south_lat,south_lon],
                                                         labels=None, ms=10,
                                                         timelim=None, latlim=[30, 42], 
                                                         parallels = [30,35,40], meridians=[-100,-85,-70],
                                                         lonlim=[-100, -70], center=[40, -80], 
                                                         ax=ax, m=m)
    
    else:
        print ('Something went wrong. Chack that state and hdffilenamelist are of the same type and length')
    
    data.close()
plotTrajectories(state=['tn', 'mo', 'ky', 'al', 'sc', 'ga', 'ar', 'ms', 'nc'], 
                 timelim=[datetime.datetime(2017,7,3,17,25,0),
                          datetime.datetime(2017,7,3,17,35,0)])