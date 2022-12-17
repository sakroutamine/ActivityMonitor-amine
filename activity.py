from AppKit import NSWorkspace
import time
import appscript
import pandas as pd
import numpy as np
from urllib.parse import urlparse
import datetime
import matplotlib.pyplot as plt



# function to make the graph
def makeGraph(dataframe):
    dataframe = dataframe.round(3)
    dataframe = dataframe.fillna(0)
    dataframe = dataframe.dropna()
    # Plot the graph so that it also shows the time on each bar
    graph = dataframe.plot.barh(stacked=True, figsize=(8,7))
    graph.set_ylabel('Windows')
    graph.set_xlabel('Window Times')
    graph.set_xticks(np.arange(0, dataframe.max() + 2))
    graph.bar_label(graph.containers[0])
    plt.tight_layout()


    plt.show()

# Phase 1
    # Get raw data of  
        # Which Windows are being activated
        # How long a user spends on his window
        # Which tabs within Safari are being used
        # How long those tabs are being used for

# Window Variables
active_window_name = ""
current_tab = ""
start_window = 0
end_window = 0
windows = []
windows_time_lst = []

# Tab Timer Variables
start_tab = 0
end_tab = 0
tab_time_lst = []
rough_tab_lst = []

# Seconds
timer = int(input("Timer in seconds: "))

# Overall Timer
# timer = float(input("Enter how many seconds timer: "))
end_time = time.time() + timer

while time.time() < end_time:

    # Starts the code of locating the new window name
    new_window_name = (NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName'])
    
    # If there is a change of windows then this code runs in order to set the new window as current
    if active_window_name != new_window_name:
        # Gets the active window name
        active_window_name = new_window_name
        windows.append(active_window_name)

        # Measures the time that is spent on that tab
        end_window = time.perf_counter()
        result_windows = (end_window - start_window)
        windows_time_lst.append(result_windows)
        start_window = time.perf_counter()
    
    # Accesses Safari
    if active_window_name == 'Safari':
        # Accesses the tab from Safari
        new_tab = appscript.app("Safari").windows.first.current_tab.URL()
        
        
        if new_tab != current_tab:
            # Sets new tab as Current tab
            current_tab = new_tab
            rough_tab_lst.append(current_tab)

            # Measures the time that is spent on that tab
            end_tab = time.perf_counter()
            result_tab = (end_tab - start_tab)
            tab_time_lst.append(result_tab)
            start_tab = time.perf_counter()

            continue

    time.sleep(1)


# Bugs
    # If it stays on only one tab or window the whole time the inputs will be wrong (FIXED)

# Completed
    # Windows List


# Phase 2
    # Simplify the windows list to remove duplicates and add values together

# Windows with Timings

# Delete the first element as it has no value 
del windows_time_lst[0]
# Add the amount of time you spent on the last tab you leave off off
last_window = timer - sum(windows_time_lst)
windows_time_lst.append(last_window)

Window_df = pd.DataFrame( {'Windows':windows, 'Window Times':windows_time_lst})
Window_df = Window_df.groupby('Windows')['Window Times'].sum()
print(Window_df)
makeGraph(Window_df)

# Get time of last tab left off
del tab_time_lst[0]
last_tab = Window_df.loc['Safari'] - sum(tab_time_lst)
tab_time_lst.append(last_tab)

# Slice the strings
# Rough tabs contains the raw data while tablst contains the prettier version of the data
tab_lst = []
for i in rough_tab_lst:
    newString = urlparse(i).netloc
    tab_lst.append(newString)

# Tabs with Timings
Tab_df = pd.DataFrame( {'Safari Tabs':tab_lst, 'Time Spent on Each Tab':tab_time_lst})
Tab_df = Tab_df.groupby('Safari Tabs')['Time Spent on Each Tab'].sum()
print()
print(Tab_df)
makeGraph(Tab_df)

print("testing")
# Phase 3
    # Make the UI that displays the data 
    # Select your Workflow with your dates
    # Date that you worked on -> Window Timings -> Safari Tab Timings
    # Websites that count as unproductive and productive
    # Bar Graph