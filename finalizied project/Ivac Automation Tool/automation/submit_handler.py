from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def wait_for_successful_login(driver, timeout=3600):
    """
    Wait for user to manually complete:
    1. Click "I am human" checkbox
    2. Complete any captcha
    3. Login
    4. Application page loads
    
    Timeout: 1 hour
    """
    wait = WebDriverWait(driver, timeout)

    try:
        print("\n" + "="*60)
        print("⏸️  PAUSED - Manual action required!")
        print("="*60)
        print("✋ Please do the following in the browser:")
        print("   1. Click the 'I am human' checkbox")
        print("   2. Complete any captcha if prompted")
        print("   3. Login with your credentials")
        print("   4. Wait for the application page to fully load")
        print("="*60)
        print(f"⏳ Waiting for /application page (timeout: {timeout}s)...\n")
        
        # Wait for the application page URL
        wait.until(EC.url_contains("/application"))
        
        # Wait for page to fully load
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        
        # Additional wait for body element
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        time.sleep(2)  # Extra buffer for JS to settle
        
        print("="*60)
        print("✅ Application page loaded!")
        print("✅ Resuming automation...\n")
        print("="*60 + "\n")
        return True

    except Exception as e:
        print(f"\n❌ Error: Application page not detected within {timeout}s")
        print(f"❌ Details: {e}")
        return False
