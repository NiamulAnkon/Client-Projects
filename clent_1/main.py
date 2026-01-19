from automation.browser import launch_browser
from automation.submit_handler import wait_for_successful_login
from automation.application_form_handler import ApplicationFormHandler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    driver = launch_browser()
    driver.get("https://payment.ivacbd.com/")

    print("👉 Please login manually in the opened browser.")
    print("👉 Complete captcha and OTP. Do not close the browser.")

    logged_in = wait_for_successful_login(driver)

    if not logged_in:
        print("❌ Login not detected. Exiting.")
        return

    print("✅ Login detected successfully.")
    print("⏳ Waiting for application page...")

    WebDriverWait(driver, 60).until(
        EC.url_contains("/application")
    )

    print("✅ Application page opened.")

    handler = ApplicationFormHandler(driver)

    webfile_number = "BGDDVBCB1425"

    handler.process_single_application(webfile_number)

    print("✅ Application processing completed.")

if __name__ == "__main__":
    main()
