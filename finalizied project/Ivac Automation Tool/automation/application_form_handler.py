import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from .config import (
    MISSION_CENTER, 
    IVAC_CENTER, 
    VISA_TYPE, 
    VISIT_PURPOSE, 
    RANDOMIZE_VISIT_PURPOSE,
    STOP_BEFORE_SAVE
)

class ApplicationFormHandler:
    def __init__(self, driver):
        self.driver = driver
    
    def _wait_for_dropdown_options(self, element_id):
        """Helper to ensure dropdown is populated before selecting."""
        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda d: len(Select(d.find_element(By.ID, element_id)).options) > 1)

    def fill_mission(self):
        wait = WebDriverWait(self.driver, 30)
        print("[*] Waiting for mission dropdown...")
        
        mission_select = wait.until(
            EC.presence_of_element_located((By.ID, "center"))
        )
        Select(mission_select).select_by_value(MISSION_CENTER)
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

        # Human-like typing
        for ch in webfile:
            webfile_input.send_keys(ch)
            time.sleep(random.uniform(0.1, 0.3))
        
        for ch in webfile:
            confirm_input.send_keys(ch)
            time.sleep(random.uniform(0.1, 0.3))
            
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
        self._wait_for_dropdown_options("center")
        ivac_select = Select(self.driver.find_element(By.ID, "center"))
        ivac_select.select_by_value(IVAC_CENTER)
        print(f"✅ IVAC center set to {IVAC_CENTER}")

    def select_visa_type(self):
        self._wait_for_dropdown_options("visa_type")
        visa_select = Select(self.driver.find_element(By.ID, "visa_type"))
        visa_select.select_by_value(VISA_TYPE)
        print(f"✅ Visa type set to {VISA_TYPE}")

    def select_family_members(self, family_count):
        self._wait_for_dropdown_options("family_count")
        family_select = Select(self.driver.find_element(By.ID, "family_count"))
        family_select.select_by_value(str(family_count))
        print(f"✅ Family members set to {family_count}")

    def fill_visit_purpose(self):
        wait = WebDriverWait(self.driver, 20)
        purpose_textarea = wait.until(
            EC.presence_of_element_located((By.ID, "visit_purpose"))
        )
        
        purpose = random.choice(VISIT_PURPOSE) if RANDOMIZE_VISIT_PURPOSE else VISIT_PURPOSE[0]
        purpose_textarea.clear()
        purpose_textarea.send_keys(purpose)
        print(f"✅ Visit purpose filled.")

    def review_and_submit(self):
        if STOP_BEFORE_SAVE:
            input("⏸️ Please review the form and press Enter to continue with submission...")
        
        wait = WebDriverWait(self.driver, 20)
        submit_button = wait.until(
            EC.element_to_be_clickable((By.ID, "submit_button"))
        )
        submit_button.click()
        print("✅ Application submitted successfully!")

    def process_single_application(self, webfile_number, family_count):
        """Updated signature to match main.py call"""
        self.wait_for_application_page()
        time.sleep(2)

        self.fill_webfile_number(webfile_number)
        self.wait_for_unlock()
        time.sleep(1)

        self.fill_mission()
        time.sleep(1) # Extra time for IVAC center to load
        
        self.select_ivac_center()
        time.sleep(0.5)
        
        self.select_visa_type()
        time.sleep(0.5)
        
        self.select_family_members(family_count)
        time.sleep(0.5)
        
        self.fill_visit_purpose()
        time.sleep(1)
        
        self.review_and_submit()
        
        if self.slots_not_available_detected():
            return "SLOTS_NOT_AVAILABLE"

        return "OK"

    def wait_until_back_to_application_page(self):
        WebDriverWait(self.driver, 600).until(
            lambda d: "/application" in d.current_url
        )

    def slots_not_available_detected(self):
        try:
            # Check for specific "no slots" text on the page
            message = self.driver.find_element("xpath", "//*[contains(text(),'slot')]").text.lower()
            return "not available" in message
        except:
            return False