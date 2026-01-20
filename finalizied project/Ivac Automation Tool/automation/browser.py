import undetected_chromedriver as uc
import random

def launch_browser():
    options = uc.ChromeOptions()
    
    # Basic setup
    options.add_argument("--start-maximized")
    
    # Standard security bypass arguments
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    # Setting a realistic User-Agent (Optional, UC handles this well)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Initialize the undetected driver
    # UC automatically finds your Chrome version and handles the driver download
    driver = uc.Chrome(options=options)
    
    # We use explicit waits in your handler, but a small implicit wait 
    # acts as a secondary safety net
    driver.implicitly_wait(5)

    return driver