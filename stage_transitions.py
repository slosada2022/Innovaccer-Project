import pandas as pd


ckd_stage_diagnoses = pd.read_csv("results/ckd_stage_diagnoses.csv")
#create frames to hold inter-stage transition times
stage_times = pd.DataFrame(columns=["person_id", "1 to 2", "2 to 3", "3 to 4", "4 to 5", "5 to End stage"])


#here, we iterate through the diagnosis dates to find the time each patient transitions between stages

for row in ckd_stage_diagnoses.itertuples(index=False):
    new_row = [row.person_id]

    for i in range(2, len(row)):
        next_stage = row[i]
        prev_stage = row[i-1]
        
        if isinstance(next_stage, str) and isinstance(prev_stage, str): #if both stages aren't tracked, there's no transition time
            new_row.append((pd.to_datetime(next_stage) - pd.to_datetime(prev_stage)).days)
        else:
            new_row.append(None)

    stage_times.loc[len(stage_times)] = new_row

#stage_times.to_csv("results/stage_times.csv", index=False)
print(stage_times.head())   