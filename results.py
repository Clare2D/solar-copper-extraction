# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 11:15:52 2014

@author: cmurray
"""
import matplotlib.pyplot as plt
import numpy as np
import time as time_module
from stackedBarGraph import StackedBarGrapher


class ShowResults():
    def __init__(self, simtime, dt,a_heap, initial=None):
        self.simtime=simtime
        self.today=time_module.strftime('%Y%m%d')
        self.dt=dt
        self.a_heap=a_heap
        self.initial=initial
        self.a_pond=initial.a_pond
        self.results_q=None
        self.temp_table=None
        self.heat_table=None
        self.solar_table=None
        self.case_results=None
        self.reloaded_results=None
        
    def parametrisation_summary(self,para_results_store,collector_area_array,case): 
        self.pond2_temp_average=[]
        self.pond1_temp_average=[]
        self.utilisation_factor=[]
        self.cu_output_array=[]
        self.solar_energy=[]
        self.heap_generation_array=[]
        self.pond2_temps_array=np.empty([self.simtime,len(collector_area_array)])
        self.pond1_temps_array=np.empty([self.simtime,len(collector_area_array)])
        self.pond2_heat_results=np.empty([6,len(collector_area_array)])
        self.pond1_heat_results=np.empty([6,len(collector_area_array)])
        self.boiler_energy_used=[]
        total_surface_irradiation_array=[]
        summary_array=np.empty([20,len(collector_area_array)])
        i=0
        for collector_area in collector_area_array:
            self.pond2_temps_array[:,i]=np.copy(para_results_store[collector_area]['pond2']['Pond results time'][:,0])
            self.pond1_temps_array[:,i]=np.copy(para_results_store[collector_area]['pond1']['Pond results time'][:,0])
            self.pond2_temp_average.append(np.copy(np.mean(self.pond2_temps_array[:,i])))
            self.pond1_temp_average.append(np.copy(np.mean(self.pond1_temps_array[:,i])))
            self.heap_generation_array.append(np.copy(np.sum(para_results_store[collector_area]['HeapSim_overall']['heap_generation'])))
            self.cu_output_array.append(np.copy(para_results_store[collector_area]['HeapSim_overall']['CuExtr'][-1][0]*100))
            self.boiler_energy_used.append(np.copy(np.sum(para_results_store[collector_area]['Boiler'][:,1])))            
            
            self.solar_energy.append(np.sum(para_results_store[collector_area]['pond2']['Pond results time'][:,5]))
            total_surface_irradiation_array.append(np.sum(para_results_store[collector_area]['TRNSYS'][:,9]))
            
            if collector_area == 0:
                self.utilisation_factor.append(0)
            else:
                self.utilisation_factor.append((np.sum(para_results_store[collector_area]['pond2']['Pond results time'][:,5]))/total_surface_irradiation_array[i])

            pond2_heat_results_area=[]
            pond1_heat_results_area=[]            
            for j in range(1,7):
                pond2_heat_results_area.append(np.sum(para_results_store[collector_area]['pond2']['Pond results time'][:,j]))            
            for j in range(1,7):
                pond1_heat_results_area.append(np.sum(para_results_store[collector_area]['pond1']['Pond results time'][:,j]))                            
            self.pond2_heat_results[:,i]=pond2_heat_results_area
            self.pond1_heat_results[:,i]=pond1_heat_results_area
            
            if collector_area == 0:
                self.solar_energy[0]=0
                self.pond2_heat_results[4,0]=0
            
            i=i+1 
        summary_array[0,:]=collector_area_array
        summary_array[1,:]=np.copy(self.pond2_temp_average)
        summary_array[2,:]=np.copy(self.cu_output_array)
        summary_array[3,:]=np.copy(self.solar_energy)
        summary_array[4,:]=total_surface_irradiation_array
        summary_array[5,:]=np.copy(self.utilisation_factor)
        summary_array[6:12,:]=np.copy(self.pond2_heat_results)
        summary_array[12,:]=np.copy(self.heap_generation_array)
        summary_array[13:19,:]=np.copy(self.pond1_heat_results)
        summary_array[19,:]=np.copy(self.boiler_energy_used)
        
        para_results_store['Summary']=summary_array  
        
    def export_speed_extraction(self,all_results,case,collector_area_array):
        cu_extraction=[]
        cpy_extraction=[]
        for ca in collector_area_array:
            a=all_results[case][ca]['HeapSim_overall']['CuExtr']
            b=all_results[case][ca]['HeapSim_overall']['XPy']
            cu_extraction.append(a)
            cpy_extraction.append(b)
        for i in range(len(collector_area_array)):
            cu_extraction.append(cpy_extraction[i])   
        np.savetxt('Cu_extraction.txt',cu_extraction,delimiter=',')
        
                
    def export_case(self,all_results,case_no,collector_area):
        case='Case'+str(case_no)
        case_p1=all_results[case][collector_area]['pond1']['Pond results time']
        case_p2=all_results[case][collector_area]['pond2']['Pond results time']
        heap_base=all_results[case][collector_area]['HeapSim_overall']['temp_base']
        heap_top=all_results[case][collector_area]['HeapSim_overall']['temp_top']
        heap_gen=all_results[case][collector_area]['HeapSim_overall']['heap_generation']
        results_array=np.column_stack((case_p1,case_p2,heap_base,heap_top,heap_gen))
        np.savetxt('Results_'+case+'.txt',results_array,delimiter=',')

    def export_diesel_use(self,all_results,collector_area_array):
        diesel_use=np.empty([8760,0])        
        for ca in collector_area_array:
            diesel_use=np.column_stack((diesel_use,all_results['Case7'][ca]['Boiler'][:,1]))
        np.savetxt('Diesel_Use.txt',diesel_use,delimiter=',')
            
    def para_results(self,para_results_store,collector_area_array):
        fig, ax1 = plt.subplots(figsize=(16.0,10.0))
        ax2 = ax1.twinx()            
        ax1.plot(collector_area_array, self.cu_output_array, 'b-',linewidth=2,label='Cu Output')
        ax2.plot(collector_area_array,self.pond2_temp_average, 'r-',linewidth=2,label='Temperature')      
        ax1.plot(0, 0, 'r-',linewidth=2,label='Temperature')
        ax1.set_xlabel('Collector Area (m2)')
        ax1.set_ylabel('Cu Extraction (%)')
        ax2.set_ylabel('Average Pond 2 temperature (K)')
        ax1.set_ylim(0,100)
        plt.suptitle(' Cu Extraction vs. Collector Area vs. Temperature')
        ax1.legend(loc=4)
        plot_name = 'CuExtraction_'+self.today+'.png'
        plt.savefig(plot_name,bbox_inches='tight')   

    def plot_cu_extraction(self,para_results_store,collector_area_array,case,start):
        plt.figure(start)
        plt.plot(collector_area_array,para_results_store['Summary'][2,:],label=str(case))
        plt.legend(loc=7)
        plt.xscale('log')
        plt.xlim(0,200000)
        plt.xlabel('Collector Area(m2)')
        plt.ylabel('Cu Extracted (%)')
        plt.savefig('case_vs_cu_'+str(start)+'.png', bbox_inches='tight')

    def case_comparison(self,para_results_store,parametrised_results,case1,case2,comparison):
        # Where case 1 and 2 are the names of cases to be compared
        comparison_array=np.empty([3,19])
        i=0
        for case in [case1,case2]: 
            for j in range(19):
                comparison_array[i,j]=para_results_store[case]['Summary'][j,2]
            i=i+1
        for j in range(19):
            comparison_array[2,j]=comparison_array[0,j]/comparison_array[1,j]
        parametrised_results[comparison]=np.copy(comparison_array)
        
    def daily_heat_profile(self,day,results_store):
        start_point=day*24
#        daily_data_p1=results_store['pond1']['Pond results time'][start_point:start_point+24,1:6]
        daily_data_p2=results_store['pond2']['Pond results time'][start_point:start_point+24,0:6]
        fig, ax1 = plt.subplots(figsize=(16.0, 10.0))    
        ax2 = ax1.twinx()
#        fig(figsize=(16.0, 10.0))
#        plt.plot(daily_data_p1[:,0],label="P1_conv",marker='o')
#        plt.plot(daily_data_p1[:,1],label="P1_evap",marker='+')
#        plt.plot(daily_data_p1[:,2],label="P1_rad",marker='s')
#        plt.plot(daily_data_p1[:,3],label="P1_flow",marker='^')
        ax1.plot(daily_data_p2[:,1],label="P2_conv",ls='--',marker='o')
        ax1.plot(daily_data_p2[:,2],label="P2_evap",ls='--',marker='+')
        ax1.plot(daily_data_p2[:,3],label="P2_rad",ls='--',marker='s')
        ax1.plot(daily_data_p2[:,4],label="P2_flow",ls='--',marker='^')
        ax1.plot(daily_data_p2[:,5],label="P2_solar",ls='--',marker='o')
        ax1.plot(0, 0,color='k',linewidth=2,label='Temperature')
        ax1.legend(fontsize=12,loc=0)        
        ax2.plot(daily_data_p2[:,0],label='Temperature', linewidth=2.,color='k')
        
        y_formatter = plt.ScalarFormatter(useOffset=False)
        ax2.yaxis.set_major_formatter(y_formatter)
        plt.grid(True,color='0.7')
        plt.xlim(0.0,23.0)
        plt.xlabel("Time (hrs)")
        ax1.set_ylabel("Daily Energy Flows (kWh)")
        ax2.set_ylabel('Temperature (K)')
        plt.suptitle("Pond energy for Day %s" % day)
        plt.savefig("Daily_Energy_Plot.png", bbox_inches='tight')
        
    def pie_chart_heat_loss(self,results_store):
        plt.figure(figsize=(6,6))
        p2_heat=np.abs(np.sum(results_store['Summary'][[6,7,8,9,11],0]))
        p1_heat=np.abs(np.sum(results_store['Summary'][[13,14,15,16,18],0]))
        heap_heat=np.abs(results_store['Summary'][12,0])
        tot_heat=p1_heat+p2_heat+heap_heat
        fracs=[p1_heat/tot_heat,p2_heat/tot_heat,heap_heat/tot_heat]
        labels=['Pond1','Pond 2','Heap']
        plt.pie(fracs,autopct='%1.1f%%',pctdistance=1.15,labeldistance=1.3)
        plt.legend(labels,fontsize=11)
        plt.title('Portion of heat losses by component: Base Case',fontsize=12)
        plt.savefig("Heat_loss_pie_chart.png", bbox_inches='tight')
        
    def pie_chat_pond2(self,results_store):
        plt.figure(figsize=(6,6))
        labels=['Convection','Evaporation','Radiation','Flow']
        a=[]
        for i in [6,7,8,9]:        
            a.append(abs(results_store['Summary'][i,0]))
        tot=sum(a)
        [a[i]/tot for i in [0,1,2,3]]        
        plt.pie(a,autopct='%1.1f%%',labeldistance=1.1,labels=labels)
        plt.title('Pond 2 Heat Loss Mechanisms: Base Case',fontsize=12)
        plt.savefig("Pond2_Heat_mech_pie_chart.png", bbox_inches='tight')
        
    def cover_comparison(self,all_results):
        N=3
        ind = np.arange(N)
        fig=plt.figure()
        ax=fig.add_subplot(111)
        p2_nocover=all_results['Case7']['Summary'][[6,7,8,],0]
        p2_cover=all_results['Case5']['Summary'][[6,7,8,],0]
        width=0.25        
        label=['Convection','Evaporation','Radiation']        
        
        ax.bar(ind,p2_nocover,width, color='r')
        ax.bar(ind+width,p2_cover,width, color='b')
        ax.set_ylabel('Heat Loss (kWh)',fontsize=12)
        ax.set_title('Comparison of a covered vs. non-covered pond')
        xTickMarks = label
        ax.set_xticks(ind+width)
        ax.set_xticklabels(xTickMarks)
        plt.grid(True,color='0.7')
        ax.legend(('Uncovered','Covered'),loc=4,fontsize=11)
        plt.savefig("cover_vs_nocover.png", bbox_inches='tight')
        
    def energy_plot(self,all_results,collector_area_array):
        SBG = StackedBarGrapher()
#        N=9
#        ind = np.arange(N)
#        fig=plt.figure()
#        ax=fig.add_subplot(111)        
#        width=0.45
        fig=plt.figure()
        ax = fig.add_subplot(111)     
        
        P2=all_results['Summary'][11,:]-all_results['Summary'][10,:]
        P1=all_results['Summary'][18,:]
        sol=all_results['Summary'][10,:]
        heap=all_results['Summary'][12,:]
        
#        ax.bar(ind,P1,width, color='m')
#        ax.bar(ind,P2,width, color='g',bottom=P1)
#        ax.bar(ind,heap,width, color='r',bottom=np.sum([P1,P2]))
#        ax.bar(ind,sol,width, color='b',bottom=np.sum([P1,P2,heap])) 
        to_plot=np.swapaxes([P1,P2,heap,sol],0,1)        
        colors=['m','g','r','b','k','m','g','r','b']
        
        SBG.stackedBarPlot(ax,to_plot,colors)        
        
        
#        ax.set_ylabel('Energy (kWh)',fontsize=12)
#        ax.set_title('Energy flows for different collector areas')
#        xTickMarks = collector_area_array
#        ax.set_xticks(ind+width)
#        ax.set_xticklabels(xTickMarks)
#        plt.xlabel('Collector Area (m2)')
#        ax.legend(('Pond 1','Pond 2','Heap Gen','Solar Gain'),loc=4,fontsize=11)
        plt.savefig("Energy_bar.png", bbox_inches='tight')        
    
        
    def plot_p2_energy_vs_col_area(self,para_results_store,collector_area_array,name):
        plt.figure()
        plt.plot(collector_area_array,para_results_store['Summary'][6,:],label='P2_conv',marker='o')       
        plt.plot(collector_area_array,para_results_store['Summary'][7,:],label='P2_evap',marker='+')     
        plt.plot(collector_area_array,para_results_store['Summary'][8,:],label='P2_rad',marker='s')     
        plt.plot(collector_area_array,para_results_store['Summary'][9,:],label='P2_flow',marker='^')
        plt.plot(collector_area_array,para_results_store['Summary'][10,:],label='P2_solar',marker='*')
        plt.plot(collector_area_array,para_results_store['Summary'][11,:],label='P2_tot',linewidth=2)   
        plt.legend(loc=2)
        plt.xscale('log')
        plt.grid(True,color='0.7')
        plt.axhline(y=0,color='black')
        plt.xlim(0,200000)
        plt.title(name+': Pond 2 Energy vs Collector Area')
        plt.xlabel('Collector Area (m2)')
        plt.ylabel('Energy (kWh)')
       
    def boiler_use(self,all_results,boiler_array):
        plt.figure()
        for i in boiler_array:
            plt.plot(all_results[i][20000]['Boiler'][:,1],label=i)
        plt.legend()
        plt.title('Conventional Energy')

    def economic_inputs(self,para_results_store,collector_area):
        economic_input_array=np.empty([5,4])  
        qtr=8760/4        
        hs_time=np.reshape(para_results_store[collector_area]['HeapSim_overall']['Time'],len(para_results_store[collector_area]['HeapSim_overall']['Time'])) 
        if hs_time[-1]<365:
            hs_time=[i*24 for i in hs_time]
        hs_cu_rate=np.reshape(para_results_store[collector_area]['HeapSim_overall']['CuExtr'],len(para_results_store[collector_area]['HeapSim_overall']['CuExtr']))
        mass_h20=[]        
        
        for i in range(1,5):
            qtr_range=range(int((i-1)*qtr),int(i*qtr))
            economic_input_array[0,i-1]=np.interp(int(i*qtr),hs_time,hs_cu_rate)  
            if collector_area == 0:
                economic_input_array[1,i-1]=0
            else:
                economic_input_array[1,i-1]=np.sum(para_results_store[collector_area]['pond2']['Pond results time'][qtr_range,5])            
            economic_input_array[2,i-1]=np.sum(para_results_store[collector_area]['Boiler'][qtr_range,1])
            economic_input_array[3,i-1]=np.sum(para_results_store[collector_area]['TRNSYS'][qtr_range,4])+np.sum(para_results_store[collector_area]['TRNSYS'][qtr_range,5])            
            if collector_area == 0:
                economic_input_array[3,i-1]=0 
                
            t_air=self.initial.weather_array[:,11]
            for j in range(8760):
                mass_h20.append((para_results_store[collector_area]['pond2']['Pond results time'][j,2]*1000+para_results_store[collector_area]['pond1']['Pond results time'][j,2]*1000)/((2502535.269-212.56*(t_air[j*self.dt]-273.15))))
            for k in range(len(qtr_range)):
                mass=np.sum(mass_h20[k])    
            economic_input_array[4,i-1]=np.sum(mass)                                        
            
        para_results_store[collector_area]['Economic Summary']=economic_input_array 

    def plot_results(self,results_store,collector_area):
        plt.plot()       

        plt.figure(figsize=(16.0, 10.0)) 
        plt.suptitle('Energy: Pond 1')
        plt.plot(results_store['pond1']['Pond results time'][:, 1], label='Q_conv')
        plt.plot(results_store['pond1']['Pond results time'][:, 2], label='Q_evap')
        plt.plot(results_store['pond1']['Pond results time'][:, 3], label='Q_rad')
        plt.plot(results_store['pond1']['Pond results time'][:, 4], label='Q_flow')
        plt.legend(fontsize=12)
        plt.grid(True,color='0.7')
        plt.xlim(0, self.simtime)
        plt.xlabel("Time (hrs)")
        plt.ylabel("Heat (kWh)")
        name1="Pond1_heat_CA"+str(collector_area)+self.today+".png"
        plt.savefig(name1, bbox_inches='tight')
    
        plt.figure(figsize=(16.0, 10.0))
        plt.suptitle('Energy: Pond 2')
        plt.plot(results_store['pond2']['Pond results time'][:, 1], label='Q_conv')
        plt.plot(results_store['pond2']['Pond results time'][:, 2], label='Q_evap')
        plt.plot(results_store['pond2']['Pond results time'][:, 3], label='Q_rad')
        plt.plot(results_store['pond2']['Pond results time'][:, 4], label='Q_flow')
        plt.plot(results_store['pond2']['Pond results time'][:, 5], label='Q_solar')
        plt.legend(fontsize=12)
        plt.xlim(0, self.simtime)
        plt.grid(True,color='0.7')
        plt.xlabel("Time (hrs)")
        plt.ylabel("Heat (kWh)")
        name2="Pond2_heat_CA"+str(collector_area)+self.today+".png"
        plt.savefig(name2, bbox_inches='tight')
    
        plt.figure(figsize=(16.0, 10.0))
        plt.suptitle('Temperatures over the year')
        plt.plot(results_store['pond1']['Pond results time'][:, 0], label='Pond1')
        plt.plot(results_store['pond2']['Pond results time'][:, 0], label='Pond2')
        plt.plot(results_store['HeapSim_overall']['temp_top'],label='Top Heap Temp')
        plt.plot(results_store['HeapSim_overall']['temp_base'], label='Base Heap Temp')
        plt.legend(loc=4,fontsize=12)
        plt.xlim(0, self.simtime)
        plt.grid(True,color='0.7')
        plt.ylim(285,325)
        plt.xlabel("Time (hrs)")
        plt.ylabel("Temperature (K)")
        name3="Temperatures_CA"+str(collector_area)+self.today+".png"
        plt.savefig(name3, bbox_inches='tight')
    
        plt.figure(figsize=(16.0, 10.0))
        plt.suptitle("TRNSYS Results")
        plt.plot(results_store['TRNSYS'][:,1],label='T_HX out')
        plt.plot(results_store['TRNSYS'][:,8],label='T_HX return')
        plt.plot(results_store['TRNSYS'][:,3],label='T_collector out')
        plt.ylabel("Temperature (K)")
        plt.xlabel("Time (hrs)")
        plt.grid(True,color='0.7')
        plt.xlim(0,self.simtime)
        plt.legend(fontsize=12,loc=4)
        name4="TRNSYS_Results_CA"+str(collector_area)+self.today+".png"
        plt.savefig(name4, bbox_inches='tight')
        
    def print_results(self,results_store):
        title_block_temps=np.array(["Mean","Max ","Min "])
        title_block_heat=np.array(["Convection","Evaporation","Radiation","Flow","Solar","Tot"])
        component_list=np.reshape(["Component   ","Pond 1       ","Pond 2       ","Solar        "],[4,1])
        
        pond1_results=results_store['pond1']['Pond results time']
        pond2_results=results_store['pond2']['Pond results time'] 
        trnsys_output_file=results_store['TRNSYS']
        
        total_surface_irradiation=np.sum(trnsys_output_file[:,9])
        total_col_gain=np.sum(trnsys_output_file[:,6])
        
        res_t_pond1=np.array(["{:5.0f}".format(np.mean(pond1_results[:,0])),"{:5.0f}".format(np.max(pond1_results[:,0])),"{:5.0f}".format(np.min(pond1_results[:,0]))])
        res_t_pond2=np.array(["{:5.0f}".format(np.mean(pond2_results[:,0])),"{:5.0f}".format(np.max(pond2_results[:,0])),"{:5.0f}".format(np.min(pond2_results[:,0]))])
        res_t_solar=np.array(["{:5.0f}".format(np.mean(trnsys_output_file[:,1])),"{:5.0f}".format(np.max(trnsys_output_file[:,1])),"{:5.0f}".format(np.min(trnsys_output_file[:,1]))])
        self.temp_table=np.hstack([component_list,np.vstack([title_block_temps,res_t_pond1,res_t_pond2,res_t_solar])])    
        
        res_q_pond1=np.array(["{:5.0f}".format(np.sum(pond1_results[:,1])),"{:5.0f}".format(np.sum(pond1_results[:,2])),"{:5.0f}".format(np.sum(pond1_results[:,3])),"{:5.0f}".format(np.sum(pond1_results[:,4])),"{:5.0f}".format(np.sum(pond1_results[:,5])),"{:5.0f}".format(np.sum(pond1_results[:,6]))])
        res_q_pond2=np.array(["{:5.0f}".format(np.sum(pond2_results[:,1])),"{:5.0f}".format(np.sum(pond2_results[:,2])),"{:5.0f}".format(np.sum(pond2_results[:,3])),"{:5.0f}".format(np.sum(pond2_results[:,4])),"{:5.0f}".format(np.sum(pond2_results[:,5])),"{:5.0f}".format(np.sum(pond2_results[:,6]))])
        req_q_solar=np.array(["{:5.0f}".format(0),"{:5.0f}".format(0),"{:5.0f}".format(0),"{:5.0f}".format(0),"{:5.0f}".format(np.sum(trnsys_output_file[:,7])),"{:5.0f}".format(np.sum(trnsys_output_file[:,7]))])        
        self.heat_table=np.hstack([component_list,np.vstack([title_block_heat,res_q_pond1,res_q_pond2,req_q_solar])])
               
        print "Temperature Results      (K)"
        print self.temp_table
        print '\n'
        print "Heat Results     (kWh/m2)"
        print self.heat_table
        print '\n'
        print "Solar Results"
        print "Global irradiation:      ","{:14.0f}".format(total_surface_irradiation),"kWh"   #Collector area...
        print "Collector heat gain:     ","{:14.0f}".format(total_col_gain),"kWh"
        print "Actual system gain:      ","{:14.0f}".format(np.sum(pond2_results[:,5])),"kWh"
        print "Utilisation factor:      ","{:14.1f}".format(100*(np.sum(pond2_results[:,5])/(total_surface_irradiation))),"%"
        
    def overall(self):
        hs_temp_input=[1,5,8,10,11,12,13,14,15,16,17,18,19,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]
        hs_cu_extraction=[0.01,0.012,0.016,0.022,0.062,0.288,0.436,0.519,0.573,0.61,0.638,0.658,0.674,0.686,0.727,0.75,0.765,0.773,0.777,0.772,0.773,0.758,0.745,0.731,0.72,0.712,0.706,0.701,0.697,0.693]
        sys_temp_input=[14,16,17,18,20,23,28,31,34,42,50,93]
        sys_cu_extraction=[0.587,0.618,0.624,0.654,0.689,0.709,0.742,0.754,0.761,0.77,0.767,0.691]
        collector_area=[2000,4000,6000,10000,12000,20000,30000,40000,50000,80000,100000,1000000]
        
        fig, ax1 = plt.subplots(figsize=(16.0,10.0))
        ax2 = ax1.twinx()
        ax1.plot(hs_temp_input, hs_cu_extraction,linewidth=2)
        ax1.plot(sys_temp_input, sys_cu_extraction, linewidth=2)
        ax2.plot(sys_temp_input,collector_area, 'r-',linewidth=2)
        ax1.set_xlabel('Temperature Input (degC)')
        ax1.set_ylabel('Cu Extraction (%)')
        ax2.set_ylabel('Collector Area (m2)')
        ax2.set_yscale('log')
        ax1.set_ylim(0,1)
        plt.suptitle('Cu Extraction vs. Temperature')
        plt.savefig('CuExtraction.png',bbox_inches='tight')
          
    def plot_pond2_temps(self,para_results_store,collector_area_array):
        N=8
        ind = np.arange(N)
        fig=plt.figure()
        ax=fig.add_subplot(111)        
        width=0.25
        
        i=0
        a=[]; b=[]
        for col_area in collector_area_array:
            a.append(np.average(para_results_store['Case3'][col_area]['pond2']['Pond results time'][:,0]))
            b.append(np.average(para_results_store['Case4'][col_area]['pond2']['Pond results time'][:,0]))
            i=i+1
        ax.bar(ind,b,width, color='r')
        ax.bar(ind+width,a,width, color='b') 
        
        ax.set_ylabel('Average Temperature (K)',fontsize=12)
        ax.set_title('Temperature Comparison of a covered vs. non-covered pond')
        xTickMarks = collector_area_array
        ax.set_xticks(ind+width)
        ax.set_xticklabels(xTickMarks)
        plt.xlabel('Collector Area (m2)')
        plt.ylim(280,320)
        ax.legend(('Uncovered','Covered'),loc=4,fontsize=11)
        plt.grid(True,color='0.7')
        plt.savefig("Temp_cover_vs_nocover.png", bbox_inches='tight')
        


       
#    def plot_solar_vs_col_area(self,para_results_store,collector_area_array,name):
#        plt.figure()
#        host = host_subplot(111, axes_class=AA.Axes)
#        plt.subplots_adjust(right=0.75)     
#        par1 = host.twinx()
#        par2 = host.twinx()
#
#        offset=60
#        new_fixed_axis = par2.get_grid_helper().new_fixed_axis
#        par2.axis['right'] = new_fixed_axis(loc="right", axes=par2,offset=(offset, 0))
#
#        par2.axis['right'].toggle(all=True)
#
#        p1, = host.plot(collector_area_array,self.solar_energy,label='Solar Energy')
#        p2, = par1.plot(collector_area_array,self.pond2_temp_average,label='Temperature')
#        p3, = par2.plot(collector_area_array,self.cu_output_array,label='Cu Output')
#        
#        host.legend(loc=4)
#        host.axis["left"].label.set_color(p1.get_color())
#        par1.axis["right"].label.set_color(p2.get_color())
#        par2.axis["right"].label.set_color(p3.get_color())    
#        
#        plt.draw()
#        plt.show()
#        
#        plot_name = name+'_SolarEnergy_'+self.today+'.png'
#        plt.savefig(plot_name,bbox_inches='tight')           
        


    def plot_temperatures(self,para_results_store,collector_area_array,name):
        plt.figure(101)
        plt.plot(collector_area_array,self.pond2_temp_average,label='Pond2_'+name,marker='o')
        plt.plot(collector_area_array,self.pond1_temp_average,label='Pond1_'+name)
        plt.legend(loc=2)
        plt.xscale('log')
        plt.xlim(0,200000)
        plt.xlabel('Collector Area(m2)')
        plt.ylabel('Mean Pond Temperature (°C)')
        
    def plot_total_energy(self,para_results_store,collector_area_array,name):
        plt.figure(102)
        plt.plot(collector_area_array,para_results_store['Summary'][11,:],label='P2_tot',linewidth=2)  
        plt.legend(loc=2)
        plt.xscale('log')
        plt.xlim(0,200000)
        plt.xlabel('Collector Area(m2)')
        plt.ylabel('Mean Pond Temperature (°C)')