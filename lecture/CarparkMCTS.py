import pandas as pd
import math
from datetime import datetime
from datetime import timedelta
# Load re-generated time of arrival and exit for each hourly user
# Column names: Day, Weekday, ArrivalTime, ExitTime, LengthOfStay
hourly_data = pd.read_csv("C:\\Users\\Wei Zhang\\Box Sync\\Teaching\
\BA Program\\Quantitative Analysis Methods\\2019-2020\\Slides\
\Session_03_Data\\Hourly_ReGen.csv", header=0, index_col=0)
# Load re-generated time of exit and return for each monthly floating user
# Column names: Day, Weekday, CarNo, ExitTime, ReturnTime, Duration
monthly_data = pd.read_csv("C:\\Users\\Wei Zhang\\Box Sync\\Teaching\
\BA Program\\Quantitative Analysis Methods\\2019-2020\\Slides\
\Session_03_Data\\MonthlyFloating_ReGen.csv", header=0, index_col=0)

# Carpark parameter (Period measured by minute)
NS=40;NM=20;Period=15
# Initial state (monthly, hourly)
state={'nM':20,'nH':0}
# Define the trees related to different days of a week
weekday_tree={0:{'Time':datetime.strptime('12:0:0 AM','%I:%M:%S %p'),'Child':[],'State':state,
                 'Type':'D','n':0,'V':0},'DayOfWeek':{1:1,2:1,3:1,4:1,5:1,6:0,7:0}}
weekend_tree={0:{'Time':datetime.strptime('12:0:0 AM','%I:%M:%S %p'),'Child':[],'State':state,
                 'Type':'D','n':0,'V':0},'DayOfWeek':{1:0,2:0,3:0,4:0,5:0,6:1,7:1}}

def Expand(tree, node):
    if len(tree[node]['Child'])==0:
        tree[len(tree)-1]={'Time':tree[node]['Time'],'Child':[],'Parent':node,
                           'Decision':'Available','Type':'S','n':0,'V':0,'UCB':float('inf')}
        tree[len(tree)-1]={'Time':tree[node]['Time'],'Child':[],'Parent':node,
                           'Decision':'Full','Type':'S','n':0,'V':0,'UCB':float('inf')}
        tree[node]['Child']=[len(tree)-3,len(tree)-2]
        

