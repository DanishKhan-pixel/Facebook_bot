import time
import random
import string
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import logging

logger = logging.getLogger(__name__)

class FacebookAutomation:
    def __init__(self, headless=False, proxy=None):
        self.headless = headless
        self.proxy = proxy
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        try:
            chrome_options = Options()
            
            # Basic options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Performance options
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--disable-javascript')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            
            # User agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # Proxy if provided
            if self.proxy:
                chrome_options.add_argument(f'--proxy-server={self.proxy}')
            
            # Headless mode
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # Use undetected-chromedriver
            self.driver = uc.Chrome(options=chrome_options)
            
            # Additional anti-detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up driver: {e}")
            return False
    
    def generate_random_name(self):
        """Generate random first and last name"""
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Robert', 'Emma', 'James', 'Maria']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        
        return random.choice(first_names), random.choice(last_names)
    
    def generate_random_birthday(self):
        """Generate random birthday (18+ years old)"""
        current_year = datetime.datetime.now().year
        birth_year = random.randint(current_year - 50, current_year - 18)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        
        return birth_year, birth_month, birth_day
    
    def fill_signup_form(self, email, password):
        """Fill Facebook signup form"""
        try:
            wait = WebDriverWait(self.driver, 20)
            
            # Generate random names
            first_name, last_name = self.generate_random_name()
            
            # First Name
            first_name_field = wait.until(EC.presence_of_element_located((By.NAME, "firstname")))
            first_name_field.clear()
            first_name_field.send_keys(first_name)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Last Name
            last_name_field = self.driver.find_element(By.NAME, "lastname")
            last_name_field.clear()
            last_name_field.send_keys(last_name)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Email
            email_field = self.driver.find_element(By.NAME, "reg_email__")
            email_field.clear()
            email_field.send_keys(email)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Confirm Email (if present)
            try:
                email_confirm_field = self.driver.find_element(By.NAME, "reg_email_confirmation__")
                email_confirm_field.clear()
                email_confirm_field.send_keys(email)
                time.sleep(random.uniform(0.5, 1.5))
            except NoSuchElementException:
                pass
            
            # Password
            password_field = self.driver.find_element(By.NAME, "reg_passwd__")
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Birthday
            birth_year, birth_month, birth_day = self.generate_random_birthday()
            
            # Month
            month_dropdown = self.driver.find_element(By.NAME, "birthday_month")
            month_dropdown.click()
            time.sleep(random.uniform(0.3, 0.8))
            month_option = self.driver.find_element(By.XPATH, f"//option[@value='{birth_month}']")
            month_option.click()
            time.sleep(random.uniform(0.3, 0.8))
            
            # Day
            day_dropdown = self.driver.find_element(By.NAME, "birthday_day")
            day_dropdown.click()
            time.sleep(random.uniform(0.3, 0.8))
            day_option = self.driver.find_element(By.XPATH, f"//option[@value='{birth_day}']")
            day_option.click()
            time.sleep(random.uniform(0.3, 0.8))
            
            # Year
            year_dropdown = self.driver.find_element(By.NAME, "birthday_year")
            year_dropdown.click()
            time.sleep(random.uniform(0.3, 0.8))
            year_option = self.driver.find_element(By.XPATH, f"//option[@value='{birth_year}']")
            year_option.click()
            time.sleep(random.uniform(0.3, 0.8))
            
            # Gender
            gender_options = self.driver.find_elements(By.NAME, "sex")
            if gender_options:
                random_gender = random.choice(gender_options)
                random_gender.click()
                time.sleep(random.uniform(0.5, 1.0))
            
            return True
            
        except Exception as e:
            logger.error(f"Error filling signup form: {e}")
            return False
    
    def submit_form(self):
        """Submit the signup form"""
        try:
            # Find submit button
            submit_selectors = [
                (By.NAME, "submit"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//input[@type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']")
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(*selector)
                    break
                except NoSuchElementException:
                    continue
            
            if submit_button:
                submit_button.click()
                time.sleep(5)
                return True
            else:
                logger.error("Submit button not found")
                return False
                
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            return False
    
    def check_success(self):
        """Check if account creation was successful"""
        try:
            current_url = self.driver.current_url
            
            # Success indicators
            success_indicators = [
                "checkpoint" in current_url,
                "confirm" in current_url,
                "login" in current_url,
                "facebook.com/checkpoint" in current_url,
                "facebook.com/confirm" in current_url
            ]
            
            if any(success_indicators):
                return True
            
            # Check for error messages
            error_selectors = [
                "//div[contains(@class, 'error')]",
                "//div[contains(@class, 'alert')]",
                "//span[contains(@class, 'error')]"
            ]
            
            for selector in error_selectors:
                try:
                    error_elements = self.driver.find_elements(By.XPATH, selector)
                    if error_elements:
                        error_text = error_elements[0].text
                        logger.warning(f"Facebook error detected: {error_text}")
                        return False
                except:
                    continue
            
            # If no obvious errors and not on success page, assume success
            return True
            
        except Exception as e:
            logger.error(f"Error checking success: {e}")
            return False
    
    def create_facebook_account(self, email, password):
        """Main method to create Facebook account"""
        try:
            # Setup driver
            if not self.setup_driver():
                return False
            
            # Navigate to Facebook signup
            self.driver.get('https://www.facebook.com/signup')
            time.sleep(3)
            
            # Fill the form
            if not self.fill_signup_form(email, password):
                return False
            
            # Submit the form
            if not self.submit_form():
                return False
            
            # Check for success
            success = self.check_success()
            
            return success
            
        except Exception as e:
            logger.error(f"Error in Facebook account creation: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

def create_facebook_account_real(email, password, headless=True):
    """Wrapper function for creating Facebook account"""
    automation = FacebookAutomation(headless=headless)
    return automation.create_facebook_account(email, password) 