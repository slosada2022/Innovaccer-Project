import pandas as pd



# Load csv files
concepts = pd.read_csv("ehrshot-omop/concept.csv", low_memory=False)
concept_relationship = pd.read_csv("ehrshot-omop/concept_relationship.csv")
condition = pd.read_csv("ehrshot-omop/condition_occurrence.csv")
person = pd.read_csv("ehrshot-omop/person.csv")



# Filter for ICD-10 codes related to CKD
ckd_icd10_codes = ["N18.1", "N18.2", "N18.3", "N18.4", "N18.5", "N18.6", "N18.9"]


ckd_icd10_concepts = concepts[
    (concepts["vocabulary_id"] == "ICD10CM") &
    (concepts["concept_code"].isin(ckd_icd10_codes))
]

ckd_icd10_concepts[["concept_id", "concept_code", "concept_name"]]



# Join to find SNOMED concepts related to your ICD-10 codes
mapped = concept_relationship[
    (concept_relationship["relationship_id"] == "Maps to") &
    (concept_relationship["concept_id_1"].isin(ckd_icd10_concepts["concept_id"]))
]

# Join to get SNOMED concept details
ckd_snomed_concepts = concepts[concepts["concept_id"].isin(mapped["concept_id_2"])]
#print(ckd_snomed_concepts[["concept_id", "concept_name", "vocabulary_id"]])


#Use those SNOMED IDs to filter condition_occurrence
ckd_concept_ids = ckd_snomed_concepts["concept_id"].tolist()
ckd_conditions = condition[condition["condition_concept_id"].isin(ckd_concept_ids)]

ckd_patient_ids = ckd_conditions["person_id"].unique()
print(f"Found {len(ckd_patient_ids)} unique patients with CKD.")



# ckd_patients = person[person["person_id"].isin(ckd_patient_ids)]
# print(ckd_patients.head())