def BuildTree(tree, node, k):
    day=0 # pointing to a day in the data sets
    for d in range(k):
        day=day+1
        
        # Prepare a notebook to keep track of entrance and exit given any initial state
        notebook={'Die':0}
        time=tree[node]['Time']
        while time<datetime.strptime('11:59:59 PM', '%I:%M:%S %p'):
            notebook[time]={'Revenue':0,'Delta_nM':0,'Delta_nH':0}
            time=time+timedelta(minutes=Period)
        nM=tree[node]['State']['nM'];nH=tree[node]['State']['nH']
        
        # Simulate when the outside monthly users return
        if nM<NM:
            search=0                                                                                     ######################## We need give a random number to find the day   
            # Search in the data for a monthly user who left before the starting time given by the 'node'
            for i in range(NM-nM):
                while tree['DayOfWeek'][monthly_data['Weekday'].values[search]]==0:
                    # Move on until we find the correct day
                    search=search+1
                    if search>=len(monthly_data):
                        search=0
                # t_1 stores the exit time and t_2 stores the return time
                t_1=datetime.strptime(monthly_data['ExitTime'].values[search], '%I:%M:%S %p')
                t_2=datetime.strptime(monthly_data['ReturnTime'].values[search], '%I:%M:%S %p')
                # If the current time is between t_1 & t_2, we can use this record to simulate the return time
                if tree[node]['Time']>t_1 and tree[node]['Time']<=t_2:
                    time=tree[node]['Time']
                    while time+timedelta(minutes=Period)<=t_2:
                        time=time+timedelta(minutes=Period)
                    # Find out when this user will return and record the time in the notebook
                    notebook[time]['Delta_nM']=notebook[time]['Delta_nM']+1
        # Simulate when the inside hourly users leave
        if nH>0:
            search=0                                                                                    ######################## We need give a random number to find the day
            # Search in the data for an hourly user who entered before the starting time
            for i in range(nH):
                while tree['DayOfWeek'][hourly_data['Weekday'].values[search]]==0:
                    search=search+1
                    if search>=len(hourly_data):
                        search=0
                t_1=datetime.strptime(hourly_data['ArrivalTime'].values[search], '%I:%M:%S %p')
                t_2=datetime.strptime(hourly_data['ExitTime'].values[search], '%I:%M:%S %p')
                if tree[node]['Time']>t_1 and tree[node]['Time']<=t_2:
                    time=tree[node]['Time']
                    while time+timedelta(minutes=Period)<=t_2:
                        time=time+timedelta(minutes=Period)
                    notebook[time]['Delta_nH']=notebook[time]['Delta_nH']-1        # Initialize day and time for simulation
                    
        while tree['DayOfWeek'][hourly_data['Weekday'][day].values[0]]==0:
            # Find the correct day for the simulation (the day indexes are the same in both data sets)
            day=day+1
            if day>hourly_data.index[len(hourly_data.index)-1]:
                day=1
        # Find out the total number of hourly users to come; the number of monthly users is known
        total_H=len(hourly_data['Weekday'][day])
        index_H=0;index_M=0
        time=tree[node]['Time']
        # Start expansion, selection, and simulation
        pointer=node
        # Continue until reaching the end of a day
        while time<=datetime.strptime('11:59:59 PM', '%I:%M:%S %p'):
            # Expanson
            if len(tree[pointer]['Child'])==0:
                Expand(tree, pointer)
            # Selection
            if tree[tree[pointer]['Child'][1]]['UCB']>tree[tree[pointer]['Child'][0]]['UCB']:
                pointer=tree[pointer]['Child'][1]
            else:
                pointer=tree[pointer]['Child'][0]
            # Simulation
            if index_H>=total_H:
                # If we run out of hourly users, just set the arrival time to the day end
                t_1=datetime.strptime('12:0:0 AM','%I:%M:%S %p')+timedelta(days=1)
            else:
                # t_1 is the arrival time of the next hourly user
                t_1=datetime.strptime(hourly_data['ArrivalTime'][day].values[index_H], '%I:%M:%S %p')
            if index_M>=NM:
                # If we run out of monthly users, just set the exit time to the day end
                t_2=datetime.strptime('12:0:0 AM','%I:%M:%S %p')+timedelta(days=1)
            else:
                # t_2 is the exit time of the next monthly user
                t_2=datetime.strptime(monthly_data['ExitTime'][day].values[index_M], '%I:%M:%S %p') 
            # Check for the next 15min whether there will be hourly users arriving or monthly users leaving
            while t_1<time+timedelta(minutes=Period) or t_2<time+timedelta(minutes=Period):
                # Check which comes first
                if t_1<t_2:
                    # If an hourly user comes first, check whether the door is open
                    if tree[pointer]['Decision']=='Available':
                        nM=tree[tree[pointer]['Parent']]['State']['nM']+notebook[time]['Delta_nM']
                        nH=tree[tree[pointer]['Parent']]['State']['nH']+notebook[time]['Delta_nH']
                        # Check whether arrive in this period and whether spaces are available
                        if t_1>=time and nM+nH<NS:
                            # If yes, record the revenue and write in the notebook
                            notebook[time]['Revenue']=notebook[time]['Revenue']+hourly_data[
                                'LengthOfStay'][day].values[index_H]
                            notebook[time]['Delta_nH']=notebook[time]['Delta_nH']+1
                            # Redefine t_1 and t_2 to be current and exit time
                            t_1=time
                            t_2=datetime.strptime(hourly_data['ExitTime'][day].values[index_H], '%I:%M:%S %p')
                            # Check whether the exit time is before day end; if yes, update the notebook
                            if t_2<datetime.strptime('12:0:0 AM','%I:%M:%S %p')+timedelta(days=1):
                                while t_1+timedelta(minutes=Period)<=t_2:
                                    t_1=t_1+timedelta(minutes=Period)
                                notebook[t_1]['Delta_nH']=notebook[t_1]['Delta_nH']-1
                    index_H=index_H+1
                else:# If a monthly user leaves first
                    if t_2>=time:
                        notebook[time]['Delta_nM']=notebook[time]['Delta_nM']-1
                        t_1=time
                        t_2=datetime.strptime(monthly_data['ReturnTime'][day].values[index_M], '%I:%M:%S %p')
                        if t_2<datetime.strptime('12:0:0 AM','%I:%M:%S %p')+timedelta(days=1): #monthly user returns within this day, update the notebook
                            while t_1+timedelta(minutes=Period)<=t_2:
                                t_1=t_1+timedelta(minutes=Period)
                            notebook[t_1]['Delta_nM']=notebook[t_1]['Delta_nM']+1
                    index_M=index_M+1 # go to next montly user
                if index_H>=total_H:
                    t_1=datetime.strptime('12:0:0 AM','%I:%M:%S %p')+timedelta(days=1)
                else:
                    t_1=datetime.strptime(hourly_data['ArrivalTime'][day].values[index_H], '%I:%M:%S %p')
                if index_M>=NM:
                    t_2=datetime.strptime('12:0:0 AM','%I:%M:%S %p')+timedelta(days=1)
                else:
                    t_2=datetime.strptime(monthly_data['ExitTime'][day].values[index_M], '%I:%M:%S %p') 
            # Now get the updated system state at the end of the 15min period
            nM=tree[tree[pointer]['Parent']]['State']['nM']+notebook[time]['Delta_nM']
            nH=tree[tree[pointer]['Parent']]['State']['nH']+notebook[time]['Delta_nH']
            # Check if any monthly users are offended
            if nM+nH>NS:
                notebook['Die']=1
                break
            # Check if the state has been realized before
            n_Child=len(tree[pointer]['Child'])
            while n_Child>0:
                if tree[tree[pointer]['Child'][n_Child-1]]['State']=={'nM':nM,'nH':nH}:
                    pointer=tree[pointer]['Child'][n_Child-1]
                    break
                else:
                    n_Child=n_Child-1
            # If no, add a new decision node
            if n_Child==0:
                tree[len(tree)-1]={'Time':time+timedelta(minutes=Period),'Child':[],
                                   'Parent':pointer,'State':{'nM':nM,'nH':nH},'Type':'D','n':0,'V':0}
                tree[pointer]['Child'].append(len(tree)-2)
                pointer=len(tree)-2
            # Update the current system time
            time=tree[pointer]['Time']
        # Start backpropagation; BSR is the total revenue going forward in the simulation
        BSR=0
        while pointer>node:
            pointer=tree[pointer]['Parent']
            # Only update BSR if the node is a state-of-nature node (representing an option)
            if tree[pointer]['Type']=='S':
                BSR=BSR+notebook[tree[pointer]['Time']]['Revenue']*(1-notebook['Die'])
            # Update V and n
            tree[pointer]['V']=(tree[pointer]['V']*tree[pointer]['n']+BSR)/(tree[pointer]['n']+1)
            tree[pointer]['n']=tree[pointer]['n']+1
            # Only update UCB for a state-of-nature node
            # Also update the N_i and UCB for options not chosen in this simulation
            if tree[pointer]['Type']=='S':
                tree[pointer]['UCB']=tree[pointer]['V']+2*(
                    math.log(tree[tree[pointer]['Parent']]['n']+1)/tree[pointer]['n'])**0.5
                if pointer==tree[tree[pointer]['Parent']]['Child'][0]:
                    other=tree[tree[pointer]['Parent']]['Child'][1]
                else:
                    other=tree[tree[pointer]['Parent']]['Child'][0]
                if tree[other]['n']>0:
                    tree[other]['UCB']=tree[other]['V']+2*(
                        math.log(tree[tree[other]['Parent']]['n']+1)/tree[other]['n'])**0.5

