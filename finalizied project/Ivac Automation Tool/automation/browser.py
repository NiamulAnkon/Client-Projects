import undetected_chromedriver as uc
import random
import time
from selenium.common.exceptions import WebDriverException

def launch_browser():
    options = uc.ChromeOptions()
    
    # Basic setup
    options.add_argument("--start-maximized")
    
    # Prevent premature browser closing
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Standard security bypass arguments
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    
    # Keep browser process alive longer
    options.add_argument("--disable-component-extensions-with-background-pages")
    options.add_argument("--disable-background-networking")
    
    # Setting a realistic User-Agent (Optional, UC handles this well)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Initialize the undetected driver with better timeout settings
    # version_main=None lets undetected-chrome find the matching version automatically
    driver = uc.Chrome(
        options=options,
        use_subprocess=False,  # Prevents potential subprocess issues
        version_main=None
    )
    
    # Set longer implicit wait to prevent premature timeouts
    driver.implicitly_wait(10)
    
    # Set command timeout to 5 minutes (prevents "timed out" errors during manual steps)
    driver.set_page_load_timeout(300)
    
    # Verify connection is stable
    try:
        driver.execute_script("return 1;")
        print("✅ Browser connection established and verified\n")
    except WebDriverException as e:
        print(f"❌ Failed to establish browser connection: {e}")
        raise

    return driver


def keep_browser_alive(driver, interval=30):
    """
    Keep the browser connection alive by sending periodic commands.
    Useful during long manual waits.
    """
    try:
        driver.execute_script("return 1;")
        return True
    except WebDriverException:
        return False