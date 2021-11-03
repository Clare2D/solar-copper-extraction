# -*- coding: utf-8 -*-
"""
Created on Fri Aug 08 08:48:17 2014

@author: cmurray
"""

import numpy as np
import math as mt
import pickle
import time as time_module

class InitialCalcs():
    def __init__(self,lat=-23,longi=-68,dtgmt=-3,weather_file="El_tesoro_hour.txt"):     # tmax,tmin,tskmax,tskmin,lat,longi,stgmt,weather_file      
        #El_tesoro lat=-23 long=-68 dtgmt=-3
        self.tmax=303.
        self.tmin=273.
        self.tskmax=313.
        self.tskmin=213.
        self.lat=lat; 
        self.longi=longi
        self.dtgmt=dtgmt
        self.weather_file=weather_file
        self.weather_array = None
        self.parameter_array=None
        self.cases=None
        self.reloaded_results=None

    def sol_dec(self,dec):
        #sol_dec_ =23.45*mt.sin((360/365)*(dec-81))
        sol_dec_=0.
        return sol_dec_    
    def coz(self, decl, lha):
        coz_=mt.sin(mt.radians(self.lat))*mt.sin(mt.radians(decl))+mt.cos(mt.radians(self.lat))*mt.cos(mt.radians(decl))*mt.cos(mt.radians(lha))
        return coz_    
    def l_vap(self,t):
        h_fg_=2502535.259-212.56384*t
        return h_fg_    
    def vap_pres(self,t):
        # Vapour pressure as per the Antoine equation. Answer in pa
        a = 8.07131; b = 1730.63; c = 233.426
        vap_pres_=(10**(a-b/(t-273.15+c)))*133.322368
        return vap_pres_    
    def sat_pres(self,t):
        sat_pres_= (np.exp(77.345+0.0057*t-7235./t))/t**8.2
        return sat_pres_    
    def sh(self,t, pr):                # Saturated Humidity
        p=pr*(760./101325)
        a = 8.07131; b = 1730.63; c = 233.426
        p_=(0.6242*10.**(a-(b/(t-273.15+c))))/(p-10.**(a-(b/(t-273.15+c))))
        return p_    
    def sh_dif(self,t):            # derivative of Saturated Humidity
        a = 8.07131; b = 1730.63; c = 233.426
        p_dif_=1.43727361504688*10.0**(a + b/(-c + t - 273.15))*10.0**(a - b/(c + t - 273.15))*b/((-10.0**(a - b/(c + t - 273.15)) + 1000)**2*(c + t - 273.15)**2) - 1.43727361504688*10.0**(a + b/(-c + t - 273.15))*b/((-10.0**(a - b/(c + t - 273.15)) + 1000)*(-c + t - 273.15)**2)
        return p_dif_    
    def e_a(self,t):
        e_a_=0.674*0.007*(t-273.15)
        return e_a_      

    def calc_weather_array(self):
        i=0        # Weather:day,  hour,  hour(sum),  rain, ws, global_irr,  beam_irr,  diff_irr, DP_temp, RH,  Air_pr, air_temp,  Inf_temp,  sky_temp
        self.weather_array=np.genfromtxt(self.weather_file,  delimiter=",")
        a=np.zeros([8760,2])
        self.weather_array=np.hstack([self.weather_array,a])        
        self.weather_array[:,11]=[j+273.15 for j in self.weather_array[:,11]]
        self.weather_array[:,9]=[j/100 for j in self.weather_array[:,9]]
        self.weather_array[:,10]=[j*100 for j in self.weather_array[:,10]]
        for day in range(365):
            for hour in range(24):
                b_day=(360/365)*(day-81)
                eot=9.87*mt.sin(2*b_day)-7.53*mt.cos(b_day)-1.5*mt.sin(b_day)        
                tc=4*(self.longi-15*self.dtgmt)+eot
                lst=hour+tc/60
                hra=15*(lst-12)
                decl=self.sol_dec(day)
                coz1=self.coz(decl, hra)
                coza=self.coz(decl, 0)
                if coz1>0:
                    self.weather_array[i,12]=(self.tmin+(self.tmax-self.tmin)*(coz1/coza))
                    self.weather_array[i,13]=(self.tskmin+(self.tskmax-self.tskmin)*(coz1/coza)**0.25)
                else:
                    self.weather_array[i,12]=self.tmin
                    self.weather_array[i,13]=self.tskmin  
                i=i+1
        return self.weather_array

    def initial_properties(self,h_heap,g1,a_heap):
        self.v_heap=a_heap*h_heap        #m3
        self.dens_ore=1700.             # kg/m3
        self.mfr_heap=a_heap*g1    # kg/hr
        self.d_pond=10.
        self.a_pond=self.mfr_heap*24/(self.d_pond*1000)
        
    def temp_warning(self,t_pond1,t_pond2):
        if t_pond1<273:
            print "Pond 1 temp below 0"
        if t_pond2<273:
            print "Pond 2 temp below 0"
            
    def rk4(self,i,dt,temp_solve,t_pond,t_in,t_out):
        k1=temp_solve(i,t_pond,t_in,t_out)
        k2=temp_solve(i,t_pond+(dt/2)*k1,t_in,t_out)
        k3=temp_solve(i,t_pond+(dt/2)*k2,t_in,t_out)
        k4=temp_solve(i,t_pond+dt*k3,t_in,t_out)
        sol=t_pond+(dt/6)*(k1+2*k2+2*k3+k4)
        return sol
    
    def input_definition(self,para_results_store,case,boiler_on,pond_cover,cu_concentration,pyr_concentration,g1,h_heap):
        input_array=[]        
        input_array.append('Case:'+str(case))
        input_array.append('Cu Concentration:'+str(cu_concentration))
        input_array.append('Pyrite Concentration:'+str(pyr_concentration))
        input_array.append('Heap Flow Rate:'+str(g1))
        input_array.append('Pond Area:'+str(self.a_pond))
        input_array.append('Heap Height:'+str(h_heap))
        if boiler_on==True:
            input_array.append('Boiler On')
        else:
            input_array.append('Boiler Off')
        if pond_cover==True:
            input_array.append('Ponds Covered')
        else:
            input_array.append('Ponds Uncovered')
        para_results_store['Inputs']=input_array 
    
    def pickler_dump(self,para_results_store,file_name_input):
        today=time_module.strftime('%Y%m%d')
        name=file_name_input+today
        with open(name, 'wb') as handle:
            pickle.dump(para_results_store, handle)
            
    def pickler_load(self,name):
        self.reloaded_results = pickle.load( open(name, "rb" ) )

