"""
Useful definitions used throughout the IDR.
"""

from drapi.code.drapi.drapi import flatExtend

__all__ = ["LIST_OF_PHI_VARIABLES_BO",
           "LIST_OF_PHI_VARIABLES_CLINICAL_TEXT",
           "LIST_OF_PHI_VARIABLES_OMOP",
           "VARIABLE_NAME_TO_FILE_NAME_DICT",
           "FILE_NAME_TO_VARIABLE_NAME_DICT"]

DICT_OF_PHI_VARIABLES_BIRTHDATES = {"BO": ["Date Of Birth"],
                                    "OMOP": ["birth_datetime"]}
DICT_OF_PHI_VARIABLES_AGE = {"BO": ["Current Age",
                                    "Age At Diagnosis",
                                    "Age at Encounter"]}

LIST_OF_PHI_DATES_BO = ["Date of Diagnosis",
                        "Chemo Start Date Summary",
                        "Combined Last Contact",
                        "Date Of Birth",
                        "Date Of Conclusive Diagnosis",
                        "Date Of Diagnosis",
                        "Date Of Multiple Tumors",
                        "Date Of Sentinel Lymph Node Biopsy",
                        "Date Regional Lymph Node Dissection",
                        "Date Systemic Therapy Started",
                        "Date of Diagnosis - Year",
                        "First Contact Date",
                        "First Recurrence Date",
                        "Hormone Start Date",
                        "Immuno Start Date",
                        "Initial Rx Date",
                        "Most Definitive Surgery Date",
                        "Non Cancer Directed Surgery Date",
                        "Other Rx Start Date",
                        "Radiation End Date",
                        "Radiation Start Date",
                        "Surgery Date Summary",
                        "Surgery Discharge Date Summary"]

LIST_OF_PHI_DATES_CLINICAL_TEXT = ["ContactDate",
                                   "CreatedDatetime",
                                   "EncounterDate",
                                   "OrderPlacedDatetime",
                                   "OrderResultDatetime",
                                   "ServiceDatetime"]

LIST_OF_PHI_DATES_OMOP = ["birth_datetime",
                          "condition_end_date",
                          "condition_end_datetime",
                          "condition_start_date",
                          "condition_start_datetime",
                          "death_date",
                          "death_datetime",
                          "device_exposure_end_date",
                          "device_exposure_end_datetime",
                          "device_exposure_start_date",
                          "device_exposure_start_datetime",
                          "drug_exposure_end_date",
                          "drug_exposure_end_datetime",
                          "drug_exposure_start_date",
                          "drug_exposure_start_datetime",
                          "measurement_date",
                          "measurement_datetime",
                          "observation_date",
                          "observation_datetime",
                          "observation_period_end_date",
                          "observation_period_start_date",
                          "procedure_date",
                          "procedure_datetime",
                          "verbatim_end_date",
                          "visit_end_date",
                          "visit_end_datetime",
                          "visit_start_date",
                          "visit_start_datetime"]


LIST_OF_PHI_VARIABLES_BO = ["Acct Number - Enter DateTime Comb",
                            "Acct Number - Exit DateTime Comb",
                            "At Station",
                            "Authoring Provider Key",
                            "Authorizing Provider Key",
                            "Chemotherapy Rx Hosp Code Desc",
                            "Cosign Provider Key",
                            "Diagnosis County",
                            "EPIC Patient ID",
                            "Encounter #",
                            "Encounter # (CSN)",
                            "Encounter # (Primary CSN)",
                            "Encounter Key",
                            "Encounter Key (Primary CSN)",
                            "Enterprise ID",
                            "From Station",
                            "F/u Physicians",
                            "Linkage Note ID",
                            "Location of Svc",
                            "Location of Svc ID",
                            "Medical Record Number",
                            "Managing Physician",
                            "MRN (Jax)",
                            "MRN (UF)",
                            "NRAS",  # This is PHI but cannot be de-identified, so it should be deleted
                            "Note ID",
                            "Note Key",
                            "Order ID",
                            "Ordering Provider Key",
                            "Order Key",
                            "Prim  surgeon Code",  # NOTE: Double space is intentional
                            "Provider Key",
                            "Patient Encounter Key",
                            "Patient Key",
                            "Patnt Key",
                            "Radiation Hosp Code Desc",
                            "Source Sys",
                            "Surgery Rx Hosp Code Desc",
                            "To Station"]

