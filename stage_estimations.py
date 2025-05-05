import pandas as pd


#this code finds the mean and median of our transition times
stage_times = pd.read_csv("results/stage_times.csv").drop(columns="person_id")

# print("Mean:\n", stage_times.mean(numeric_only=True))
# print("Median:\n", stage_times.median(numeric_only=True))

transition_columns = stage_times.columns.to_list()  #exclude patient id column

filtered_times = stage_times[transition_columns].where(stage_times[transition_columns] >= 0)

# print("Mean:\n", filtered_times.mean(numeric_only=True))
# print("Median:\n", filtered_times.median(numeric_only=True))

summary = pd.DataFrame({
    "Raw Mean": stage_times.mean(),
    "Raw Median": stage_times.median(),
    "Filtered Mean": filtered_times.mean(),
    "Filtered Median": filtered_times.median(),
}).T.round(2)

summary.to_csv("results/summary.csv")