'''
<div class="sv-panel-body">
If you a current full time or part time member of staff at the University of Sydney please advise us below.<br><br>
<div class="sv-form-container">
    <div class="sv-form-horizontal">
        <div class="sv-form-group">
            <label class="sv-col-md-3 sv-control-label">Are you a current University of Sydney staff member? *</label>
                <div class="sv-col-md-4">
                    
                    <div class="sv-radio"><label><input name="IPQ_APONLSSB1" id="IPQ_APONLSSB1A" type="radio" value="Y" onclick="check_IPQ_APONLSSB1();">&nbsp;Yes</label></div>
                    
                    
                        <div class="sv-radio"><label><input name="IPQ_APONLSSB1" id="IPQ_APONLSSB1B" type="radio" value="N" onclick="check_IPQ_APONLSSB1();">&nbsp;No</label></div>
                    
                        <small>Please indicate whether you are currently a full time or part time staff member at the University of Sydney.</small>
                </div>
            </div>
                    
        </div>
    </div>
</div>
'''

import re
from selenium.webdriver.common.by import By
from forms.utils.form_utils import check_button_by_id, set_value_by_id

class PersonalInfoEnrollmentStatus:
    def __init__(self, driver, data):
        self.driver = driver
        self.data = data

    def run(self):
        students = self.data
        driver = self.driver
        personal_info = students[-1][0]
        
        # Check if the person is a staff member at the University of Sydney
        is_staff_member = personal_info.get('is_staff_member', False)
        
        if is_staff_member:
            # Select "Yes" for current staff member
            check_button_by_id(driver, "IPQ_APONLSSB1A")
        else:
            # Select "No" for current staff member
            check_button_by_id(driver, "IPQ_APONLSSB1B")
    
    # Methods removed as they're now imported from form_utils.py

