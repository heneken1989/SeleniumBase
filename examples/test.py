from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import platform
import shutil
import time

def check_profile_data(profile_path):
    """Check if the profile directory contains Chrome profile data"""
    key_files = ['Default', 'First Run', 'Local State', 'Preferences']
    if os.path.exists(profile_path):
        files = os.listdir(profile_path)
        print(f"📂 Profile directory contents: {files}")
        
        # Check Default directory for cookies and login data
        default_path = os.path.join(profile_path, 'Default')
        if os.path.exists(default_path):
            default_files = os.listdir(default_path)
            print(f"📂 Default directory contents: {default_files}")
            if 'Cookies' in default_files and 'Login Data' in default_files:
                print("✅ Found cookies and login data!")
                return True
        
        print("❌ Missing cookies or login data in profile")
        return False
    return False

def setup_chrome_profile():
    # Try to find existing profile with login data
    profile_locations = [
        "examples/SeleniumBase/chrome_profile",  # Your copied profile
        "chrome_profile",                        # Root directory
        "data/chrome_profile",                   # Data directory
        "SeleniumBase/data/chrome_profile"       # SeleniumBase directory
    ]
    
    # Try each location
    for location in profile_locations:
        if os.path.exists(location):
            abs_path = os.path.abspath(location)
            print(f"🔍 Checking profile at: {abs_path}")
            if check_profile_data(abs_path):
                print(f"🔄 Using existing profile from: {abs_path}")
                # Ensure permissions in Docker
                if platform.system() == 'Linux':
                    os.system(f'chmod -R 777 {abs_path}')
                return abs_path
    
    # If no valid profile found, use the first location
    default_profile = os.path.abspath(profile_locations[0])
    os.makedirs(default_profile, exist_ok=True)
    if platform.system() == 'Linux':
        os.system(f'chmod -R 777 {default_profile}')
    print(f"⚠️ No valid profile found, using: {default_profile}")
    return default_profile

# Set up Chrome profile
chrome_profile = setup_chrome_profile()
print(f"🔧 Final Chrome profile path: {chrome_profile}")

def try_another_way(sb):
    try:
        # Scroll down gradually to find the element
        for i in range(0, 1000, 200):  # Scroll in steps of 200px up to 1000px
            sb.execute_script(f"window.scrollTo(0, {i});")
            sb.sleep(0.5)  # Brief pause between scrolls
            
        # Find the specific parent div with jscontroller
        element = sb.find_element("//div[@jscontroller='f8Gu1e'][@jsname='eBSUOb']")
        sb.sleep(1)  # Brief pause after scrolling
        
        # Try regular click first
        try:
            sb.click_element(element)
            print("🔄 Found and clicked 'Try another way' using regular click")
        except:
            # If regular click fails, try JavaScript click
            print("⚠️ Regular click failed, trying JavaScript click...")
            # Try clicking the button inside the div
            try:
                button = sb.find_element("//button[.//span[contains(text(), 'Try another way')]]")
                sb.execute_script("arguments[0].click();", button)
                print("🔄 Clicked 'Try another way' button using JavaScript")
            except:
                # If button click fails, try the parent div
                sb.execute_script("arguments[0].click();", element)
                print("🔄 Clicked parent div using JavaScript")
        
        sb.sleep(3)
    except Exception as e:
        print("⚠️ 'Try another way' not found:", str(e))

def get_next_unused_backup_code():
    all_codes = [
         "6576618741", "9789910562"
    ]
    used_path = "used_codes.txt"

    try:
        with open(used_path, "r") as f:
            used_codes = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        used_codes = []

    for code in all_codes:
        if code not in used_codes:
            print(f"🔐 Using backup code: {code}")
            with open(used_path, "a") as f:
                f.write(code + "\n")
            return code

    raise Exception("❌ No unused backup codes available.")

# Additional Chrome options for better profile handling
chrome_options = {
    "uc": True,
    "headless": False,
    "user_data_dir": chrome_profile,

}