def Optimization(tree, k):
    node=0
    while tree[node]['Time']<datetime.strptime('12:0:0 AM','%I:%M:%S %p')+timedelta(days=1):
        print('Now is '+str(tree[node]['Time'].time())+'.')
        if tree[node]['n']==0:
            BuildTree(tree, node, k)
        if tree[tree[node]['Child'][1]]['UCB']>tree[tree[node]['Child'][0]]['UCB']:
            node=tree[node]['Child'][1]
        else:
            node=tree[node]['Child'][0]
        print('For the next 15 min, show '+tree[node]['Decision']+'.')
        print('During this 15 min:')
        delta_nM=int(input('What is the net number of entrance of monthly users?'))
        delta_nH=int(input('What is the net number of entrance of hourly users?'))
        nM=tree[tree[node]['Parent']]['State']['nM']+delta_nM
        nH=tree[tree[node]['Parent']]['State']['nH']+delta_nH
        if nM+nH>NS:
            print('Game Over!')
            break
        else:
            n_Child=len(tree[node]['Child'])
            while n_Child>0:
                if tree[tree[node]['Child'][n_Child-1]]['State']=={'nM':nM,'nH':nH}:
                    node=tree[node]['Child'][n_Child-1]
                    break
                else:
                    n_Child=n_Child-1
            if n_Child==0:
                tree[len(tree)-1]={'Time':tree[node]['Time']+timedelta(minutes=Period),'Child':[],
                                            'Parent':node,'State':{'nM':nM,'nH':nH},'Type':'D','n':0,'V':0}
                tree[node]['Child'].append(len(tree)-2)
                node=len(tree)-2


BuildTree(weekday_tree, 0, 100)

# Write down the tree in a CSV
#weekday_tree.pop('DayOfWeek')
#tree_data=pd.DataFrame(data=weekday_tree)
#transposed_tree=tree_data.T
#transposed_tree.to_csv("C:\\Users\\Wei Zhang\\Box Sync\\Teaching\
#\BA Program\\Quantitative Analysis Methods\\2019-2020\\Slides\
#\Session_03_Data\\tree_data.csv")

Optimization(weekday_tree, 100)
