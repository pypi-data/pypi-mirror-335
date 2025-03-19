import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from forms.utils.form_utils import set_value_by_id, check_button_by_id

'''
<div class="sv-panel-body">
	If you have already applied for a University of Sydney course please advise us below.<br><br>
	<div class="sv-form-container">
		<div class="sv-form-horizontal">
			<div class="sv-form-group">
				<label class="sv-col-md-3 sv-control-label">Are you a current applicant at the University of Sydney? *</label>
				<div class="sv-col-md-4">
					<div class="sv-radio"><label><input name="IPQ_APONPAP" id="IPQ_APONPAPA" type="radio" value="Y" onclick="check_IPQ_APONPAP();">&nbsp;Yes</label></div>
					<div class="sv-radio"><label><input name="IPQ_APONPAP" id="IPQ_APONPAPB" type="radio" value="N" onclick="check_IPQ_APONPAP();">&nbsp;No</label></div>
				</div>
			</div>
			<div class="sv-form-group" id="section4" style="display: none;">
				<label for="IPQ_APONPAPN" class="sv-col-md-3 sv-control-label">Applicant ID *</label>
				<div class="sv-col-md-4">
					<input name="IPQ_APONPAPN" id="IPQ_APONPAPN" class="sv-form-control" type="text" maxlength="12" value="">
					<small>Your Applicant ID is the unique reference number that you were sent to track your application.</small>
				</div>
			</div>
		</div>
	</div>
</div>
'''

class PersonalInfoCouseApplications:
    def __init__(self, driver, data):
        self.driver = driver
        self.data = data

    def run(self):
        students = self.data
        driver = self.driver
        personal_info = students[-1][0]
        
        # Check if the student is a current applicant
        is_current_applicant = personal_info.get('is_current_applicant', False)
        
        # Select the appropriate radio button
        if is_current_applicant:
            check_button_by_id(driver, "IPQ_APONPAPA")  # Yes
            
            # Wait for the applicant ID field to appear
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "IPQ_APONPAPN"))
            )
            
            # Fill in applicant ID if available
            applicant_id = personal_info.get('applicant_id', '')
            if applicant_id:
                set_value_by_id(driver, "IPQ_APONPAPN", applicant_id)
            else:
                # If no applicant ID is provided but selected "Yes", use a default
                set_value_by_id(driver, "IPQ_APONPAPN", "APP12345678")
        else:
            # Select "No"
            check_button_by_id(driver, "IPQ_APONPAPB")
