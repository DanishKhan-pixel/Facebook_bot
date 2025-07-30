import time
import re
import logging
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .email_generator import wait_for_otp, check_email_for_otp
from .facebook_automation import FacebookAutomation

logger = logging.getLogger(__name__)

class FacebookVerificationHandler:
    def __init__(self, driver=None):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20) if driver else None
    
    def handle_phone_verification(self, phone_number: str) -> bool:
        """Handle phone number verification"""
        try:
            if not self.driver:
                return False
            
            # Look for phone verification form
            phone_field = self.driver.find_element(By.NAME, "phone_number")
            phone_field.clear()
            phone_field.send_keys(phone_number)
            time.sleep(1)
            
            # Submit phone verification
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in phone verification: {e}")
            return False
    
    def handle_email_verification(self, email: str) -> bool:
        """Handle email verification with OTP"""
        try:
            if not self.driver:
                return False
            
            # Wait for OTP to arrive in email
            otp = wait_for_otp(email, timeout=120)
            if not otp:
                logger.error("No OTP received in email")
                return False
            
            # Find OTP input field
            otp_field = self.driver.find_element(By.NAME, "code")
            otp_field.clear()
            otp_field.send_keys(otp)
            time.sleep(1)
            
            # Submit OTP
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in email verification: {e}")
            return False
    
    def handle_captcha(self) -> bool:
        """Handle CAPTCHA challenges"""
        try:
            if not self.driver:
                return False
            
            # Look for CAPTCHA elements
            captcha_selectors = [
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[contains(@class, 'captcha')]",
                "//img[contains(@alt, 'captcha')]"
            ]
            
            for selector in captcha_selectors:
                try:
                    captcha_element = self.driver.find_element(By.XPATH, selector)
                    logger.warning("CAPTCHA detected - manual intervention may be required")
                    time.sleep(10)  # Wait for manual solving
                    return True
                except NoSuchElementException:
                    continue
            
            return True  # No CAPTCHA found
            
        except Exception as e:
            logger.error(f"Error handling CAPTCHA: {e}")
            return False
    
    def handle_security_check(self) -> bool:
        """Handle Facebook security checks"""
        try:
            if not self.driver:
                return False
            
            current_url = self.driver.current_url
            
            # Check for various security check pages
            security_indicators = [
                "checkpoint" in current_url,
                "security" in current_url,
                "confirm" in current_url,
                "verify" in current_url
            ]
            
            if any(security_indicators):
                logger.info("Security check detected")
                
                # Handle different types of security checks
                if "phone" in current_url.lower():
                    return self.handle_phone_verification("")
                elif "email" in current_url.lower():
                    return self.handle_email_verification("")
                elif "captcha" in current_url.lower():
                    return self.handle_captcha()
                else:
                    # Generic security check - wait and continue
                    time.sleep(5)
                    return True
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling security check: {e}")
            return False
    
    def complete_account_setup(self) -> bool:
        """Complete the account setup process"""
        try:
            if not self.driver:
                return False
            
            # Handle various post-creation steps
            current_url = self.driver.current_url
            
            # Skip profile setup if possible
            if "profile" in current_url or "setup" in current_url:
                try:
                    skip_button = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Skip')]")
                    skip_button.click()
                    time.sleep(2)
                except NoSuchElementException:
                    pass
            
            # Handle friend suggestions
            if "friends" in current_url or "suggestions" in current_url:
                try:
                    skip_button = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Skip')]")
                    skip_button.click()
                    time.sleep(2)
                except NoSuchElementException:
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error completing account setup: {e}")
            return False

def verify_facebook_account(email: str, password: str, headless: bool = True) -> bool:
    """Complete Facebook account verification process"""
    try:
        # Create new automation instance for verification
        automation = FacebookAutomation(headless=headless)
        
        if not automation.setup_driver():
            return False
        
        try:
            # Navigate to Facebook login
            automation.driver.get('https://www.facebook.com/login')
            time.sleep(3)
            
            # Login with created account
            email_field = automation.driver.find_element(By.NAME, "email")
            email_field.send_keys(email)
            time.sleep(1)
            
            password_field = automation.driver.find_element(By.NAME, "pass")
            password_field.send_keys(password)
            time.sleep(1)
            
            login_button = automation.driver.find_element(By.NAME, "login")
            login_button.click()
            time.sleep(5)
            
            # Handle verification if needed
            verification_handler = FacebookVerificationHandler(automation.driver)
            
            # Check for security checks
            if not verification_handler.handle_security_check():
                return False
            
            # Complete account setup
            if not verification_handler.complete_account_setup():
                return False
            
            # Check if login was successful
            current_url = automation.driver.current_url
            if "facebook.com/home" in current_url or "facebook.com/" in current_url:
                return True
            else:
                return False
                
        finally:
            automation.driver.quit()
            
    except Exception as e:
        logger.error(f"Error in account verification: {e}")
        return False

def extract_otp_from_email(email_content: str) -> Optional[str]:
    """Extract OTP code from email content"""
    try:
        # Common OTP patterns
        patterns = [
            r'\b\d{6}\b',  # 6-digit code
            r'\b\d{4}\b',  # 4-digit code
            r'verification code[:\s]*(\d+)',
            r'code[:\s]*(\d+)',
            r'OTP[:\s]*(\d+)',
            r'(\d{4,6})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, email_content, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting OTP: {e}")
        return None 