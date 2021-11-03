# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 09:27:25 2014

@author: cmurray
"""

import numpy as np

class Pond():
    def __init__(self,time,dt,mf_heap,solar_on,pond_cover,results_store,initial=None,trn=None):
        self.time=time        
        self.dt=dt
        self.mf_heap=mf_heap/3600   # kg/s
        self.solar_on=solar_on      # 1 for pond2, 0 for pond1
        self.pond_cover=pond_cover
        self.cp_fluid=4184.         # J/kgK
        self.cp_air=1000.           # J/kgK
        self.cp_vap=1840.           # J/kgK
        self.dens_h20=1000.         # kg/m3
        self.e_h20=0.96             # water surface emissivity
        self.ab_h20=0.94            # absorbtivity pond water
        self.r_h20=0.03             # reflectivity pond water
        self.a_pond=initial.a_pond
        self.stbc=5.67*10**-8
        self.d_pond=initial.d_pond                 # m
        self.v_pond=self.a_pond*self.d_pond     # m3
        self.results_store=results_store
        self.initial_calcs = initial
        self.t_air=initial.weather_array[:,11]
        self.ws=initial.weather_array[:,4]
        self.q0=initial.weather_array[:,5]
        self.trn = trn
        self.m_col=self.trn.trns_in[:,2]
        self.t_hx_out=self.trn.trns_in[:,1]
        self.results_pond=np.empty([self.time/self.dt,7])
        self.results_pond_time=np.empty([self.time,7])
        self.heat_difference_array=np.empty([self.time/self.dt,1])  

    def p_conv(self,i,t_pond):
        h_pond=2.8+3.*self.ws[i*self.dt]  
        cover_factor=1
        if self.pond_cover == True:
            cover_factor=0.25
        conv=cover_factor*h_pond*(self.t_air[i*self.dt]-t_pond)/1000
        self.results_pond[i,1] = conv*self.a_pond
        return conv*self.a_pond

    def p_evap(self,i,t_pond):
        ws_4m=self.ws[i*self.dt]*np.log(4.)/np.log(10.)
        m_evap=(0.068+0.13*ws_4m)*(self.initial_calcs.sat_pres(self.t_air[i*self.dt])-self.initial_calcs.vap_pres(t_pond))*1.344*10**-7
        evap=(1-self.pond_cover)*m_evap*(2502535.269-212.56*(self.t_air[i*self.dt]-273.15))/1000
        if self.pond_cover == True:
            evap=0
        self.results_pond[i,2] = evap*self.a_pond
        return evap*self.a_pond

    def p_rad(self,i,t_pond):
        if self.pond_cover == True:
            self.ab_h20=0.93
            self.r_h20=0.03
            self.e_h20=0.92
        rad=(self.ab_h20*self.q0[i*self.dt]+((1-self.r_h20)*self.initial_calcs.e_a(self.t_air[i*self.dt])*self.stbc*self.t_air[i*self.dt]**4)-self.e_h20*self.stbc*t_pond**4)/1000
        self.results_pond[i,3] = rad*self.a_pond
        return rad*self.a_pond

    def p_flow(self,i,t_in,t_out):
        flow=(self.mf_heap*self.cp_fluid*(t_in-t_out)/1000)
        self.results_pond[i,4] = flow
        return flow

    def p_solar(self,i,t_pond):
        if self.solar_on == True:
            solar=self.solar_on*self.m_col[i]*self.cp_fluid*(self.t_hx_out[i]-t_pond)/1000
        else:
            solar=0
        self.results_pond[i,5] = solar
        return solar

    def p_tot(self,i,t_pond,t_in,t_out):
        tot=self.p_conv(i,t_pond)+self.p_rad(i,t_pond)+self.p_solar(i,t_pond)+self.p_flow(i,t_in,t_pond)+self.p_evap(i,t_pond)
        self.results_pond[i,6] = tot
        return tot
        
    def temp_tot(self,i,t_pond,t_in,t_out):
        temp=(1/(self.dens_h20*self.cp_fluid*self.v_pond))*self.p_tot(i,t_pond,t_in,t_out)*1000*3600
        return temp

    def p_calculations(self,i,t_pond,t_in,t_out):
        t_pond=self.initial_calcs.rk4(i,self.dt,self.temp_tot,t_pond,t_in,t_out)    
        self.results_pond[i,0]=t_pond
        return t_pond 
        
    def condense_results(self,pond_name):        
        for j in range(self.time):
            for k in range(7):
                self.results_pond_time[j,k]=np.mean(self.results_pond[int(j/self.dt):int((j+1)/self.dt),k]) 
        self.results_store[pond_name]={"Pond results":self.results_pond,"Pond results time":self.results_pond_time}
        


        
    
      
