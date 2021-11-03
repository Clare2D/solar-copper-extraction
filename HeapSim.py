# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 11:20:36 2014

@author: cmurray
"""
import numpy as np
import matplotlib.pyplot as plt
from win32com import client
from time import sleep

class HeapSimProcessing():
    def __init__(self, cu_concentration,time,initial=None):
        self.initial=initial
        self.cu_concentration=cu_concentration
        self.time=time
        self.temps_top=None
        self.temps_base=None
        self.heapsim_input_array=np.empty([self.time+1,3])   
        self.cu_effluent=None
        self.heap_generation_results=np.empty([self.time,1])
        self.boiler_results=np.empty([self.time,2])

    def heapsim_inputs(self,initial_run,boiler_on,heap_mfr,t_req,results_store,temp_i=288.):
        if initial_run==0:
            for i in range(0,int(self.time)):
                self.heapsim_input_array[i,2]=results_store['pond2']['Pond results time'][i,0]-273
        else:
            for i in range(0,int(self.time)):
                self.heapsim_input_array[i,0]=(i+1)/24
                self.heapsim_input_array[i,1]=i+1   
                if boiler_on == True:
                    self.heapsim_input_array[i,2]=temp_i-273
                else:
                    self.heapsim_input_array[i,2]=temp_i-273
        self.heapsim_input_array[8760,0]=heap_mfr
        np.savetxt("P:\\600\\groupdrives\\Abteilungsleitung_STO\\Aktuell\\Studenten\\2013-murray\\02_work\\Thesis\\HeapSim\\heapsim_inputs.txt", self.heapsim_input_array)

    def heapsim_run(self):
        cl=client.Dispatch("Excel.Application")
        cl.Workbooks.Open(Filename="P:\\600\\groupdrives\\Abteilungsleitung_STO\\Aktuell\\Studenten\\2013-murray\\02_work\\Thesis\\HeapSim\\HeapSimCPY.xlsm",ReadOnly=1)
        cl.Application.Run("Add_all_events") 
        cl.Application.Run("Set_flow_rate") 
        cl.Application.Run("Write_EventFile")
        cl.Application.Run("Submit_input")        
        cl.Application.Run("Launch_Program")
        sleep(60)
        cl.Application.Run("Retrieve_Results")
        cl.Application.Run("Export_results_2")
        cl.Workbooks.Close()
        
    def convergence_check(self,conv_limit,results_store):
        dtemp_arr_hs=[]        
        pond2=np.copy(results_store['pond2']['Pond results time'][:,0])
        for i in range(len(pond2)):
            dtemp_arr_hs.append(self.heapsim_input_array[i,2]+273-pond2[i])
        self.dtemp_mean=np.mean(dtemp_arr_hs[:])
        self.dtemp_max=np.max(dtemp_arr_hs[:])
        self.dtemp_min=np.min(dtemp_arr_hs[:])
        if abs(self.dtemp_mean)>conv_limit:
            print "HeapSim convergence checker result", self.dtemp_mean, True 
            return True             # Must reiterate the calculation
        else: 
            print "HeapSim convergence checker result", self.dtemp_mean, False 
            return False 
            
    def boiler(self,t_req,results_store,boiler_on):
        temp_pond2=np.copy(results_store['pond2']['Pond results time'][:,0]  )
        for i in range(self.time):
            self.boiler_results[i,0]=(t_req-temp_pond2[i])
            if self.boiler_results[i,0]<=0:
                self.boiler_results[i,1]=0
            else:
                self.boiler_results[i,1]=self.initial.mfr_heap*4.184*(t_req-temp_pond2[i])/3600        # kWh
            if boiler_on != True:
                self.boiler_results[i,1]=0
        results_store['Boiler']=np.copy(self.boiler_results)

    def heapsim_results(self, results_store):
        headings = ['Cu Profiles','Fe(II) Profiles','Fe(III) Profiles','H2SO4','mesoFeO','ModFeO','extrFeO','mesoSuO','modSuO','extrSuO','X Cu oxide','X Limonite','X Bornite','X Idaite','X Covellite','X Pyrite','X Chalcopyrite','S Grade','Jarosite','Potential',' O2 Profiles','T Profiles','p=2 Profiles','pH Profiles','Fe total Effluent']
        d = np.genfromtxt('HeapSim_results.txt', delimiter="\t")
        a = []
        for i in range(np.shape(d)[0]):
            if np.isnan(d[i,0]):
                a.append(i)                
        for i in a:
            d=np.delete(d,i,0)
            a[:] = [x - 1 for x in a]  
        d=np.delete(d,[np.shape(d)[1]-2,np.shape(d)[1]-1], axis = 1)
        e=np.vsplit(d,24)
        results_store['HeapSim']={}
        for i in range(len(headings)-1):
            results_store['HeapSim'].update({headings[i]: e[i]})

        f=np.genfromtxt('HeapSim_results_overall.txt', delimiter='\t')
        f=np.delete(f,0,0)
        g=np.hsplit(f,13)
        headings_overall=['Time','XBr','XLi','Xbo','Xid','XCv','XPy','Xcpy','Sgrade','Jarosite','Tave','CuExtr','NAC']
        results_store['HeapSim_overall']={}
        for i in range(len(headings_overall)-1):
            results_store['HeapSim_overall'].update({headings_overall[i]: g[i]})

    def cu_extraction(self,hour,results_store):  
        hs_time=np.reshape(results_store['HeapSim_overall']['Time'],len(results_store['HeapSim_overall']['Time']))        
        if hs_time[-1]<365:
            hs_time=[i*24 for i in hs_time]
        hs_cu_rate=np.reshape(results_store['HeapSim_overall']['CuExtr'],len(results_store['HeapSim_overall']['CuExtr']))
        extr_rate=np.interp(hour,hs_time,hs_cu_rate)
        mass_ore=self.initial.dens_ore*self.initial.v_heap
        mass_cu=self.cu_concentration*mass_ore
        cu_output=extr_rate*mass_cu 
        return cu_output
        
    def heap_temp_base(self,results_store):
        temp_heap_array=results_store['HeapSim']['T Profiles'][-1,:]
        temp_heap_array=[j+273 for j in temp_heap_array]
        temp_heap_array=np.append(temp_heap_array,temp_heap_array[-1])
        temp_heap_array=np.insert(temp_heap_array,0,temp_heap_array[0])  
        hs_time=results_store['HeapSim']['T Profiles'][0,:]
        if hs_time[-1]<365:
            hs_time=[i*24 for i in hs_time]        
        hs_time=np.append(hs_time,365*24)
        hs_time=np.insert(hs_time,0,0)
        
        temp_base_array=np.interp(range(self.time),hs_time,temp_heap_array)
        results_store['HeapSim_overall']['temp_base']=temp_base_array
        return temp_base_array
        
    def heap_temp_top(self,results_store):
        temp_heap_array=results_store['HeapSim']['T Profiles'][2,:]
        temp_heap_array=[j+273 for j in temp_heap_array]
        temp_heap_array=np.append(temp_heap_array,temp_heap_array[-1])
        temp_heap_array=np.insert(temp_heap_array,0,temp_heap_array[0])  
        hs_time=results_store['HeapSim']['T Profiles'][0,:]
        if hs_time[-1]<365:
            hs_time=[i*24 for i in hs_time]        
        hs_time=np.append(hs_time,365*24)
        hs_time=np.insert(hs_time,0,0)
        
        temp_top_array=np.interp(range(self.time),hs_time,temp_heap_array)
        results_store['HeapSim_overall']['temp_top']=temp_top_array
        return temp_top_array 

    def heap_generation(self,results_store,mf_heap,cp_fluid,boiler_on,t_req):
        self.heap_generation_results=np.empty([self.time,1])
        temp_top_array=np.copy(results_store['pond2']['Pond results time'][:,0])
        if boiler_on == True:
            temp_top_array[:]=t_req
        temp_base_array=np.copy(results_store['HeapSim_overall']['temp_base'])
        for i in range(self.time):
            self.heap_generation_results[i]=(temp_base_array[i]-temp_top_array[i])*mf_heap*cp_fluid/(3600*1000)
        results_store['HeapSim_overall']['heap_generation']=np.copy(self.heap_generation_results)

    def plot_cu_extraction(self,results_store,collector_area):
        cu=[]
        for i in range(self.time):
            cu.append(self.cu_extraction(i,results_store))
        plt.figure(101)
        plt.plot(cu)
        plt.suptitle('Cu extraction over time')
        plt.xlim(0,self.time)
        plt.ylabel('Percentage of Cu Extracted')
        print "Collector Area:  %s m2" % collector_area
        print "HeapSim Results"
        print "Total Cu extraction %s kg; %s  percent" % (str(cu[-1]), str(results_store['HeapSim_overall']['CuExtr'][-1][0]*100))
        print '\n'       
    
    def plot_heap_temps(self,results_store):
        self.temps_top=self.heap_temp_top(results_store)
        self.temps_base=self.heap_temp_base(results_store)
        plt.figure(102)
        plt.plot(self.temps_top, label = 'Heap temp at top')
        plt.plot(self.temps_base, label = 'Heap temp at base')
        plt.xlim(0,self.time)
        plt.legend(loc=4)
        plt.suptitle('HeapSim Heap Average Temperatures vs time')
        
    def cu_in_effluent(self,hour,results_store):
        hs_time=results_store['HeapSim']['Cu Profiles'][0,:]
        cu_effluent_array=results_store['HeapSim']['T Profiles'][28,:]
        if hs_time[-1]<365:
            hs_time=[i*24 for i in hs_time]        
        self.cu_effluent=np.interp(hour,hs_time,cu_effluent_array)

        plt.figure(103)
        plt.plot(cu_effluent_array, label = 'Cu Effluent')
        plt.xlim(0,self.time)
        plt.legend(loc=4)
        plt.suptitle('Cu Effluent')        
        