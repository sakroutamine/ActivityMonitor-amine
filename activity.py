# Phase 1: Import Libraries
import joblib
import pandas as pd
from AppKit import NSWorkspace
import time
import appscript
import numpy as np
from urllib.parse import urlparse
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib


# Phase 2: Define Helper Functions
def makeGraph(dataframe):
    if dataframe.empty:
        print("No data to plot.")
        return
    dataframe = dataframe.round(3).fillna(0).dropna()
    graph = dataframe.plot.barh(stacked=True, figsize=(8,7))
    graph.set_ylabel('Windows')
    graph.set_xlabel('Window Times')
    graph.set_xticks(np.arange(0, dataframe.max() + 2))
    graph.bar_label(graph.containers[0])
    plt.tight_layout()
    plt.show()

def Finish(tab_lst, tab_time_lst, website_productivity):
    productive_time = 0
    unproductive_time = 0

    for website, time_spent, productivity in zip(tab_lst, tab_time_lst, website_productivity):
        if productivity == 'productive':
            productive_time += time_spent
        else:
            unproductive_time += time_spent

    total_time = productive_time + unproductive_time
    if total_time == 0:
        print("No data for productivity calculation.")
        return

    productivity_percentage = (productive_time / total_time) * 100
    unproductivity_percentage = (unproductive_time / total_time) * 100

    plt.bar(1, productivity_percentage, color='g', width=.5, edgecolor='black')
    plt.bar(1, unproductivity_percentage, bottom=productivity_percentage, color='r', width=.5, edgecolor='black')
    plt.ylabel('Percentage')
    plt.title('Productivity Graph')
    plt.yticks(np.arange(0, 101, 10))
    plt.legend(labels=[f'The productivity rate is: {round(productivity_percentage, 2)}%', f'The unproductivity rate is: {round(unproductivity_percentage, 2)}%'])
    plt.show()


# New Phase 2.1: Train ML Model
# Load the trained model and encoder
clf = joblib.load('trained_logistic_model.pkl')
encoder = joblib.load('domain_encoder.pkl')

# Loading CSV data
csv_file_path = 'productivity_data.csv'
try:
    existing_data = pd.read_csv(csv_file_path)
except FileNotFoundError:
    existing_data = pd.DataFrame(columns=['domain_name', 'is_productive'])


# Phase 3: Initialize Variables
active_window_name, current_tab = "", ""
start_window, start_tab, productive, unproductive = 0, 0 , 0, 0
rough_tab_lst, visited_websites, website_productivity, windows, tab_time_lst, windows_time_lst = [], [], [], [], [], []
timer = int(input("Timer in seconds: "))
end_time = time.time() + timer
new_domains = {}
user_defined_productivity = {}

# New Phase 3.1: Initialize Productivity Variables


# Phase 4: Data Collection Loop
prediction = [None]
while time.time() < end_time:
    new_window_name = (NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName'])
    if active_window_name != new_window_name:
        active_window_name = new_window_name
        windows.append(active_window_name)
        end_window = time.perf_counter()
        result_windows = (end_window - start_window)
        windows_time_lst.append(result_windows)
        start_window = time.perf_counter()

    if active_window_name == 'Safari':
        new_tab = appscript.app("Safari").windows.first.current_tab.URL()
        if new_tab != current_tab:
            current_tab = new_tab
            domain_name = urlparse(current_tab).netloc
            rough_tab_lst.append(current_tab)
            visited_websites.append(domain_name)

            # Check if domain is not in the DataFrame and get user input
            if domain_name not in existing_data['domain_name'].values:
                user_input = input(f"Is the website {domain_name} productive? (yes/no): ").strip().lower()
                is_productive = 1 if user_input == 'yes' else 0
                user_defined_productivity[domain_name] = is_productive
                new_row = pd.DataFrame({'domain_name': [domain_name], 'is_productive': [is_productive]})
                existing_data = pd.concat([existing_data, new_row], ignore_index=True)
                existing_data.to_csv(csv_file_path, index=False)

            # Determine the productivity based on user input, existing data, or model prediction
            if domain_name in user_defined_productivity:
                is_productive = user_defined_productivity[domain_name]
                source = 'user input'
            elif domain_name in existing_data['domain_name'].values:
                is_productive = existing_data[existing_data['domain_name'] == domain_name]['is_productive'].iloc[0]
                source = 'CSV data'
            elif domain_name in encoder.classes_:
                domain_encoded = encoder.transform([domain_name])[0]
                is_productive = clf.predict([[domain_encoded]])[0]
                source = 'model prediction'
            else:
                print(f"Skipping prediction for unknown domain: {domain_name}")
                continue
            
            # Append the productivity status
            website_productivity.append('productive' if is_productive == 1 else 'unproductive')
            print(f"Domain: {domain_name}, Productivity: {'productive' if is_productive == 1 else 'unproductive'}, Source: {source}")

        
            end_tab = time.perf_counter()
            result_tab = (end_tab - start_tab)
            tab_time_lst.append(result_tab)
            start_tab = time.perf_counter()
    
    if active_window_name in encoder.classes_:
        window_encoded = encoder.transform([active_window_name])[0]
        prediction = clf.predict([[window_encoded]])
    else:
        print(f"Skipping prediction for unknown window: {active_window_name}")

    if prediction[0] == 1:
        productive += 1
    else:
        unproductive += 1

    time.sleep(1)

# After the data collection loop
# for i, website in enumerate(visited_websites):
#     if website in user_defined_productivity:
#         website_productivity[i] = 'productive' if user_defined_productivity[website] == 1 else 'unproductive'


# Phase 5: Data Processing for Window
del windows_time_lst[0]
last_window = timer - sum(windows_time_lst)
windows_time_lst.append(last_window)
Window_df = pd.DataFrame({'Windows': windows, 'Window Times': windows_time_lst})
Window_df = Window_df.groupby('Windows')['Window Times'].sum()

# Phase 6: Graph for Window Activity
# print(Window_df)
makeGraph(Window_df)
print("Visited websites and their productivity:")
for website, prod in zip(visited_websites, website_productivity):
    print(f"{website}: {prod}")

# Phase 7: Data Processing for Tabs
if len(tab_time_lst) > 0:
    del tab_time_lst[0]
    last_tab = abs(Window_df['Safari'] - sum(tab_time_lst))
    tab_time_lst.append(last_tab)
    
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
# At the end of the script
existing_data.to_csv(csv_file_path, index=False)
# Phase 10: Display Productivity Graph
Finish(tab_lst, tab_time_lst, website_productivity)
