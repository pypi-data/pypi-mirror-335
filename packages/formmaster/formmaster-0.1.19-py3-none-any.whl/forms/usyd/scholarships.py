'''
<div class="sv-form-horizontal">
    <div class="sv-form-group">
        <label class="sv-col-md-3 sv-control-label">Have you been awarded a scholarship or sponsorship to support your studies? *</label>
        <div class="sv-col-md-4">
            <div class="sv-radio"><label><input name="IPQ_APONSH13" id="IPQ_APONSH13A" type="radio" value="Y" onclick="check_IPQ_APONSH13();">&nbsp;Yes</label></div>
            <div class="sv-radio"><label><input name="IPQ_APONSH13" id="IPQ_APONSH13B" type="radio" value="N" onclick="check_IPQ_APONSH13();">&nbsp;No</label></div>
        </div>
    </div>
    <div class="sv-form-group" id="section8" style="display: none;">
        <label for="IPQ_APONSH14" class="sv-col-md-3 sv-control-label">What is the name of the scholarship or sponsor? *</label>
        <div class="sv-col-md-4">
            <input name="IPQ_APONSH14" id="IPQ_APONSH14" class="sv-form-control" type="text" maxlength="100" value="">
        </div>
    </div>
    <div class="sv-form-group">
        <label class="sv-col-md-3 sv-control-label">Have you applied for a scholarship (for which your application is pending)? *</label>
        <div class="sv-col-md-4">
            <div class="sv-radio"><label><input name="IPQ_APONSH15" id="IPQ_APONSH15A" type="radio" value="Y" onclick="check_IPQ_APONSH15();">&nbsp;Yes</label></div>
            <div class="sv-radio"><label><input name="IPQ_APONSH15" id="IPQ_APONSH15B" type="radio" value="N" onclick="check_IPQ_APONSH15();" data-gtm-form-interact-field-id="0">&nbsp;No</label></div>
        </div>
    </div>
    <div class="sv-form-group" id="section9" style="display: none;">
        <label for="IPQ_APONSH16" class="sv-col-md-3 sv-control-label">What is the name of the scholarship? *</label>
        <div class="sv-col-md-4">
            <input name="IPQ_APONSH16" id="IPQ_APONSH16" class="sv-form-control" type="text" maxlength="100" value="">
        </div>
    </div>
</div>
'''


import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from forms.utils.form_utils import set_value_by_id, ensure_radio_selected

class Scholarships:
    def __init__(self, driver, data):
        self.driver = driver
        self.data = data

    def run(self):
        students = self.data
        driver = self.driver
        personal_info = students[-1][0]
        
        # Check if the student has been awarded a scholarship or sponsorship
        has_scholarship = personal_info.get('has_scholarship', False)
        
        if has_scholarship:
            # Select "Yes" for scholarship awarded
            ensure_radio_selected(driver, "IPQ_APONSH13A")
            
            # Wait for the scholarship name field to appear
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "section8"))
                )
                
                # Fill in scholarship name if available
                scholarship_name = personal_info.get('scholarship_name', '')
                if not scholarship_name:
                    scholarship_name = "Study Abroad Scholarship"  # Default placeholder
                    
                set_value_by_id(driver, "IPQ_APONSH14", scholarship_name)
            except TimeoutException:
                print("Warning: Scholarship name field did not appear after selecting Yes")
        else:
            # Select "No" for scholarship awarded
            ensure_radio_selected(driver, "IPQ_APONSH13B")
        
        # Check if the student has applied for a pending scholarship
        has_pending_scholarship = personal_info.get('has_pending_scholarship', False)
        
        if has_pending_scholarship:
            # Select "Yes" for pending scholarship
            ensure_radio_selected(driver, "IPQ_APONSH15A")
            
            # Wait for the pending scholarship name field to appear
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "section9"))
                )
                
                # Fill in pending scholarship name if available
                pending_scholarship_name = personal_info.get('pending_scholarship_name', '')
                if not pending_scholarship_name:
                    pending_scholarship_name = "International Student Merit Scholarship"  # Default
                    
                set_value_by_id(driver, "IPQ_APONSH16", pending_scholarship_name)
            except TimeoutException:
                print("Warning: Pending scholarship name field did not appear after selecting Yes")
        else:
            # Select "No" for pending scholarship
            ensure_radio_selected(driver, "IPQ_APONSH15B")
    