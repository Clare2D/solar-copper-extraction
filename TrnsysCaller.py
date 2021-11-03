# -*- coding: utf-8 -*-
"""
Created on Fri Aug 08 11:44:56 2014

@author: cmurray
"""

# Trnsys Caller Script
# writes an input file then runs TRNSYS 
import numpy as np
import os


class TrnsysCaller():
    def __init__(self,time,dt):
        self.time=time
        self.dt=dt
        self.pyth_t=None
        self.trns_in=None
        self.trns_in_time=np.empty([self.time,11])
        self.dtemp_mean=None
        self.dtemp_max=None
        self.dtemp_min=None
        self.total_surface_irradiation=None
        self.total_col_gain=None
        self.total_HX_gain=None
        self.total_pump_elec_req=None
        self.consolidater_checker={}
        self.run=0
    
    def write_trnsys_input_file(self,initial_run,results_store,temp_i=293.):
        if initial_run==0:
            self.pyth_t=np.copy(results_store['pond2']['Pond results'][:,0])
        else:
            self.pyth_t=np.array([temp_i for x in range(int(self.time/self.dt))]) 
        np.savetxt("pyth_temp.txt", self.pyth_t)
        
    def edit_deck_file(self,area_collector):
        a='area_col='+str(area_collector)
        f=open('Solar.dck','r')
        s=f.readlines()
        s[41]=a + '\n'
        f.close()
        f=open('Solar.dck','w')
        f.writelines(s)
        f.close()
        
    def call_trnsys(self,on_):
        if on_==True:
            wd=os.getcwd()
            os.system("C:\TRNSYS17\Exe\TRNExe.exe " + wd + "\Solar.dck /n")
            self.trns_in=np.genfromtxt("trnsys_results_temp.txt", delimiter=",",skip_header=1, usecols=(0,1,2,3,4,5,6,7,8,9))
            self.trns_in=self.trns_in[:-1]
        if on_==False:
            self.trns_in=np.zeros([self.time/self.dt,10])
        
    def convergence_check(self,conv_limit,pond2):
        dtemp_arr=[]        
        for i in range(len(pond2)):
            dtemp_arr.append(self.trns_in[i,8]-pond2[i,0])
        self.dtemp_mean=np.mean(dtemp_arr[:])
        self.dtemp_max=np.max(dtemp_arr[:])
        self.dtemp_min=np.min(dtemp_arr[:])
        if abs(self.dtemp_mean)>conv_limit:
            print "TRNSYS convergence checker result", self.dtemp_mean, True
            return True             
        else: 
            print "TRNSYS convergence checker result", self.dtemp_mean, False
            return False  

    def condense_results(self,results_store):        
        for j in range(self.time):
            self.trns_in_time[j,0]=j
            for k in [1,3,4,5,6,7,8,9]:
                self.trns_in_time[j,k]=np.mean(self.trns_in[int(j/self.dt):int((j+1)/self.dt),k])
            for k in [2]:
                self.trns_in_time[j,k]=np.sum(self.trns_in[int(j/self.dt):int((j+1)/self.dt),k]) 
        self.total_surface_irradiation=np.sum(self.trns_in_time[:,9])
        self.total_col_gain=np.sum(self.trns_in_time[:,6])
        self.total_HX_gain=np.sum(self.trns_in_time[:,7])
        self.total_pump_elec_req=np.sum(self.trns_in_time[:,[3,4]])
        results_store['TRNSYS']=self.trns_in_time
        
      