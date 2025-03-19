'''
<div class="sv-panel-body">
        If you are lodging this application following a University of Sydney roadshow, exhibition or recruitment event you may be eligible for an application processing fee waiver. Please upload a copy of the voucher you recieved at the event to support your request.<br><br>
        <div class="sv-form-container">
            <div class="sv-form-horizontal">
                <div class="sv-form-group">
                    <label class="sv-col-md-3 sv-control-label">Is this application eligible for a fee waiver related to a recruitment event? *</label>
                    <div class="sv-col-md-4">
                        
                        <div class="sv-radio"><label><input name="IPQ_APONLEVV" id="IPQ_APONLEVV" type="radio" value="Y">&nbsp;Yes</label></div>
                        
                        
                        <div class="sv-radio"><label><input name="IPQ_APONLEVV" id="IPQ_APONLEVV" type="radio" value="N">&nbsp;No</label></div>
                        
                    </div>
                </div>
            </div>
        </div>
    </div>
'''

import re
from selenium.webdriver.common.by import By
from forms.utils.form_utils import select_radio_by_value

class PersonalInfoFeeWeaver:
    def __init__(self, driver, data):
        self.driver = driver
        self.data = data

    def run(self):
        students = self.data
        driver = self.driver
        personal_info = students[-1][0]
        
        # Check if the application is eligible for a fee waiver
        is_fee_waiver_eligible = personal_info.get('is_fee_waiver_eligible', False)
        
        # Note: Both radio buttons have the same ID in the HTML (IPQ_APONLEVV)
        # We need to select them by name and value instead
        if is_fee_waiver_eligible:
            # Select "Yes" for fee waiver eligibility
            select_radio_by_value(driver, "IPQ_APONLEVV", "Y")
        else:
            # Select "No" for fee waiver eligibility
            select_radio_by_value(driver, "IPQ_APONLEVV", "N")
    
    # Methods removed as they're now imported from form_utils.py
