from automation.browser import launch_browser
from automation.submit_handler import wait_for_successful_login
from automation.application_form_handler import ApplicationFormHandler
from automation.input_handler import collect_application_inputs

def main():
    applications = collect_application_inputs()

    driver = launch_browser()
    driver.get("https://payment.ivacbd.com/")

    print("\n" + "="*60)
    print("🔓 LOGIN PAGE OPENED")
    print("="*60)
    print("Chrome browser is now open and waiting for you.")
    print("Script is PAUSED and will not touch the browser.")
    print("="*60 + "\n")
    
    # Wait for user to manually complete login
    logged_in = wait_for_successful_login(driver)

    if not logged_in:
        print("⚠️ Login not detected. Exiting.")
        return

    print("✅ Logged in successfully. Starting automation.\n")

    handler = ApplicationFormHandler(driver)

    for index, app in enumerate(applications, start=1):
        print(f"📄 Processing file {index}/{len(applications)} → {app['webfile']}")

        status = handler.process_single_application(
            webfile_number=app["webfile"],
            family_count=app["family_count"]
        )

        if status == "SLOTS_NOT_AVAILABLE":
            print("🚫 Slots are not available. Stopping automation.")
            break

        print("⏸ Please submit the application manually.")
        print("⏸ Waiting to return to application page...\n")

        handler.wait_until_back_to_application_page()

    print("🏁 Automation finished.")

if __name__ == "__main__":
    main()