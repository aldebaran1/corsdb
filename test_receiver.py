#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 14:27:05 2017

@author: Sebastijan Mrak <smrak@gmail.com>
"""

from pandas import read_hdf
import pandas
import numpy as np
import datetime
import os
import glob
import yaml
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from gsit import pyGps

obsfolder = '/home/smrak/sharedrive/cors/'
navfolder = '/home/smrak/sharedrive/cors/nav/'

# Input VARIABLES
#day = 185
#el_mask = 40
#state = 'mo'
#station = ''

def singleStation(day, el_mask, state, station=''):
    #Find HDF5 filename
    if station == '':
        wlstr ='*'+ str(day) + '*.h5'
    else:
        wlstr =state + station + str(day) + '*.h5'
    filestr = os.path.join(obsfolder+state+'/'+str(day)+'/', wlstr)
    flistHDF = glob.glob(filestr)
    #Find NAV filename
    wlstr ='*' + str(day) + '*.17n'
    filestr = os.path.join(navfolder, wlstr)
    flistNAV = glob.glob(filestr)
    #Find YAML filename
    if station == '':
        wlstr ='*'+ str(day) + '*.yaml'
    else:
        wlstr =state + station + str(day) + '*.yaml'
    filestr = os.path.join(obsfolder+state+'/'+str(day)+'/', wlstr)
    flistYML = glob.glob(filestr)
    
    #filenames
    hdffn = flistHDF[0]
    navfn = flistNAV[0]
    ymlfn = flistYML[0]
    
    # Processing per station
    
    # YAML import header
    stream = yaml.load(open(ymlfn, 'r'))
    rx_xyz = stream.get('APPROX POSITION XYZ')
    
    # HDF Observations
    data = read_hdf(hdffn)
    obstimes = np.array((data.major_axis))
    obstimes = pandas.to_datetime(obstimes) - datetime.timedelta(seconds=18)
    dumb = data['L1', :,1, 'data']
    svlist = dumb.axes[0]
    
    fig1 = plt.figure(figsize=(12,12))
    formatter = mdates.DateFormatter('%H:%M')
    ax1 = fig1.add_subplot(311)
    #fig2 = plt.figure(figsize=(12,4))
    ax2 = fig1.add_subplot(312, sharex=ax1)
    #fig3 = plt.figure(figsize=(12,4))
    ax3 = fig1.add_subplot(313, sharex=ax1)
    for sv in svlist:
        # GPS only svnum <=32
        if sv <= 32: 
            C1 = np.array(data['C1', sv, :, 'data'])
            C2 = np.array(data['P2', sv, :, 'data'])
            L1 = np.array(data['L1', sv, :, 'data'])
            L2 = np.array(data['L2', sv, :, 'data'])
            aer = pyGps.getIonosphericPiercingPoints(rx_xyz, sv, obstimes, 120, navfn, cs='aer')
            #filter by Elevation angle
            idel = np.where((aer[1] > el_mask))[0]
            t = obstimes[idel]
            #Get TEC
            # Calc only if there is more than 30min of data
            if (np.isfinite(L1[idel]).shape[0]>1000):
                tec, intervals = pyGps.getPhaseCorrTEC(L1[idel], L2[idel], C1[idel], C2[idel], intervals=True)
                l = []
                for ran in intervals:
                    l.append(ran[1]-ran[0])
                idl = np.where(np.array(l) < 1000)[0]
    #            print (idl)
                if len(idl) > 0:
                    idLL = intervals[idl[0]]
                    tec[idLL[0]:idLL[1]] = np.nan
                # Detrend data without NaNs
                if np.sum(np.isfinite(tec)) > 100:
                    idf = np.isfinite(tec)
                    tec_recovery = np.nan * np.zeros(tec.shape[0])
#                    techpf_recovery = np.nan * np.zeros(tec.shape[0])
        
                    diff_tec = pyGps.phaseDetrend(tec[idf], order=3)
    #                sigma_phi = pyGps.phaseScintillation(C1[idel], polyfit_order=3, skip=40)
                    tec_recovery[idf] = diff_tec
                    
                    # Plottings
                    ax2.plot(t, tec_recovery, label='sv'+str(sv))
                    ax3.plot(t[:-1], np.diff(tec), label='sv'+str(sv))
                    ax1.plot(t, C1[idel], label='sv'+str(sv))
    ax3.set_ylim([-1,1])
    ax1.set_xlim([obstimes[0], obstimes[-1]])
    ax2.set_ylabel('Detr. tec')
    ax3.set_ylabel('Delta tec')
    ax1.set_ylabel('C1')
    ax3.set_xlabel('time [UTC]')
    ax1.set_title('Missouri, day '+str(day)+' Rx: ' + hdffn[-11:-7])
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    #ax3.legend(bbox_to_anchor=(1.1, 1.1))
    ax1.xaxis.set(major_formatter = formatter)
    ax2.xaxis.set(major_formatter = formatter)
    ax3.xaxis.set(major_formatter = formatter)
    plt.savefig('/home/smrak/Documents/eclipse/plots/mo/'+hdffn[-11:-3]+'.png', dpi=300)
    
def runSateListRaw(day, el_mask, state):
    #Find HDF5 filename
    wlstr ='*' + str(day) + '*.h5'
    filestr = os.path.join(obsfolder+state+'/'+str(day)+'/', wlstr)
    flistHDF = glob.glob(filestr)
    #Find NAV filename
    wlstr ='*' + str(day) + '*.17n'
    filestr = os.path.join(navfolder, wlstr)
    flistNAV = glob.glob(filestr)
    #Find YAML filenamE
    wlstr ='*'+ str(day) + '*.yaml'
    filestr = os.path.join(obsfolder+state+'/'+str(day)+'/', wlstr)
    flistYML = glob.glob(filestr)
    
    for i in range(len(flistHDF)):
        #filenames
        hdffn = flistHDF[i]
        navfn = flistNAV[0]
        ymlfn = flistYML[i]
        
        # Processing per station
        
        # YAML import header
        stream = yaml.load(open(ymlfn, 'r'))
        rx_xyz = stream.get('APPROX POSITION XYZ')
        
        # HDF Observations
        data = read_hdf(hdffn)
        obstimes = np.array((data.major_axis))
        obstimes = pandas.to_datetime(obstimes) - datetime.timedelta(seconds=18)
        dumb = data['L1', :,1, 'data']
        svlist = dumb.axes[0]
        
        fig1 = plt.figure(figsize=(12,12))
        formatter = mdates.DateFormatter('%H:%M')
        ax1 = fig1.add_subplot(411)
        #fig2 = plt.figure(figsize=(12,4))
        ax2 = fig1.add_subplot(412, sharex=ax1)
        #fig3 = plt.figure(figsize=(12,4))
        ax3 = fig1.add_subplot(413, sharex=ax1)
        ax4 = fig1.add_subplot(414, sharex=ax1)
        for sv in svlist:
            # GPS only svnum <=32
            if sv <= 32: 
                C1 = np.array(data['C1', sv, :, 'data'])
                C2 = np.array(data['P2', sv, :, 'data'])
                L1 = np.array(data['L1', sv, :, 'data'])
                L2 = np.array(data['L2', sv, :, 'data'])
                aer = pyGps.getIonosphericPiercingPoints(rx_xyz, sv, obstimes, 120, navfn, cs='aer')
                #filter by Elevation angle
                idel = np.where((aer[1] > el_mask))[0]
                t = obstimes[idel]
                #Get TEC
                ax1.plot(t, C1[idel], label='sv'+str(sv))
                ax2.plot(t, C2[idel], label='sv'+str(sv))
                ax3.plot(t, L1[idel], label='sv'+str(sv))
                ax4.plot(t, L2[idel], label='sv'+str(sv))
                
        ax1.set_xlim([obstimes[0], obstimes[-1]])
        ax1.set_ylabel('C1 [m]')
        ax2.set_ylabel('P2 [m]')
        ax3.set_ylabel('L1 [cycle]')
        ax4.set_ylabel('L2 [cycle]')
        ax3.set_xlabel('time [UTC]')
        ax1.set_title('NC, day '+str(day)+' Rx: ' + hdffn[-11:-7])
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax3.get_xticklabels(), visible=False)
        #ax3.legend(bbox_to_anchor=(1.1, 1.1))
#        ax1.xaxis.set(major_formatter = formatter)
#        ax2.xaxis.set(major_formatter = formatter)
        ax4.xaxis.set(major_formatter = formatter)
        plt.savefig('/home/smrak/Documents/eclipse/plots/'+state+'/'+hdffn[-11:-3]+'.png', dpi=300)
    
def runStateList(day, el_mask, state):
    #Find HDF5 filename
    wlstr ='*' + str(day) + '*.h5'
    filestr = os.path.join(obsfolder+state+'/'+str(day)+'/', wlstr)
    flistHDF = glob.glob(filestr)
    #Find NAV filename
    wlstr ='*' + str(day) + '*.17n'
    filestr = os.path.join(navfolder, wlstr)
    flistNAV = glob.glob(filestr)
    #Find YAML filenamE
    wlstr ='*'+ str(day) + '*.yaml'
    filestr = os.path.join(obsfolder+state+'/'+str(day)+'/', wlstr)
    flistYML = glob.glob(filestr)
    
    for i in range(len(flistHDF)):
        #filenames
        hdffn = flistHDF[i]
        navfn = flistNAV[0]
        ymlfn = flistYML[i]
        
        # Processing per station
        
        # YAML import header
        stream = yaml.load(open(ymlfn, 'r'))
        rx_xyz = stream.get('APPROX POSITION XYZ')
        
        # HDF Observations
        data = read_hdf(hdffn)
        obstimes = np.array((data.major_axis))
        obstimes = pandas.to_datetime(obstimes) - datetime.timedelta(seconds=18)
        dumb = data['L1', :,1, 'data']
        svlist = dumb.axes[0]
        
        fig1 = plt.figure(figsize=(12,12))
        formatter = mdates.DateFormatter('%H:%M')
        ax1 = fig1.add_subplot(311)
        #fig2 = plt.figure(figsize=(12,4))
        ax2 = fig1.add_subplot(312, sharex=ax1)
        #fig3 = plt.figure(figsize=(12,4))
        ax3 = fig1.add_subplot(313, sharex=ax1)
        for sv in svlist:
            # GPS only svnum <=32
            if sv <= 32: 
                C1 = np.array(data['C1', sv, :, 'data'])
                C2 = np.array(data['P2', sv, :, 'data'])
                L1 = np.array(data['L1', sv, :, 'data'])
                L2 = np.array(data['L2', sv, :, 'data'])
                aer = pyGps.getIonosphericPiercingPoints(rx_xyz, sv, obstimes, 120, navfn, cs='aer')
                #filter by Elevation angle
                idel = np.where((aer[1] > el_mask))[0]
                t = obstimes[idel]
                #Get TEC
                # Calc only if there is more than 30min of data
                if (np.isfinite(L1[idel]).shape[0]>1000):
                    tec, intervals = pyGps.getPhaseCorrTEC(L1[idel], L2[idel], C1[idel], C2[idel], intervals=True)
                    l = []
                    for ran in intervals:
                        l.append(ran[1]-ran[0])
                    idl = np.where(np.array(l) < 1000)[0]
        #            print (idl)
                    if len(idl) > 0:
                        idLL = intervals[idl[0]]
                        tec[idLL[0]:idLL[1]] = np.nan
                    # Detrend data without NaNs
                    if np.sum(np.isfinite(tec)) > 100:
                        idf = np.isfinite(tec)
                        tec_recovery = np.nan * np.zeros(tec.shape[0])
#                        techpf_recovery = np.nan * np.zeros(tec.shape[0])
            
                        diff_tec = pyGps.phaseDetrend(tec[idf], order=3)
        #                sigma_phi = pyGps.phaseScintillation(C1[idel], polyfit_order=3, skip=40)
                        tec_recovery[idf] = diff_tec
                        
                        # Plottings
                        ax2.plot(t, tec_recovery, label='sv'+str(sv))
                        ax3.plot(t[:-1], np.diff(tec), label='sv'+str(sv))
                        ax1.plot(t, C1[idel], label='sv'+str(sv))
        ax3.set_ylim([-1,1])
        ax1.set_xlim([obstimes[0], obstimes[-1]])
        ax2.set_ylabel('Detr. tec')
        ax3.set_ylabel('Delta tec')
        ax1.set_ylabel('C1')
        ax3.set_xlabel('time [UTC]')
        ax1.set_title('NC, day '+str(day)+' Rx: ' + hdffn[-11:-7])
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        #ax3.legend(bbox_to_anchor=(1.1, 1.1))
        ax1.xaxis.set(major_formatter = formatter)
        ax2.xaxis.set(major_formatter = formatter)
        ax3.xaxis.set(major_formatter = formatter)
        plt.savefig('/home/smrak/Documents/eclipse/plots/mo/'+hdffn[-11:-3]+'.png', dpi=300)
        
        
#runStateList(184, 40, 'nc')
runSateListRaw(184, 40, 'tn')