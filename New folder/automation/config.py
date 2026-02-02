# ----------------------------TARGET SETTINGS----------------------------#
# Target Mission and IVAC for visa application
TARGET_MISSION = "1"
# Dhaka
TARGET_IVAC = "3"
# 3 - Dhaka
VISA_TYPE = "13" # MEDICAL/MEDICAL ATTENDANT
# 13 - MEDICAL/MEDICAL ATTENDANT
FAMILY_MEMBERS = "1" # 1 member
# Number of family members (1-3)
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