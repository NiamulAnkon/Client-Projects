import time
import random
import datetime
import sys
import os
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException

from .config import (
    TARGET_MISSION,
    TARGET_IVAC,
    VISIT_PURPOSE,
    RANDOMIZE_VISIT_PURPOSE,
    VISA_TYPE,
    STOP_BEFORE_SAVE
)

class IVACBot:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def log_status(self, webfile, status):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open("logs/history.log", "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {webfile} | {status}\n")
        except Exception as e:
            print(f"⚠️ Log failed: {e}")

    def human_type(self, element, text):
        # Ensure the element is enabled before typing
        try:
            self.wait.until(lambda d: element.is_enabled())
        except Exception:
            pass

        element.clear()
        time.sleep(0.2)
        for ch in str(text):
            element.send_keys(ch)
            time.sleep(random.uniform(0.03, 0.07))
        # Trigger input/change events for frameworks that rely on them
        try:
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", element)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", element)
        except Exception:
            pass

    def safe_select(self, element_id, target, mode="text"):
        """
        Robust Combo Box handler with fallbacks.
        Modes: 'text' (Visible Text), 'value' (HTML value attribute), 'index' (0, 1, 2...)
        If selection by the requested mode fails, fallback attempts are tried.
        Returns True on success, False on failure.
        """
        for attempt in range(5):
            try:
                # Wait for the element to appear and be enabled; refetch each attempt to avoid stale references
                self.wait.until(EC.presence_of_element_located((By.ID, element_id)))
                dropdown_elem = self.driver.find_element(By.ID, element_id)
                self.wait.until(lambda d: dropdown_elem.is_enabled())

                select = Select(dropdown_elem)

                tried = []
                # Decide attempt order based on mode preference
                if mode == "value":
                    tried = ["value", "text", "index"]
                elif mode == "index":
                    tried = ["index", "value", "text"]
                else:
                    tried = ["text", "value", "index"]

                for m in tried:
                    try:
                        if m == "value":
                            select.select_by_value(str(target))
                        elif m == "index":
                            select.select_by_index(int(target))
                        else:  # text
                            select.select_by_visible_text(str(target))

                        # Small pause for AJAX-driven dependent fields
                        time.sleep(1.2)

                        # Log the actual selected option
                        try:
                            sel = select.first_selected_option
                            print(f"✅ Selected for '{element_id}': {sel.text} (value={sel.get_attribute('value')})")
                        except Exception:
                            pass

                        return True
                    except Exception as e_inner:
                        # Try next fallback
                        # Only print for the last fallback to avoid noisy logs
                        last_tried = (m == tried[-1])
                        if last_tried:
                            print(f"❌ Selection error on {element_id} (mode tried={m}): {e_inner}")
                        continue

            except (StaleElementReferenceException, WebDriverException) as e:
                print(f"🔄 Retrying {element_id} due to page refresh or driver hiccup (attempt {attempt + 1})...")
                time.sleep(1)
                continue
            except Exception as e:
                print(f"❌ Unexpected error locating {element_id}: {e}")
                time.sleep(1)
                continue

        print(f"❌ Failed to select {element_id} after multiple attempts")
        return False

    def perform_login(self, phone, login_url=None, timeout=60, debug=False):
        """
        Navigate to the login page, attempt to pre-fill the phone field and click a login/send button.
        This version has extra heuristics:
         - searches by placeholder, class, inputmode, and label
         - attempts inside iframes
         - removes readonly/disabled when safe and sets value via JS when typing fails
         - sets `debug=True` to print available inputs on the page for troubleshooting
        If automatic submission isn't possible, leave the page ready for manual completion (captcha/OTP).
        """
        try:
            url = login_url or "https://payment.ivacbd.com/"
            print(f"🔐 Opening login page: {url}")
            self.driver.get(url)

            # Wait for page to be ready
            try:
                self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            except Exception:
                pass

            time.sleep(0.8)

            # Build a list of selector strategies (tuples of (By, selector))
            phone_selectors = [
                (By.ID, "login_mobile"),
                (By.ID, "mobile"),
                (By.ID, "phone"),
                (By.NAME, "phone"),
                (By.NAME, "mobile"),
                (By.NAME, "username"),
                (By.CSS_SELECTOR, "input[type='tel']"),
                (By.CSS_SELECTOR, "input[inputmode='tel']"),
                (By.CSS_SELECTOR, "input[class*='bg-white'][class*='border-gray-300'][class*='p-2.5']"),
                (By.XPATH, "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'phone') or contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'mobile')]") ,
                (By.XPATH, "//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'phone') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'mobile')]/following::input[1]"),
                (By.XPATH, "//input[contains(@class,'phone') or contains(@class,'mobile')]") ,
            ]

            # Helper to inspect candidates and print attributes
            def inspect_candidate(elem):
                try:
                    attrs = {
                        'id': elem.get_attribute('id'),
                        'name': elem.get_attribute('name'),
                        'type': elem.get_attribute('type'),
                        'placeholder': elem.get_attribute('placeholder'),
                        'class': elem.get_attribute('class'),
                        'readonly': elem.get_attribute('readonly'),
                        'disabled': elem.get_attribute('disabled'),
                        'inputmode': elem.get_attribute('inputmode'),
                    }
                    print("   - Candidate:", attrs)
                except Exception:
                    pass

            def find_in_context():
                # Try selectors
                for sel in phone_selectors:
                    try:
                        self.wait.until(EC.presence_of_element_located(sel), timeout=4)
                        cand = self.driver.find_element(*sel)
                        if cand:
                            # Filter hidden/zero-size elements
                            try:
                                if not cand.is_displayed():
                                    if debug:
                                        print("   > Found hidden candidate, skipping (not displayed)")
                                    continue
                            except Exception:
                                pass

                            if debug:
                                inspect_candidate(cand)
                            return cand
                    except Exception:
                        continue

                # As a final fallback, list visible inputs and try to match labels/placeholder heuristics
                try:
                    inputs = self.driver.find_elements(By.XPATH, "//input[not(contains(@type,'hidden'))]")
                    if debug:
                        print(f"Found {len(inputs)} input elements on the page. Inspecting for phone-like attributes:")
                    for i in inputs:
                        p = (i.get_attribute('placeholder') or '') + ' ' + (i.get_attribute('aria-label') or '') + ' ' + (i.get_attribute('name') or '') + ' ' + (i.get_attribute('id') or '')
                        if any(x in p.lower() for x in ['phone', 'mobile', 'contact'] ) or (i.get_attribute('inputmode') == 'tel'):
                            if debug:
                                inspect_candidate(i)
                            try:
                                if i.is_displayed():
                                    return i
                            except Exception:
                                return i
                except Exception:
                    pass

                return None

            phone_elem = None

            # Try the main document context first
            phone_elem = find_in_context()

            # If not found, try each iframe (common pattern: login widgets inside frames)
            if not phone_elem:
                iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                if iframes:
                    if debug:
                        print(f"Found {len(iframes)} iframes; scanning each for phone field...")
                    for frame in iframes:
                        try:
                            self.driver.switch_to.frame(frame)
                            found = find_in_context()
                            if found:
                                phone_elem = found
                                break
                        except Exception:
                            pass
                        finally:
                            self.driver.switch_to.default_content()

            if not phone_elem:
                print("⚠️ Phone input not found: leaving page ready for manual login/captcha/OTP.")
                if debug:
                    print("Suggestion: set debug=True and re-run to list all inputs and attributes.")
                return True

            # If element is readonly or disabled, try to make it writable
            try:
                ro = phone_elem.get_attribute('readonly')
                dis = phone_elem.get_attribute('disabled')
                if ro or dis:
                    print("⚙️ Removing readonly/disabled to allow typing...")
                    try:
                        self.driver.execute_script("arguments[0].removeAttribute('readonly'); arguments[0].removeAttribute('disabled');", phone_elem)
                    except Exception:
                        pass

            except Exception:
                pass

            # Type phone - try human_type first, then JS fallback
            ident = phone_elem.get_attribute('id') or phone_elem.get_attribute('name') or 'input'
            print(f"✍️ Typing phone into {ident}")
            try:
                self.human_type(phone_elem, phone)
                # confirm value
                cur = phone_elem.get_attribute('value') or ''
                if str(phone) not in cur:
                    raise Exception('Value not set by human_type')
            except Exception:
                # Fallback: set value via JS and dispatch events
                try:
                    print("⚙️ human_type failed; setting value via JS and dispatching events...")
                    self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));", phone_elem, str(phone))
                except Exception as exjs:
                    print(f"⚠️ JS fallback failed: {exjs}")

            # Try to click an obvious button to initiate login/OTP
            btn_xpaths = [
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'login')]",
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'log in')]",
                "//button[contains(., 'Send OTP') or contains(., 'Send') or contains(., 'Continue') or contains(., 'Submit') or contains(., 'Verify')]",
                "//input[@type='submit']",
            ]

            for xp in btn_xpaths:
                try:
                    btn = self.driver.find_element(By.XPATH, xp)
                    if btn and btn.is_displayed() and btn.is_enabled():
                        print("🔁 Clicking login/send button to initiate login/OTP...")
                        try:
                            btn.click()
                        except Exception:
                            self.driver.execute_script("arguments[0].click();", btn)
                        time.sleep(0.8)
                        return True
                except Exception:
                    continue

            print("⚠️ Couldn't find a login button automatically. Please complete login manually in the browser (checkbox/captcha/OTP).")
            return True

        except Exception as e:
            print(f"❌ perform_login error: {e}")
            return False
    def fill_form(self, data):
        try:
            # 1. Webfile (Text Input)
            print(f"📝 Webfile: {data['webfile']}")
            wf = self.wait.until(EC.visibility_of_element_located((By.ID, "webfile_id")))
            self.human_type(wf, data["webfile"])

            confirm = self.wait.until(EC.visibility_of_element_located((By.ID, "first-name")))
            self.human_type(confirm, data["webfile"])
            time.sleep(2)

            # 2. Mission (Value = "1")
            print(f"📍 Mission Value: {TARGET_MISSION}")
            if not self.safe_select("center", TARGET_MISSION, mode="value"):
                raise Exception(f"Failed to select Mission '{TARGET_MISSION}'")

            # 3. IVAC (can be provided as visible text or value in config)
            print(f"📍 IVAC: {TARGET_IVAC}")
            ivac_mode = "value" if str(TARGET_IVAC).isdigit() else "text"
            if not self.safe_select("center", TARGET_IVAC, mode=ivac_mode):
                raise Exception(f"Failed to select IVAC '{TARGET_IVAC}' (mode={ivac_mode})")

            # 4. Visa Type (Value = "13")
            print(f"🎫 Visa Type Value: {VISA_TYPE}")
            if not self.safe_select("visa_type", VISA_TYPE, mode="value"):
                raise Exception(f"Failed to select Visa Type '{VISA_TYPE}'")

            # 5. Family Count (Index: 0 for 1 member, 1 for 2 members, etc.)
            # The site usually maps "1 member" to value "0"
            f_count_val = str(int(data.get("family_count", 1)) - 1)
            print(f"👨‍👩‍👧‍👦 Family Count Value: {f_count_val}")
            if not self.safe_select("family_count", f_count_val, mode="value"):
                raise Exception(f"Failed to select Family Count '{f_count_val}'")

            # 6. Visit Purpose (Text Input)
            print("🎯 Visit Purpose...")
            self.wait.until(lambda d: d.find_element(By.ID, "visit_purpose").is_enabled())
            vp = self.driver.find_element(By.ID, "visit_purpose")
            purpose = random.choice(VISIT_PURPOSE) if RANDOMIZE_VISIT_PURPOSE else VISIT_PURPOSE[0]
            if len(purpose) < 15: purpose += " for medical care"
            self.human_type(vp, purpose)

            print("✅ FORM FILLED SUCCESSFULLY")
            self.log_status(data["webfile"], "Filled")

            if STOP_BEFORE_SAVE:
                # Only pause if running interactively
                if sys.stdin and sys.stdin.isatty():
                    print("⏸️ STOP_BEFORE_SAVE is ON. Press ENTER in terminal after reviewing...")
                    input()
                else:
                    print("⚠️ STOP_BEFORE_SAVE is ON but no interactive terminal detected. Continuing...")

            save_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Save')]")))
            save_btn.click()
            print("💾 Save Clicked.")
            self.log_status(data["webfile"], "Saved")

        except Exception as e:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            webfile = data.get("webfile", "UNKNOWN")

            # Print a concise message to the console
            print(f"❌ Form Fill Error ({type(e).__name__}): {e}")

            # Ensure logs/errors directory exists
            error_dir = os.path.join("logs", "errors")
            try:
                os.makedirs(error_dir, exist_ok=True)
            except Exception:
                pass

            # Save full traceback and some driver info
            err_file = os.path.join(error_dir, f"error_{webfile}_{ts}.log")
            try:
                with open(err_file, "w", encoding="utf-8") as f:
                    f.write(f"Timestamp: {ts}\n")
                    f.write(f"Webfile: {webfile}\n\n")
                    f.write("Traceback:\n")
                    f.write(traceback.format_exc())
                    f.write("\n\nDriver capabilities:\n")
                    try:
                        f.write(repr(self.driver.capabilities) + "\n")
                    except Exception as ex_caps:
                        f.write(f"Failed to read capabilities: {ex_caps}\n")

                    # Browser console logs if supported
                    try:
                        logs = self.driver.get_log('browser')
                        f.write("\nBrowser console logs:\n")
                        for entry in logs:
                            f.write(repr(entry) + "\n")
                    except Exception as ex_logs:
                        f.write(f"Failed to get browser logs: {ex_logs}\n")

                print(f"🔍 Saved error details: {err_file}")
            except Exception as exw:
                print(f"⚠️ Failed to write error file: {exw}")

            # Try screenshot
            try:
                screenshot_path = os.path.join("logs", f"screenshot_{webfile}_{ts}.png")
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 Screenshot saved: {screenshot_path}")
            except Exception as exs:
                print(f"⚠️ Failed to take screenshot: {exs}")

            # Save page source
            try:
                page_path = os.path.join("logs", f"page_{webfile}_{ts}.html")
                with open(page_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print(f"📄 Page source saved: {page_path}")
            except Exception as exps:
                print(f"⚠️ Failed to save page source: {exps}")

            # Log and re-raise for upstream handling
            self.log_status(webfile, f"Error: {str(e)[:200]}")
            raise
