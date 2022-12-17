from __future__ import print_function
from hashlib import new
from AppKit import NSWorkspace
import time
from Foundation import *
from os import system
import appscript
import json

start = time.time()
end = time.time()
result = time.time()



active_window_name = ""
current_tab = ""

start = 0
end = 0

lst = []
time_lst = []
time_lst = []
counter = 0
end_time = time.time() + 15
while time.time() < end_time:
    # Starts the code of locating the new window name
    new_window_name = (NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName'])
    # If there is a change of windows then this code runs in order to set the new window as current
    if active_window_name != new_window_name:
        active_window_name = new_window_name
        # print(active_window_name)

        if active_window_name == 'Google Chrome':
            textOfMyScript = """tell app "google chrome" to get the url of the active tab of window 1"""
            s = NSAppleScript.initWithSource_(NSAppleScript.alloc(), textOfMyScript)
            results, err = s.executeAndReturnError_(None)
            print(results.stringValue())
            # print(1)
        # if active_window_name == 'Safari':
        #     new_tab = appscript.app("Safari").windows.first.current_tab.URL()
        #     counter+=1
        #     # print(2)
        #     if new_tab != current_tab:
        #         current_tab = new_tab
        #         lst.append(current_tab)
        #         # print(3)
        #         continue
    # else:
        if active_window_name == 'Safari':
            new_tab = appscript.app("Safari").windows.first.current_tab.URL()
            if new_tab != current_tab:
                current_tab = new_tab
                lst.append(current_tab)
                end = time.perf_counter()
                result = (round(end - start), 2)
                time_lst.append(result)
                start = time.perf_counter()
                continue
            else:
                
                continue
    print(7)
    time.sleep(1)

for i in range(4):
    print()

# for lsts in lst:
#     print(lsts)
#     print('\n')

print(lst)

for i in range(4):
    print()

# for lsts in time_lst:
#     print(lsts)
#     print('\n')

print(time_lst)