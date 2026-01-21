from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException
import time
import threading

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
    
    # Flag to track if we should keep checking connection
    connection_alive = True

    def keep_connection_alive():
        """Background thread to maintain connection with periodic commands"""
        attempt = 0
        while connection_alive and attempt < (timeout / 30):  # Check every 30 seconds
            try:
                time.sleep(30)
                if connection_alive:
                    driver.execute_script("return 1;")
            except (WebDriverException, InvalidSessionIdException):
                # Connection issue, but let main thread handle it
                break
            attempt += 1

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
        
        # Start background thread to keep connection alive
        keeper_thread = threading.Thread(target=keep_connection_alive, daemon=True)
        keeper_thread.start()
        
        # Wait for the application page URL
        wait.until(EC.url_contains("/application"))
        
        # Stop the keeper thread once we've detected the page
        connection_alive = False
        
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

    except (InvalidSessionIdException, WebDriverException) as e:
        connection_alive = False
        print(f"\n❌ Error: Browser connection lost")
        print(f"❌ Details: {e}")
        print("\n⚠️ TROUBLESHOOTING STEPS:")
        print("   1. Check if your antivirus/firewall is blocking Chrome")
        print("   2. Ensure you have enough disk space")
        print("   3. Try closing other Chrome instances")
        print("   4. Run the script again")
        return False
    except Exception as e:
        connection_alive = False
        print(f"\n❌ Error: Application page not detected within {timeout}s")
        print(f"❌ Details: {e}")
        return False

