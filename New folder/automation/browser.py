import undetected_chromedriver as uc
import random
import time
import re
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException

def get_fresh_options():
    """Generates a brand new options object for every launch attempt."""
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-component-extensions-with-background-pages")
    options.add_argument("--disable-background-networking")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return options

def launch_browser():
    # Attempt 1: Standard launch
    try:
        driver = uc.Chrome(
            options=get_fresh_options(), # Pass a fresh object
            use_subprocess=False,
            version_main=None
        )
    except SessionNotCreatedException as e:
        # Common failure: ChromeDriver and Chrome major versions mismatch.
        msg = str(e)
        m_current = re.search(r"Current browser version is (\d+)\.", msg)
        
        if m_current:
            major = int(m_current.group(1))
            print(f"⚠️ Version mismatch detected (Your Chrome is v{major}).")
            print(f"🔄 Retrying with fresh options and forced version_main={major}...")
            
            # Attempt 2: Retry with a NEW options object and the correct version
            driver = uc.Chrome(
                options=get_fresh_options(), # GET A NEW ONE HERE TO AVOID RUNTIMERROR
                use_subprocess=False, 
                version_main=major
            )
        else:
            print("❌ Browser launch failed and could not auto-detect version.")
            raise

    # Configuration after successful launch
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(300)
    
    try:
        driver.execute_script("return 1;")
        print("✅ Browser connection established and verified\n")
    except WebDriverException as e:
        print(f"❌ Failed to verify connection: {e}")
        raise

    return driver

def keep_browser_alive(driver, interval=30):
    try:
        driver.execute_script("return 1;")
        return True
    except WebDriverException:
        return False