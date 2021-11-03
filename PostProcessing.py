# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 14:43:23 2014

@author: cmurray
"""

import start
import results
from matplotlib.pylab import close
import numpy as np

close('all')

time=8760
dt=0.25
h_heap=6.
g1=5.
a_heap=200000.

collector_area_array=[0,10000,20000,50000,80000,100000,150000,200000]
cases=[]

result_names=[]
for i in range(1,13):
    cases.append('Case'+str(i))
    result_names.append('Case_'+str(i)+'_20141106')

initial = start.InitialCalcs()
initial.initial_properties(h_heap,g1,a_heap)        # CHECK!!, g1 is wrong
initial.calc_weather_array()
res= results.ShowResults(time, dt,a_heap, initial = initial) 
summary_array=[]
case=0
i=0
load_results=True

if load_results == True:
    all_results={}
    for name in result_names:
        initial.pickler_load(name)
        all_results[cases[i]]=initial.reloaded_results
        i+=1        
economic_summary=np.zeros([len(collector_area_array)*5,0])

# All Cases
for case in cases:
    count_v = 0
    res.parametrisation_summary(all_results[case],collector_area_array,case)
    summary_array.extend(all_results[case]['Summary'])
#    res.plot_cu_extraction(all_results[case],collector_area_array,case,1)
    
    economic_summary_vertical=np.zeros([0,4])
    for collector_area in collector_area_array:
        res.economic_inputs(all_results[case],collector_area)
        economic_summary_vertical=np.vstack([economic_summary_vertical,all_results[case][collector_area]['Economic Summary']])

    economic_summary=np.hstack([economic_summary,economic_summary_vertical])    
    
res.export_speed_extraction(all_results,'Case2',collector_area_array)
        
np.savetxt('Economic_Summary.txt',economic_summary,delimiter=',')
np.savetxt('All_results_Parametrisation Summary.txt',summary_array,delimiter=',') 

# Separate Cases - select as required
case_name='Case1'                                                  # Change name as required
collector_area=20000                                            # Change as required
res.daily_heat_profile(100,all_results[case_name][collector_area])
res.pie_chart_heat_loss(all_results[case_name])
res.pie_chat_pond2(all_results[case_name])
res.plot_results(all_results[case_name][50000],0)
res.cover_comparison(all_results)
res.plot_pond2_temps(all_results,collector_area_array)


#for case in ['Case1','Case2','Case3','Case4']:
#    res.plot_cu_extraction(all_results[case],collector_area_array,case,20)

res.export_case(all_results,4,0)
res.export_case(all_results,3,50000)
res.export_diesel_use(all_results,collector_area_array)
res.plot_results(all_results[case_name][collector_area],collector_area)       # Plots all the results for a specific case and area
# res.print_results(all_results[case_name])                     # Plots all the results for a specific case 
# res.res.plot_pond2_temps(all_results[case_name],collector_area_array,case_name)   # Plots all the pond temperatures for a specific case over a year


# For Additional TRNSYS runs

#t_pond2=288
#import TrnsysCaller
#trn = TrnsysCaller.TrnsysCaller(time,dt)
#trn.write_trnsys_input_file(0,all_results['Case3'][200000],temp_i=t_pond2)
#trn.call_trnsys(1) 

