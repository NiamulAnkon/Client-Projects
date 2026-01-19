import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from .config import (
    MISSION_CENTER, 
    IVAC_CENTER, 
    VISA_TYPE, 
    FAMILY_MEMBERS, 
    VISIT_PURPOSE, 
    RANDOMIZE_VISIT_PURPOSE,
    STOP_BEFORE_SAVE
    )

class ApplicationFormHandler:
    def __init__(self, driver):
        self.driver = driver
    
    def fill_mission(self):
        wait = WebDriverWait(self.driver, 30)

        print("[*] Waiting for mission dropdown...")

        mission_select = wait.until(
        EC.presence_of_element_located((By.ID, "center"))
        )


        Select(mission_select).select_by_visible_text("Dhaka")

        print("[+] Mission selected")
    
    def fill_webfile_number(self, webfile):
        wait = WebDriverWait(self.driver, 20)
        webfile_input = wait.until(
            EC.presence_of_element_located((By.ID, "webfile_id"))
        )
        confirm_input = wait.until(
            EC.presence_of_element_located((By.ID, "first-name"))
        )
        webfile_input.clear()
        confirm_input.clear()

        for ch in webfile:
            webfile_input.send_keys(ch)
            time.sleep(0.5)
        for ch in webfile:
            confirm_input.send_keys(ch)
            time.sleep(0.5)
        print(f"✅ Webfile number {webfile} entered.")

    def wait_for_unlock(self):
        wait = WebDriverWait(self.driver, 60)

        wait.until(
            lambda d: d.find_element(By.ID, "center").is_enabled()
        )

        print("✅ Dependent fields unlocked.")

    
    def wait_for_application_page(self):
        wait = WebDriverWait(self.driver, 30)
        wait.until(EC.url_contains("/application"))
        print("✅ Application page loaded.")
    

    def select_ivac_center(self):
        wait = WebDriverWait(self.driver, 20)
        ivac_select = wait.until(
            EC.presence_of_element_located((By.ID, "center"))
        )
        Select(ivac_select).select_by_value(IVAC_CENTER)
        print(f"✅ IVAC center set to {IVAC_CENTER}")

    def select_visa_type(self):
        wait = WebDriverWait(self.driver, 20)
        visa_select = wait.until(
            EC.presence_of_element_located((By.ID, "visa_type"))
        )
        Select(visa_select).select_by_value(VISA_TYPE)
        print(f"✅ Visa type set to {VISA_TYPE}")

    def select_family_members(self):
        wait = WebDriverWait(self.driver, 20)
        family_select = wait.until(
            EC.presence_of_element_located((By.ID, "family_count"))
        )
        Select(family_select).select_by_value(FAMILY_MEMBERS)
        print(f"✅ Family members set to {FAMILY_MEMBERS}")

    def fill_visit_purpose(self):
        wait = WebDriverWait(self.driver, 20)
        purpose_textarea = wait.until(
            EC.presence_of_element_located((By.ID, "visit_purpose"))
        )
        
        purpose = random.choice(VISIT_PURPOSE) if RANDOMIZE_VISIT_PURPOSE else VISIT_PURPOSE[0]
        purpose_textarea.clear()
        purpose_textarea.send_keys(purpose)
        print(f"✅ Visit purpose filled: {purpose[:50]}...")

    def review_and_submit(self):
        if STOP_BEFORE_SAVE:
            input("⏸️ Please review the form and press Enter to continue with submission...")
        
        wait = WebDriverWait(self.driver, 20)
        submit_button = wait.until(
            EC.element_to_be_clickable((By.ID, "submit_button"))
        )
        submit_button.click()
        print("✅ Application submitted successfully!")

    def process_single_application(self, webfile):
        self.wait_for_application_page()

        self.fill_webfile_number(webfile)
        self.wait_for_unlock()   # waits for JS validation

        self.fill_mission()
        self.select_ivac_center()
        self.select_visa_type()
        self.select_family_members()
        self.fill_visit_purpose()
        self.review_and_submit()
