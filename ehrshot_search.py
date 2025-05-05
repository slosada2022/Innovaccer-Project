import pandas as pd



# Load csv files
concepts = pd.read_csv("ehrshot-omop/concept.csv", low_memory=False)
concept_relationship = pd.read_csv("ehrshot-omop/concept_relationship.csv")
condition = pd.read_csv("ehrshot-omop/condition_occurrence.csv", low_memory=False)
person = pd.read_csv("ehrshot-omop/person.csv")



#These are the provided codes
ckd_icd10_codes = ["N18.1", "N18.2", "N18.3", "N18.4", "N18.5", "N18.6", "N18.9"]       #main disease codes
related_codes = ["N18.30", "N18.31", "N18.32", "Z99.2", "I12.0", "I13.11", "I13.2"]     #additional relevant codes

stage_map = {"N18.1": "Stage 1", "N18.2": "Stage 2", "N18.3": "Stage 3", "N18.4": "Stage 4", 
             "N18.5": "Stage 5", "N18.6": "ESRD", "N18.9": "Unspecified"}


# Filter for ICD-10 codes related to CKD
ckd_icd10_concepts = concepts[
    (concepts["vocabulary_id"] == "ICD10CM") &
    (concepts["concept_code"].isin(ckd_icd10_codes))
]

#ckd_icd10_concepts[["concept_id", "concept_code", "concept_name"]]



# Find SNOMED concepts related to your ICD-10 codes
mapped = concept_relationship[
    (concept_relationship["relationship_id"] == "Maps to") &
    (concept_relationship["concept_id_1"].isin(ckd_icd10_concepts["concept_id"]))
]

# Find corresponding SNOMED concept details
ckd_snomed_concepts = concepts[concepts["concept_id"].isin(mapped["concept_id_2"])]
#print(ckd_snomed_concepts[["concept_id", "concept_name", "vocabulary_id"]])


#Use those SNOMED IDs to filter condition_occurrence
ckd_concept_ids = ckd_snomed_concepts["concept_id"].tolist()
ckd_conditions = condition[condition["condition_concept_id"].isin(ckd_concept_ids)].copy()

ckd_patient_ids = ckd_conditions["person_id"].unique()
print(f"Found {len(ckd_patient_ids)} unique patients with CKD.")    #1269





# # use the ckd patient ids to find data of each ckd patient
# ckd_patients = person[person["person_id"].isin(ckd_patient_ids)]
# print(ckd_patients.head())



#part 2 - use patient data to find dates of ckd stage transitions

# Build SNOMED to stage map using concept_relationship and original ICD-10 codes
concept_stage_map = {}
for _, row in mapped.iterrows():    #iterate thru each row of mapped, which relates SNOMED and ICD-10 codes
    icd_code = ckd_icd10_concepts.loc[
        ckd_icd10_concepts["concept_id"] == row["concept_id_1"], "concept_code"
    ].values[0]
    stage = stage_map.get(icd_code)
    concept_stage_map[row["concept_id_2"]] = stage


# Add stage info to conditions
ckd_conditions["ckd_stage"] = ckd_conditions["condition_concept_id"].map(concept_stage_map)
ckd_conditions["condition_start_DATE"] = pd.to_datetime(ckd_conditions["condition_start_DATE"])

# Group by patient and stage, then get earliest date
stage_dates = (
    ckd_conditions
    .groupby(["person_id", "ckd_stage"])["condition_start_DATE"]
    .min()
    .reset_index()
)

# Sort by patient and stage progression
stage_order = ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5", "ESRD", "Unspecified"]
stage_dates["stage_order"] = stage_dates["ckd_stage"].apply(lambda x: stage_order.index(x))
stage_dates = stage_dates.sort_values(["person_id", "stage_order"])


# Pivot the table
pivoted = stage_dates.pivot(index='person_id', columns='ckd_stage', values='condition_start_DATE')

# Sort columns by clinical order
stage_order = ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5", "ESRD"]
pivoted = pivoted.reindex(columns=stage_order)

# Reset index to turn person_id into a column again
pivoted = pivoted.reset_index()
pivoted.to_csv("results/ckd_stage_diagnoses.csv")
#this variable is ckd_stage_diagnoses
