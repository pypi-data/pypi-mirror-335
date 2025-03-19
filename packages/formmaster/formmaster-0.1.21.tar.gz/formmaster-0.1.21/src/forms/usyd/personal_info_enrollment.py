import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from forms.utils.form_utils import set_value_by_id, check_button_by_id

'''
<div class="sv-panel-body">
	If you have already enrolled in a University of Sydney course please advise us below.<br><br>
	<div class="sv-form-container">
		<div class="sv-form-horizontal">
			<div class="sv-form-group">
				<label class="sv-col-md-3 sv-control-label">Are you a current University of Sydney student? *</label>
				<div class="sv-col-md-4">
					
					<div class="sv-radio"><label><input name="IPQ_APONLCES1" id="IPQ_APONLCES1A" type="radio" value="Y" onclick="check_IPQ_APONLCES1();">&nbsp;Yes</label></div>
					
					
					<div class="sv-radio"><label><input name="IPQ_APONLCES1" id="IPQ_APONLCES1B" type="radio" value="N" onclick="check_IPQ_APONLCES1();">&nbsp;No</label></div>
					
					<small>Please indicate whether you are already enrolled in a course at the University of Sydney.</small>
				</div>
			</div>
			<div class="sv-form-group" id="section6" style="display: none;">
				<label class="sv-col-md-3 sv-control-label">Have you ever been enrolled at the University of Sydney? *</label>
				<div class="sv-col-md-4">
					
					<div class="sv-radio"><label><input name="IPQ_APONLCES3" id="IPQ_APONLCES3A" type="radio" value="Y" onclick="check_IPQ_APONLCES3();">&nbsp;Yes</label></div>
					
					
					<div class="sv-radio"><label><input name="IPQ_APONLCES3" id="IPQ_APONLCES3B" type="radio" value="N" onclick="check_IPQ_APONLCES3();">&nbsp;No</label></div>
					
				</div>
			</div>
			<div class="sv-form-group" id="section5" style="display: none;">
				<label for="IPQ_APONLCES2" class="sv-col-md-3 sv-control-label">What is your University of Sydney student ID or Unikey? *</label>
				<div class="sv-col-md-4">
					<input name="IPQ_APONLCES2" id="IPQ_APONLCES2" class="sv-form-control" type="text" maxlength="9" value="">
				</div>
			</div>
		</div>
	</div>
</div>
'''

class PersonalInfoEnrollment:
    def __init__(self, driver, data):
        self.driver = driver
        self.data = data

    def run(self):
        students = self.data
        driver = self.driver
        personal_info = students[-1][0]
        
        # Check if the student is currently enrolled at Sydney
        is_current_student = personal_info.get('is_current_student', False)
        
        if is_current_student:
            # Select "Yes" for current student
            check_button_by_id(driver, "IPQ_APONLCES1A")
            
            # Wait for the student ID field to appear
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "IPQ_APONLCES2"))
            )
            
            # Fill in student ID if available
            student_id = personal_info.get('student_id', '')
            if not student_id:
                student_id = personal_info.get('unikey', '')
                
            if not student_id:
                student_id = "123456789"  # Default placeholder
                
            set_value_by_id(driver, "IPQ_APONLCES2", student_id)
        else:
            # Select "No" for current student
            check_button_by_id(driver, "IPQ_APONLCES1B")
            
            # Wait for the "Have you ever been enrolled" question to appear
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "section6"))
            )
            
            # Check if the student was previously enrolled
            was_previously_enrolled = personal_info.get('was_previously_enrolled', False)
            
            if was_previously_enrolled:
                # Select "Yes" for previously enrolled
                check_button_by_id(driver, "IPQ_APONLCES3A")
                
                # Wait for the student ID field to appear
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "IPQ_APONLCES2"))
                )
                
                # Fill in previous student ID if available
                previous_student_id = personal_info.get('previous_student_id', '')
                if not previous_student_id:
                    previous_student_id = personal_info.get('unikey', '')
                    
                if not previous_student_id:
                    previous_student_id = "987654321"  # Default placeholder
                    
                set_value_by_id(driver, "IPQ_APONLCES2", previous_student_id)
            else:
                # Select "No" for previously enrolled
                check_button_by_id(driver, "IPQ_APONLCES3B")

