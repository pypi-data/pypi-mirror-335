'''
<fieldset>
                      <legend>
                        
                      </legend>
                      <div class="sv-form-group">
                        <label for="MUA_CODE.DUMMY.MENSYS">
                          ID number
                        </label>
                        <input type="text" name="MUA_CODE.DUMMY.MENSYS.1" value="" id="MUA_CODE.DUMMY.MENSYS" class="sv-form-control" data-gtm-form-interact-field-id="0">
                      </div>
                      <div class="sv-form-group">
                        <label for="PASSWORD.DUMMY.MENSYS">
                          Password
                        </label>
                        <input type="password" name="PASSWORD.DUMMY.MENSYS.1" value="" id="PASSWORD.DUMMY.MENSYS" class="sv-form-control" data-gtm-form-interact-field-id="1"> 
                      </div>
                      <div class="sv-row">
                       <div class="sv-col-sm-6 sv-col-sm-push-6">
                         <div class="sv-form-group">
                           <input type="submit" name="BP101.DUMMY_B.MENSYS" value="Log in" class="sv-btn sv-btn-block sv-btn-primary" id="siwLgnLogIn">
                          </div>
                        </div>
                        <div class="sv-col-sm-6 sv-col-sm-pull-6">
                          <div class="sv-form-group">
                            <!--<x-subst type="html" name="FORGOTTEN_BUTTON.DUMMY.MENSYS">
                              <a href="#" class="sv-btn sv-btn-block sv-btn-default" id="">Forgotten your password?</a>
                            </x-subst>-->
							 <a href="http://sydney.edu.au/students/log-in-to-university-systems/log-in-to-sydney-student.html" class="sv-btn sv-btn-block sv-btn-default" id="">Need help logging in?</a>
                          </div>
                        </div>
                      </div>
                      <!--<hr>
                      <div class="sv-row">
                        <div class="sv-col-sm-12 sv-text-center">                                                   
                          <x-subst type="html" name="BP009.DUMMY_B.MENSYS">Or login using...</x-subst>                                                 
                        </div>
                      </div>
                      <br>
                      <div class="sv-row">
                        <div class="sv-col-sm-12">
                          <div class="sv-col-sm-2 sv-col-xs-4">
                            <x-subst type="html" name="FACEBOOK_BUTTON.DUMMY.MENSYS">Facebook</x-subst>
                          </div>
                          <div class="sv-col-sm-2 sv-col-xs-4">
                            <x-subst type="html" name="GOOGLE_BUTTON.DUMMY.MENSYS">Google</x-subst>
                          </div>
                          <div class="sv-col-sm-2 sv-col-xs-4">
                            <x-subst type="html" name="MICROSOFT_BUTTON.DUMMY.MENSYS">Microsoft Live</x-subst>
                          </div>
                          <div class="sv-col-sm-2 sv-col-xs-4">
                            <x-subst type="html" name="LINKEDIN_BUTTON.DUMMY.MENSYS">LinkedIn</x-subst>
                          </div>
                          <div class="sv-col-sm-2 sv-col-xs-4">
                            <x-subst type="html" name="WEIBO_BUTTON.DUMMY.MENSYS">Weibo</x-subst>
                          </div>
                          <div class="sv-col-sm-2 sv-col-xs-4">
                            <x-subst type="html" name="SALESFORCE_BUTTON.DUMMY.MENSYS">SalesForce</x-subst>
                          </div>                          
                        </div>
                      </div>-->
                    </fieldset>
'''

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger import get_logger

class LoginForm:
    def __init__(self, driver, data):
        self.driver = driver
        self.data = data

    def run(self):
        """
        Fill the USYD login form with student credentials and submit
        """
        try:
            # Wait for elements to be present to avoid "no such element" error
            wait = WebDriverWait(self.driver, 10)
            
            # Find and fill ID number field
            id_field = wait.until(EC.visibility_of_element_located(
                (By.ID, "MUA_CODE.DUMMY.MENSYS")
            ))
            id_field.clear()
            id_field.send_keys(self.username)
            
            # Find and fill password field
            password_field = wait.until(EC.visibility_of_element_located(
                (By.ID, "PASSWORD.DUMMY.MENSYS")
            ))
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Find and click login button
            login_button = wait.until(EC.element_to_be_clickable(
                (By.ID, "siwLgnLogIn")
            ))
            login_button.click()
            
            get_logger().info("Create profile finished.")

            # Wait for login process
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return False