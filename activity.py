# Phase 1: Import Libraries
import joblib
import pandas as pd
from AppKit import NSWorkspace
import time
import appscript
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import numpy as np
import joblib

# Phase 2: Define Helper Functions
def makeGraph(dataframe):
    if dataframe.empty:
        print("No data to plot.")
        return
    dataframe = dataframe.round(3).fillna(0).dropna()
    graph = dataframe.plot.barh(stacked=True, figsize=(8, 7))
    graph.set_ylabel('Windows')
    graph.set_xlabel('Window Times')
    graph.set_xticks(np.arange(0, dataframe.max() + 2))
    graph.bar_label(graph.containers[0])
    plt.tight_layout()
    plt.show()

def Finish(complete, uncomplete):
    total = complete + uncomplete
    if total == 0:
        print("No data for productivity calculation.")
        return
    productivity = (complete / total) * 100
    unproductivity = (uncomplete / total) * 100
    plt.bar(1, productivity, color='g', width=.5, edgecolor='black')
    plt.bar(1, unproductivity, bottom=productivity, color='r', width=.5, edgecolor='black')
    plt.ylabel('Percentage')
    plt.title('Productivity Graph')
    plt.yticks(np.arange(0, 101, 5))
    plt.legend(labels=[f'The productivity rate is: {round(productivity, 2)}%', f'The unproductivity rate is: {round(unproductivity, 2)}%'])
    plt.show()

# Load existing data from CSV
csv_file_path = 'productivity_data.csv'
existing_data = pd.read_csv(csv_file_path)

# New Phase 2.1: Train ML Model
# Load the trained model and encoder
clf = joblib.load('trained_logistic_model.pkl')
encoder = joblib.load('domain_encoder.pkl')

# Phase 3: Initialize Variables
active_window_name, current_tab = "", ""
start_window, start_tab, productive, unproductive = 0, 0, 0, 0
rough_tab_lst, visited_websites, website_productivity, windows, tab_time_lst, windows_time_lst = [], [], [], [], [], []
timer = int(input("Timer in seconds: "))
end_time = time.time() + timer
new_domains = {}

# Phase 4: Data Collection Loop
prediction = [None]
while time.time() < end_time:
    new_window_name = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
    if active_window_name != new_window_name:
        active_window_name = new_window_name
        windows.append(active_window_name)
        end_window = time.perf_counter()
        windows_time_lst.append(end_window - start_window)
        start_window = end_window

    if active_window_name == 'Safari':
        new_tab = appscript.app("Safari").windows.first.current_tab.URL()
        if new_tab != current_tab:
            current_tab = new_tab
            domain_name = urlparse(new_tab).netloc
            if domain_name and domain_name not in existing_data['domain_name'].values and domain_name not in new_domains:
                user_input = input(f"Is the website {domain_name} productive? (yes/no): ").strip().lower()
                is_productive = 1 if user_input == 'yes' else 0
                new_domains[domain_name] = is_productive
                existing_data = pd.concat([existing_data, pd.DataFrame({'domain_name': [domain_name], 'is_productive': [is_productive]})], ignore_index=True)

            if domain_name in new_domains:
                website_productivity.append('productive' if new_domains[domain_name] == 1 else 'unproductive')
            else:
                is_productive = existing_data[existing_data['domain_name'] == domain_name]['is_productive'].iloc[0]
                website_productivity.append('productive' if is_productive else 'unproductive')

            rough_tab_lst.append(domain_name)
            visited_websites.append(domain_name)
            end_tab = time.perf_counter()
            tab_time_lst.append(end_tab - start_tab)
            start_tab = end_tab

    if active_window_name in encoder.classes_:
        window_encoded = encoder.transform([active_window_name])[0]
        prediction = clf.predict([[window_encoded]])
        if prediction[0] == 1:
            productive += 1
        else:
            unproductive += 1

    time.sleep(1)

# Save updated data back to CSV
existing_data.to_csv(csv_file_path, index=False)

# Phase 5: Data Processing for Window
del windows_time_lst[0]
last_window = timer - sum(windows_time_lst)
windows_time_lst.append(last_window)
Window_df = pd.DataFrame({'Windows': windows, 'Window Times': windows_time_lst})
Window_df = Window_df.groupby('Windows')['Window Times'].sum()

# Phase 6: Graph for Window Activity
print(Window_df)
makeGraph(Window_df)
print("Visited websites and their productivity:")
for website, prod in zip(visited_websites, website_productivity):
    print(f"{website}: {prod}")

# Phase 7: Data Processing for Tabs
if len(tab_time_lst) > 0:
    del tab_time_lst[0]
tab_lst = [urlparse(i).netloc for i in rough_tab_lst]
if len(tab_lst) == len(tab_time_lst):
    Tab_df = pd.DataFrame({'Safari Tabs': tab_lst, 'Time Spent on Each Tab': tab_time_lst})
    Tab_df = Tab_df.groupby('Safari Tabs')['Time Spent on Each Tab'].sum()
    # Phase 8: Graph for Tab Activity
    makeGraph(Tab_df)
else:
    print("Data length mismatch, can't create Tab DataFrame.")

# Phase 9: Calculate Productivity
# Phase 10: Display Productivity Graph
Finish(productive, unproductive)
