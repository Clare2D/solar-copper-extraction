# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 09:20:27 2014

@author: cmurray
"""

import start
import TrnsysCaller
import HeatCalcs
import HeapSim
from matplotlib.pyplot import close

close('all')

dt = 0.25
time = 8760
h_heap=6.
cu_concentration = 0.005     # 0.5%
pyr_concentration = 0.02     # 2%
a_heap=200000.               # m2
collector_area_array=[0,10000,20000,50000,80000,100000,150000,200000]
t_initial = 288
t_pond1=t_pond2=t_heap_base=t_heap_top=t_initial
case=8      

for boiler_on in [False,True]:
    for pond_cover in [True,False]:
        for g1 in [10.]:
            if g1==5.:
                t_req=50.+273
            if g1==7.:
                t_req=55.+273
            if g1==12.:
                t_req=55.+273
            
            case=case+1
            para_results_store={}
            initial = start.InitialCalcs()
            initial.calc_weather_array()
            initial.initial_properties(h_heap,g1,a_heap)        
            initial.input_definition(para_results_store,case,boiler_on,pond_cover,cu_concentration,pyr_concentration,g1,h_heap)
            for collector_area in collector_area_array:
                results_store = {}

                initial_run = 1 
                # Initial TRNSYS Run
                trn = TrnsysCaller.TrnsysCaller(time,dt)
                if collector_area==0:
                    solar_on=False
                    trn.call_trnsys(0)
                else:
                    solar_on=True                
                    trn.edit_deck_file(collector_area)                                          # Sets the collector area
                    trn.write_trnsys_input_file(initial_run,results_store,temp_i=t_initial)     # Creates the file to export to Trnsys
                    trn.call_trnsys(1)                                                          # Creates the file from Trnsys  

                # Initial HeapSim Run
                heapsim = HeapSim.HeapSimProcessing(cu_concentration,time,initial=initial)
                if boiler_on == True:
                    t_hs=t_req
                else:
                    t_hs=t_initial
                heapsim.heapsim_inputs(initial_run,boiler_on,g1,t_req,results_store,temp_i=t_hs)
                heapsim.heapsim_run()
                heapsim.heapsim_results(results_store)
                temps_heap_base = heapsim.heap_temp_base(results_store)
                temps_heap_top = heapsim.heap_temp_top(results_store)                
                
                # Initial Pond instances
                pond1 = HeatCalcs.Pond(time, dt, initial.mfr_heap, 0, pond_cover, results_store, initial = initial, trn = trn)
                if solar_on == False:
                    pond2 = HeatCalcs.Pond(time, dt, initial.mfr_heap, 0, pond_cover, results_store, initial = initial, trn = trn)
                else:
                    pond2 = HeatCalcs.Pond(time, dt, initial.mfr_heap, 1, pond_cover, results_store, initial = initial, trn = trn)
                    
                # Energy Calculations
                trn_convergence_checker = True
                heapsim_convergence_checker = True
                while ((trn_convergence_checker == True or heapsim_convergence_checker == True)):
                    for i in range(int(time/dt)):
                        t_pond1_new = pond1.p_calculations(i,t_pond1,t_heap_base,t_pond2)
                        t_pond2_new = pond2.p_calculations(i,t_pond2,t_pond1,t_heap_top)
                    
                        t_heap_base = temps_heap_base[int(i*dt)]
                        t_heap_top = temps_heap_top[int(i*dt)]
                    
                        t_pond1 = t_pond1_new
                        t_pond2 = t_pond2_new
                
                    pond1.condense_results('pond1')
                    pond2.condense_results('pond2')
                    
                    # Check for Convergence: TRNSYS
                    if solar_on == False:
                        trn_convergence_checker = False
                    else:
                        trn_convergence_checker = trn.convergence_check(0.5,pond2.results_pond)    
                        if trn_convergence_checker == True:
                            t_pond1 = t_pond2 = t_heap_base = t_heap_top = t_initial 
                            trn.write_trnsys_input_file(0,results_store)      # Creates the file to export to Trnsys
                            trn.call_trnsys(1)
                            pond1 = HeatCalcs.Pond(time, dt,initial.mfr_heap, 0,pond_cover,results_store, initial = initial, trn = trn) 
                            pond2 = HeatCalcs.Pond(time, dt,initial.mfr_heap, solar_on,pond_cover,results_store, initial = initial, trn = trn)   
                    
                    # Check for Convergence: HeapSim
                    if boiler_on == True:
                        heapsim_convergence_checker = False
                    else:
                        heapsim_convergence_checker = heapsim.convergence_check(0.5,results_store)
                        if heapsim_convergence_checker == True:
                            heapsim.heapsim_inputs(0,boiler_on,g1,t_req,results_store)
                            heapsim.heapsim_run()
                            heapsim.heapsim_results(results_store)
                            temps_heap_base = heapsim.heap_temp_base(results_store)
                            temps_heap_top = heapsim.heap_temp_top(results_store)
                            
                    # Calculate heap generation and boiler requirements                    
                    heapsim.heap_generation(results_store,initial.mfr_heap,pond2.cp_fluid,boiler_on,t_req)
                    heapsim.boiler(t_req,results_store,boiler_on)                       
                    t_pond1 = t_pond2 = t_heap_base = t_heap_top = t_initial
                    
                trn.condense_results(results_store)    
                para_results_store[collector_area] = results_store
                
            initial.pickler_dump(para_results_store,'FR10_'+str(case)+'_')       # Saves parametrisation results for another day :)