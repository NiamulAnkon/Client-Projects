from automation.browser import launch_browser
from automation.input_handler import collect_all_data
from automation.handler import IVACBot
from automation.submit_handler import wait_for_successful_login
from selenium.webdriver.support.ui import WebDriverWait
import sys


APPLICATION_URL = "https://payment.ivacbd.com/application"


def wait_until_application_page(driver, timeout=600):
    """
    Waits until user returns back to /application page
    after payment or submission.
    """
    WebDriverWait(driver, timeout).until(
        lambda d: "/application" in d.current_url
    )
    return True


def main():
    print("🧾 IVAC Automation Tool Starting...\n")
    user_data = collect_all_data()
    driver = launch_browser()
    bot = IVACBot(driver)

    try:
        try:
            bot.perform_login(user_data["login"]["phone"])
        except AttributeError:
            # Fallback: perform_login may be missing on older versions; instruct manual login
            print("⚠️ perform_login not implemented on IVACBot. Please login manually in the browser (captcha/OTP).")
        except Exception as e:
            print(f"❌ Error initiating login: {e}")
            # Attempt graceful shutdown to avoid destructor issues
            try:
                driver.quit()
            except Exception:
                pass
            return

        print("\n⏳ Waiting for manual login...")
        if not wait_for_successful_login(driver):
            print("❌ Login failed.")
            try:
                driver.quit()
            except Exception:
                pass
            return

        for index, app in enumerate(user_data["apps"], start=1):
            try:
                print(f"\n🚀 Processing {index}/{len(user_data['apps'])} | {app['webfile']}")
                
                if "/application" not in driver.current_url:
                    driver.get(APPLICATION_URL)
                
                bot.fill_form(app)
                
                # Wait for user to finish payment if more apps remain
                if index < len(user_data["apps"]):
                    print("\n💳 Please complete payment. Waiting for return to /application...")
                    wait_until_application_page(driver)
                    
            except Exception as e:
                print(f"⚠️ App {index} failed but continuing. Error: {e}")
                input("Press Enter to try the next one or fix manually...")
                continue

    finally:
        print("\n🏁 Process finished. The browser will stay open.")


if __name__ == "__main__":
    main()