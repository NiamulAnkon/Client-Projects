from automation.browser import launch_browser
from automation.submit_handler import wait_for_successful_login

def main():
    driver = launch_browser()
    driver.get("https://payment.ivacbd.com/")

    print("👉 Please login manually using browser.")
    print("👉 After successful login, application page will open automatically.")

    logged_in = wait_for_successful_login(driver)

    if logged_in:
        print("🚀 Step 2 complete. Ready to start automation.")
    else:
        print("⚠️ Step 2 failed. Login not detected.")

if __name__ == "__main__":
    main()