LIST_OF_PHI_VARIABLES_I2B2 = ["LOCATION_CD"]

LIST_OF_PHI_VARIABLES_CLINICAL_TEXT = ["AuthoringProviderKey",
                                       "AuthorizingProviderKey",
                                       "CosignProviderKey",
                                       "EncounterCSN",
                                       "EncounterKey",
                                       "LinkageNoteID",
                                       "MRN_GNV",
                                       "MRN_JAX",
                                       "NoteID",
                                       "NoteKey",
                                       "OrderID",
                                       "OrderKey",
                                       "OrderingProviderKey",
                                       "PatientKey",
                                       "Patient Key",
                                       "ProviderKey"]

# The list defined `LIST_OF_PHI_VARIABLES_OMOP_BIRTHDATE` is provided for reference. Each variable on its own is not PHI, but in combination with others they are PHI.
LIST_OF_PHI_VARIABLES_OMOP_BIRTHDATE_CONDITIONAL = ["year_of_birth",
                                                    "month_of_birth",
                                                    "day_of_birth"]

# The list `LIST_OF_PHI_VARIABLES_OMOP_UNINFORMATIVE` contains variables that are not analytically valuable because they only uniquely identify the row in a table.
LIST_OF_PHI_VARIABLES_OMOP_UNINFORMATIVE = ["condition_occurrence_id",
                                            "device_exposure_id",
                                            "drug_exposure_id",
                                            "location_source_value",
                                            "measurement_id",
                                            "observation_id",
                                            "observation_period_id",
                                            "procedure_occurrence_id",
                                            "visit_detail_id"]

LIST_OF_PHI_VARIABLES_OMOP = ["care_site_id",
                              "csn",
                              "city",
                              "county",
                              "location_id",
                              "patient_key",
                              "preceding_visit_occurrence_id",
                              "provider_id",
                              "visit_occurrence_id"]

LIST_OF_PHI_VARIABLES = flatExtend([LIST_OF_PHI_VARIABLES_BO,
                                    LIST_OF_PHI_VARIABLES_I2B2,
                                    LIST_OF_PHI_VARIABLES_CLINICAL_TEXT,
                                    LIST_OF_PHI_VARIABLES_OMOP])