def check_login_status(sb):
    """Check if logged into Gmail account 1 inbox."""
    target_url = "https://mail.google.com/mail/u/0/#inbox"
    
    # Wait for possible redirects
    for _ in range(5):
        current_url = sb.get_current_url()
        print(f"🌐 Checking URL: {current_url}")
        
        if current_url == target_url:
            return True
        
        time.sleep(1)
    
    return False

with SB(**chrome_options) as sb:

        # Try to access Gmail directly - should work if profile is valid
        print("🔄 Attempting to access Gmail...")
        sb.open("https://mail.google.com")
        sb.save_screenshot_to_logs("step1_gmail_direct.png")
        
        # Check if we're already logged in
        if check_login_status(sb):
            print("✅ Successfully accessed Gmail with saved profile!")
            sb.sleep(3)
            exit(0)
        
        print("⚠️ Not logged in, falling back to manual login...")
        # Step 1: Open Gmail login page
        sb.open("https://accounts.google.com/")
        sb.save_screenshot_to_logs("step1_open_gmail.png")  #
        text = sb.get_current_url()
        if "workspace.google.com" in sb.get_current_url():
            try:
                # Try by span text
                sb.click('//span[text()="Sign in"]')
            except:
                try:
                    # Try by aria-label
                    sb.click('//a[@aria-label="Sign into Gmail"]')
                except:
                    try:
                        # Try by href containing signinchooser
                        sb.click('//a[contains(@href, "signinchooser")]')
                    except:
                        # Try by class and span combination
                        sb.click('//a[contains(@class, "header__aside__button")]//span[contains(@class, "button__label")]')
            sb.save_screenshot_to_logs("workspace_signin_clicked.png")
        
        # Step 2: Enter email address and press Next
        sb.type('input[type="email"]', 'huyhien1989@gmail.com\n')  # Replace with your email
        print("Typed Email Address")
        try:
            sb.click("#identifierNext")
            print("✅ Clicked Next button normally.")
        except Exception as e:
            print(f"⚠️ Normal click failed: {e}")
            print("👉 Trying JavaScript click...")
            try:
                element = sb.find_element("#identifierNext")  # <- first, get fresh element
                sb.execute_script("arguments[0].click();", element)  # <- then click it
                print("✅ JavaScript clicked Next button.")
            except Exception as js_error:
                print(f"❌ JavaScript click also failed: {js_error}")
                raise  # Re-raise if both methods fail
        
        sb.save_screenshot_to_logs("step2_email_entered.png")  # Screenshot after email entered
        
        # Wait for the password field to load
        sb.wait_for_element('input[type="password"]', timeout=20)
        # Step 3: Enter password and press Next
        sb.type('input[type="password"]', 'Nguyenthihongdung1989@' + Keys.RETURN)
        sb.save_screenshot_to_logs("step3_password_entered.png")  # Screenshot after password entered
        # click try another way if present
        sb.sleep(5)
        try_another_way(sb)
        # Wait for and click on the security code option
        sb.sleep(5)
        try:
            # Try by XPath with text content
            sb.click('//div[@class="l5PPKe" and contains(text(), "Use your phone or tablet")]')
        except:
            # Try the original selector as fallback
            sb.click("*:contains('Use your phone or tablet to get a security code (even if it's offline)')")
        
        sb.save_screenshot_to_logs("step4_security_option_clicked.png")

        # Step5 Enter the backup code
        backup_code = get_next_unused_backup_code()
        print("🔍 Searching for any visible text input field...")
        # Wait for input field to be present and visible
        sb.wait_for_element("input", timeout=10)
        # Enter the backup code using SeleniumBase's type method
        sb.type("input", backup_code + Keys.RETURN)
        sb.sleep(5)
        # Take a screenshot of the result
        sb.save_screenshot_to_logs("step5_backup_code_entered.png")
        print("✅ Backup code entered successfully")
        sb.open("https://mail.google.com/mail/u/0/#inbox")
        sb.sleep(5)
        if check_login_status(sb):
            print("✅ Successfully logged in to Gmail!")
        else:
            print("❌ Failed to log in to Gmail after entering backup code.")
        sb.save_screenshot_to_logs("step6_gmail_opened.png")
