# Configuration for automation script
MISSION_CENTER = "1" # Dhaka
# 1 - Dhaka
IVAC_CENTER = "3" # Dhaka
# 3 - Dhaka
VISA_TYPE = "13" # MEDICAL/MEDICAL ATTENDANT
# 13 - MEDICAL/MEDICAL ATTENDANT
FAMILY_MEMBERS = "1" # 1 member
# Number of family members (1-5)
#----------------------------VISIT PURPOSE----------------------------#
VISIT_PURPOSE = [
    "Medical treatment at registered hospital in India",
    "Medical diagnosis and necessary treatment",
    "Medical treatment and follow-up consultation",
    "Medical consultation and specialist supervision",
    "Medical examination at recognized center",
]
#------------------------------Behavior Settings------------------------------#
RANDOMIZE_VISIT_PURPOSE = True # Randomize visit purpose from the list above
STOP_BEFORE_SAVE = True # Stop before saving the application for manual review