# Variable suffixes: By portion
VARIABLE_SUFFIXES_BO = {"Authoring Provider Key": {"columnSuffix": "provider",
                                                   "deIdIDSuffix": "PROV"},
                        "Authorizing Provider Key": {"columnSuffix": "provider",
                                                     "deIdIDSuffix": "PROV"},
                        "Accct Number - Enter DateTime Comb": {"columnSuffix": "account",
                                                               "deIdIDSuffix": "ACCT"},
                        "Acct Number - Exit DateTime Comb": {"columnSuffix": "account",
                                                             "deIdIDSuffix": "ACCT"},
                        "At Station": {"columnSuffix": "station",
                                       "deIdIDSuffix": "STN"},
                        "Chemotherapy Rx Hosp Code Desc": {"columnSuffix": "location",
                                                           "deIdIDSuffix": "LOC"},
                        "Cosign Provider Key": {"columnSuffix": "provider",
                                                "deIdIDSuffix": "PROV"},
                        "Diagnosis County": {"columnSuffix": "location",
                                             "deIdIDSuffix": "LOC"},
                        "EPIC Patient ID": {"columnSuffix": "patient",
                                            "deIdIDSuffix": "PAT"},
                        "Encounter #": {"columnSuffix": "encounter",
                                        "deIdIDSuffix": "ENC"},
                        "Encounter Key": {"columnSuffix": "encounter",
                                          "deIdIDSuffix": "ENC"},
                        "EncounterCSN": {"columnSuffix": "encounter",
                                         "deIdIDSuffix": "ENC"},
                        "Encounter # (CSN)": {"columnSuffix": "encounter",
                                              "deIdIDSuffix": "ENC"},
                        "Encounter # (Primary CSN)": {"columnSuffix": "encounter",
                                                      "deIdIDSuffix": "ENC"},
                        "Encounter Key (Primary CSN)": {"columnSuffix": "encounter",
                                                        "deIdIDSuffix": "ENC"},
                        "Enterprise ID": {"columnSuffix": "patient",
                                          "deIdIDSuffix": "PAT"},
                        "F/u Physicians": {"columnSuffix": "provider",
                                           "deIdIDSuffix": "PROV"},
                        "From Station": {"columnSuffix": "station",
                                         "deIdIDSuffix": "STN"},
                        "Linkage Note ID": {"columnSuffix": "link_note",
                                            "deIdIDSuffix": "LINK_NOTE"},
                        "Location of Svc": {"columnSuffix": "location",
                                            "deIdIDSuffix": "LOC"},
                        "Location of Svc ID": {"columnSuffix": "location",
                                               "deIdIDSuffix": "LOC"},
                        "Medical Record Number": {"columnSuffix": "patient",
                                                  "deIdIDSuffix": "PAT"},
                        "Managing Physician": {"columnSuffix": "provider",
                                               "deIdIDSuffix": "PROV"},
                        "MRN (Jax)": {"columnSuffix": "patient",
                                      "deIdIDSuffix": "PAT"},
                        "MRN (UF)": {"columnSuffix": "patient",
                                     "deIdIDSuffix": "PAT"},
                        "NRAS": {"columnSuffix": "NRAS",
                                 "deIdIDSuffix": "NRAS"},
                        "Note ID": {"columnSuffix": "note",
                                    "deIdIDSuffix": "NOTE"},
                        "Note Key": {"columnSuffix": "note",
                                     "deIdIDSuffix": "NOTE"},
                        "Order ID": {"columnSuffix": "order",
                                     "deIdIDSuffix": "ORD"},
                        "Order Key": {"columnSuffix": "order",
                                      "deIdIDSuffix": "ORD"},
                        "Ordering Provider Key": {"columnSuffix": "order",
                                                  "deIdIDSuffix": "ORD"},
                        "Patient Encounter Key": {"columnSuffix": "encounter",
                                                  "deIdIDSuffix": "ENC"},
                        "Patient Key": {"columnSuffix": "patient",
                                        "deIdIDSuffix": "PAT"},
                        "Patnt Key": {"columnSuffix": "patient",
                                      "deIdIDSuffix": "PAT"},
                        "Prim  surgeon Code": {"columnSuffix": "provider",
                                               "deIdIDSuffix": "PROV"},
                        "Provider Key": {"columnSuffix": "provider",
                                         "deIdIDSuffix": "PROV"},
                        "Radiation Hosp Code Desc": {"columnSuffix": "location",
                                                     "deIdIDSuffix": "LOC"},
                        "Source Sys": {"columnSuffix": "location",
                                       "deIdIDSuffix": "LOC"},
                        "Surgery Rx Hosp Code Desc": {"columnSuffix": "location",
                                                      "deIdIDSuffix": "LOC"},
                        "To Station": {"columnSuffix": "station",
                                       "deIdIDSuffix": "STN"}}

VARIABLE_SUFFIXES_CLINICAL_TEXT = {"AuthoringProviderKey": {"columnSuffix": "provider",
                                                            "deIdIDSuffix": "PROV"},
                                   "AuthorizingProviderKey": {"columnSuffix": "provider",
                                                              "deIdIDSuffix": "PROV"},
                                   "CosignProviderKey": {"columnSuffix": "provider",
                                                         "deIdIDSuffix": "PROV"},
                                   "EncounterCSN": {"columnSuffix": "encounter",
                                                    "deIdIDSuffix": "ENC"},
                                   "EncounterKey": {"columnSuffix": "encounter",
                                                    "deIdIDSuffix": "ENC"},
                                   "LinkageNoteID": {"columnSuffix": "link_note",
                                                     "deIdIDSuffix": "LINK_NOTE"},
                                   "MRN_GNV": {"columnSuffix": "patient",
                                               "deIdIDSuffix": "PAT"},
                                   "MRN_JAX": {"columnSuffix": "patient",
                                               "deIdIDSuffix": "PAT"},
                                   "NoteID": {"columnSuffix": "note",
                                              "deIdIDSuffix": "NOTE"},
                                   "NoteKey": {"columnSuffix": "note",
                                               "deIdIDSuffix": "NOTE"},
                                   "OrderID": {"columnSuffix": "order",
                                               "deIdIDSuffix": "ORD"},
                                   "OrderKey": {"columnSuffix": "order",
                                                "deIdIDSuffix": "ORD"},
                                   "OrderingProviderKey": {"columnSuffix": "order",
                                                           "deIdIDSuffix": "ORD"},
                                   "PatientKey": {"columnSuffix": "patient",
                                                  "deIdIDSuffix": "PAT"},
                                   "ProviderKey": {"columnSuffix": "provider",
                                                   "deIdIDSuffix": "PROV"}}

