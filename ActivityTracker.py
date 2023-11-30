import joblib
import pandas as pd
from AppKit import NSWorkspace
import time
import appscript
import numpy as np
from urllib.parse import urlparse
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder

class ActivityTracker:
    def __init__(self):
        self.clf = joblib.load('trained_logistic_model.pkl')
        self.encoder = joblib.load('domain_encoder.pkl')
        self.csv_file_path = 'productivity_data.csv'
        self.load_existing_data()
        self.initialize_variables()

    def load_existing_data(self):
        try:
            self.existing_data = pd.read_csv(self.csv_file_path)
        except FileNotFoundError:
            self.existing_data = pd.DataFrame(columns=['domain_name', 'is_productive'])
    
    def start_tracking(self):
        self.initialize_variables()  # Reinitialize variables for a new session
        self.timer = 25 * 60  # Example duration, adjust as needed
        self.end_time = time.time() + self.timer

    def initialize_variables(self):
        self.active_window_name, self.current_tab = "", ""
        self.start_window, self.start_tab, self.productive, self.unproductive = 0, 0, 0, 0
        self.rough_tab_lst, self.visited_websites, self.website_productivity = [], [], []
        self.windows, self.tab_time_lst, self.windows_time_lst = [], [], []
        self.tab_lst = []  # Initialize the list
        self.timer = int(input("Timer in seconds: "))
        self.end_time = time.time() + self.timer
        self.user_defined_productivity = {}

    def run(self):
        while time.time() < self.end_time:
            self.collect_data()
            time.sleep(1)

        self.process_data()
        self.display_graphs()
        self.calculate_and_display_productivity()
    
    def collect_data(self):
        while time.time() < self.end_time:
            new_window_name = (NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName'])
            if self.active_window_name != new_window_name:
                self.active_window_name = new_window_name
                self.windows.append(self.active_window_name)
                end_window = time.perf_counter()
                window_time = (end_window - self.start_window)
                self.windows_time_lst.append(window_time)
                self.start_window = time.perf_counter()

            if self.active_window_name == 'Safari':
                new_tab = appscript.app("Safari").windows.first.current_tab.URL()
                if new_tab != self.current_tab:
                    self.current_tab = new_tab
                    domain_name = urlparse(new_tab).netloc
                    self.rough_tab_lst.append(new_tab)
                    self.tab_lst.append(domain_name)  # Add the domain to tab_lst
                    self.visited_websites.append(domain_name)
                    print(f"Collected {len(self.tab_lst)} tabs.")  # Debug statement

                    if not domain_name:
                        continue

                    if domain_name not in self.existing_data['domain_name'].values:
                        user_input = input(f"Is the website {domain_name} productive? (yes/no): ").strip().lower()
                        is_productive = 1 if user_input == 'yes' else 0
                        self.user_defined_productivity[domain_name] = is_productive
                        new_row = pd.DataFrame({'domain_name': [domain_name], 'is_productive': [is_productive]})
                        self.existing_data = pd.concat([self.existing_data, new_row], ignore_index=True)
                        self.existing_data.to_csv(self.csv_file_path, index=False)

                    # Determine the productivity status
                    if domain_name in self.user_defined_productivity:
                        is_productive = self.user_defined_productivity[domain_name]
                    elif domain_name in self.existing_data['domain_name'].values:
                        is_productive = self.existing_data[self.existing_data['domain_name'] == domain_name]['is_productive'].iloc[0]
                    else:
                        is_productive = None  # Handle unknown domains
                    
                    # Add productivity status to website_productivity list
                    if is_productive == 1:
                        self.website_productivity.append('productive')
                    elif is_productive == 0:
                        self.website_productivity.append('unproductive')
                    else:
                        self.website_productivity.append('unknown')  # For domains with unknown productivity


                    end_tab = time.perf_counter()
                    tab_time = (end_tab - self.start_tab)
                    self.tab_time_lst.append(tab_time)
                    self.start_tab = time.perf_counter()

            time.sleep(1)


    def process_data(self):
        if len(self.windows_time_lst) > 0:
            del self.windows_time_lst[0]
            last_window_time = self.timer - sum(self.windows_time_lst)
            self.windows_time_lst.append(last_window_time)
            window_df = pd.DataFrame({'Windows': self.windows, 'Window Times': self.windows_time_lst})
            self.window_df = window_df.groupby('Windows')['Window Times'].sum()
        print(f"Processed {len(self.windows_time_lst)} window time entries.")  # Debug statement

        if len(self.tab_time_lst) > 0:
            del self.tab_time_lst[0]
            last_tab_time = abs(self.window_df.get('Safari', 0) - sum(self.tab_time_lst))
            self.tab_time_lst.append(last_tab_time)
            tab_lst = [urlparse(url).netloc for url in self.rough_tab_lst]
            if len(tab_lst) == len(self.tab_time_lst):
                tab_df = pd.DataFrame({'Safari Tabs': tab_lst, 'Time Spent on Each Tab': self.tab_time_lst})
                self.tab_df = tab_df.groupby('Safari Tabs')['Time Spent on Each Tab'].sum()
            else:
                print("Data length mismatch, can't create Tab DataFrame.")
            print(f"Processed {len(self.tab_time_lst)} tab time entries.")  # Debug statement
        else:
            print("No tab time entries to process.")


    def display_graphs(self):
        self.make_graph(self.window_df)
        if len(self.tab_time_lst) > 0:
            self.make_graph(self.Tab_df)

    def calculate_and_display_productivity(self):
        if self.tab_lst:
            print(f"Calculating productivity for {len(self.tab_lst)} tabs.")
            self.finish(self.tab_lst, self.tab_time_lst, self.website_productivity)
        else:
            print("Tab list is empty. No productivity data to calculate.")


    def make_graph(self, dataframe):
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

    def finish(self, tab_lst, tab_time_lst, website_productivity):
        print(f"Debugging Productivity Calculation:")
        print(f"Tabs: {tab_lst}")
        print(f"Tab Times: {tab_time_lst}")
        print(f"Website Productivity: {website_productivity}")

        productive_time = 0
        unproductive_time = 0

        for website, time_spent, productivity in zip(tab_lst, tab_time_lst, website_productivity):
            print(f"Website: {website}, Time Spent: {time_spent}, Productivity: {productivity}")
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

        print(f"Productive Time: {productive_time}, Unproductive Time: {unproductive_time}")
        print(f"Productivity Percentage: {productivity_percentage}%, Unproductivity Percentage: {unproductivity_percentage}%")
        print()
        print(f"Tab time list length: {len(tab_time_lst)}")
        print(f"Website productivity list length: {len(website_productivity)}")

        plt.bar(1, productivity_percentage, color='g', width=.5, edgecolor='black')
        plt.bar(1, unproductivity_percentage, bottom=productivity_percentage, color='r', width=.5, edgecolor='black')
        plt.ylabel('Percentage')
        plt.title('Productivity Graph')
        plt.yticks(np.arange(0, 101, 10))
        plt.legend(labels=[f'The productivity rate is: {round(productivity_percentage, 2)}%', f'The unproductivity rate is: {round(unproductivity_percentage, 2)}%'])
        plt.show()

    def display_graphs(self):
        if hasattr(self, 'window_df'):
            self.make_graph(self.window_df)
        else:
            print("Window data frame not available.")

        if hasattr(self, 'tab_df'):
            self.make_graph(self.tab_df)
        else:
            print("Tab data frame not available.")


# Running the script
if __name__ == "__main__":
    tracker = ActivityTracker()
    tracker.run()