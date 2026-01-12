from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def wait_for_successful_login(driver, timeout=300):
    wait = WebDriverWait(driver, timeout)

    try:
        wait.until(EC.url_contains("/application"))
        wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        print("✅ Login successful. Application page loaded.")
        return True

    except Exception:
        print("❌ Login not detected within time.")
        return False