VARIABLE_SUFFIXES_I2B2 = {"LOCATION_CD": {"columnSuffix": "location",
                                          "deIdIDSuffix": "LOC"}}

VARIABLE_SUFFIXES_OMOP = {"care_site_id": {"columnSuffix": "location",
                                           "deIdIDSuffix": "LOC"},
                          "city": {"columnSuffix": "location",
                                   "deIdIDSuffix": "LOC"},
                          "county": {"columnSuffix": "location",
                                     "deIdIDSuffix": "LOC"},
                          "csn": {"columnSuffix": "encounter",
                                  "deIdIDSuffix": "ENC"},
                          "location_id": {"columnSuffix": "location",
                                          "deIdIDSuffix": "LOC"},
                          "observation_period_id": {"columnSuffix": "encounter",
                                                    "deIdIDSuffix": "ENC"},
                          "patient_key": {"columnSuffix": "patient",
                                          "deIdIDSuffix": "PAT"},
                          "person_id": {"columnSuffix": "patient",
                                        "deIdIDSuffix": "PAT"},
                          "preceding_visit_occurrence_id": {"columnSuffix": "encounter",
                                                            "deIdIDSuffix": "ENC"},
                          "provider_id": {"columnSuffix": "provider",
                                          "deIdIDSuffix": "PROV"},
                          "visit_occurrence_id": {"columnSuffix": "encounter",
                                                  "deIdIDSuffix": "ENC"}}
# Variable suffixes: All
VARIABLE_SUFFIXES_LIST = [VARIABLE_SUFFIXES_BO,
                          VARIABLE_SUFFIXES_CLINICAL_TEXT,
                          VARIABLE_SUFFIXES_I2B2,
                          VARIABLE_SUFFIXES_OMOP]
VARIABLE_SUFFIXES = dict()
for variableSuffixDict in VARIABLE_SUFFIXES_LIST:
    VARIABLE_SUFFIXES.update(variableSuffixDict)

# Variable name to file name map. This is necessary because some variable names have characters which are not allowed in file names, e.g., "/".
VARIABLE_NAME_TO_FILE_NAME_DICT = {varName: varName for varName in LIST_OF_PHI_VARIABLES}

# Over-write the necessary values
VARIABLES_TO_OVER_WRITE = {"F/u Physicians": "F-u Physicians"}
VARIABLE_NAME_TO_FILE_NAME_DICT.update(VARIABLES_TO_OVER_WRITE)
FILE_NAME_TO_VARIABLE_NAME_DICT = {fileName: varName for varName, fileName in VARIABLE_NAME_TO_FILE_NAME_DICT.items()}

# QA
for key in VARIABLE_SUFFIXES_BO.keys():
    checkBO = key not in list(VARIABLE_SUFFIXES_CLINICAL_TEXT.keys()) + list(VARIABLE_SUFFIXES_OMOP.keys())
for key in VARIABLE_SUFFIXES_CLINICAL_TEXT.keys():
    checkClinicalText = key not in list(VARIABLE_SUFFIXES_BO.keys()) + list(VARIABLE_SUFFIXES_OMOP.keys())
for key in VARIABLE_SUFFIXES_OMOP.keys():
    checkOMOP = key not in list(VARIABLE_SUFFIXES_BO.keys()) + list(VARIABLE_SUFFIXES_CLINICAL_TEXT.keys())

assert all([checkBO, checkClinicalText, checkOMOP]), "Some variables are present in more than one variable suffix dictionary. This may lead to unintended consequences."
